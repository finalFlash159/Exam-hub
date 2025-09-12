from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, JSON, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel


class FileStatus(str, enum.Enum):
    """Enum for file upload status"""
    UPLOADING = "uploading"
    COMPLETED = "completed"
    PROCESSING = "processing"
    FAILED = "failed"
    DELETED = "deleted"


class StorageType(str, enum.Enum):
    """Enum for storage backend type"""
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"

class ProcessingStatus(str, enum.Enum):
    """Enum for document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UploadedFile(BaseModel):
    """
    Uploaded File model
    Tracks file metadata and storage information
    """
    __tablename__ = "uploaded_files"
    
    # Basic file info
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # File metadata
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)  # SHA-256
    
    # Ownership & permissions
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Storage info
    storage_type: Mapped[StorageType] = mapped_column(
        SQLEnum(StorageType), 
        default=StorageType.LOCAL,
        nullable=False
    )
    storage_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Provider-specific info
    
    # Status tracking
    upload_status: Mapped[FileStatus] = mapped_column(
        SQLEnum(FileStatus),
        default=FileStatus.COMPLETED,
        nullable=False
    )
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Processing info (for AI generation, etc.)
    processing_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    extracted_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SQLEnum(ProcessingStatus),
        default=ProcessingStatus.PENDING,
        nullable=False
    )
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="uploaded_files")
    
    def __repr__(self) -> str:
        return f"<UploadedFile(id={self.id}, filename='{self.original_filename}', owner={self.owner_id})>"
    
    @property
    def is_image(self) -> bool:
        """Check if file is an image"""
        if not self.content_type:
            return False
        return self.content_type.startswith('image/')
    
    @property
    def is_pdf(self) -> bool:
        """Check if file is a PDF"""
        return self.content_type == 'application/pdf'
    
    @property
    def size_mb(self) -> float:
        """Get file size in MB"""
        return round(self.size / (1024 * 1024), 2)
        