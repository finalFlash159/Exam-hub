from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from datetime import datetime

from .base import BaseModel

class UserRole(str, enum.Enum):
    """User roles"""
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    """User model for authentication"""
    __tablename__ = "users"

    # User info
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False
    )

    # Relationships
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    
    # File relationship
    uploaded_files: Mapped[List["UploadedFile"]] = relationship(
        "UploadedFile",
        back_populates="owner",
        cascade="all, delete-orphan",
        order_by="UploadedFile.created_at.desc()"
    )
    
    # Exam relationship 
    created_exams: Mapped[List["Exam"]] = relationship(
        "Exam",
        foreign_keys="Exam.creator_id",
        back_populates="creator",
        cascade="all, delete-orphan",
        order_by="Exam.created_at.desc()"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role={self.role})>"
    
    @property
    def file_count(self) -> int:
        """Get number of uploaded files"""
        return len([f for f in self.uploaded_files if f.upload_status != "deleted"])
    
    @property
    def total_file_size(self) -> int:
        """Get total size of uploaded files in bytes"""
        return sum(f.size for f in self.uploaded_files if f.upload_status != "deleted")