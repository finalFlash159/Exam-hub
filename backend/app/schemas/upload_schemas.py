"""
Upload API Response Schemas
Pydantic models for structured API responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Base Response Schema
class BaseResponse(BaseModel):
    """Base response schema with success indicator"""
    success: bool = Field(..., description="Request success status")
    message: Optional[str] = Field(None, description="Response message")


# File Metadata Schema
class FileMetadata(BaseModel):
    """File metadata information"""
    is_image: bool = Field(..., description="Whether file is an image")
    is_pdf: bool = Field(..., description="Whether file is a PDF")
    user_scoped: bool = Field(True, description="File is user-scoped")
    database_integrated: bool = Field(True, description="Database integration enabled")


# File Data Schema
class FileData(BaseModel):
    """File data information"""
    file_id: str = Field(..., description="Unique file identifier")
    original_filename: str = Field(..., description="Original filename from user")
    stored_filename: str = Field(..., description="Stored filename on server")
    size: int = Field(..., description="File size in bytes")
    size_mb: float = Field(..., description="File size in MB")
    content_type: str = Field(..., description="File MIME type")
    file_hash: str = Field(..., description="SHA-256 hash of file content")
    uploaded_at: str = Field(..., description="Upload timestamp (ISO format)")
    is_duplicate: bool = Field(False, description="Whether file is a duplicate")
    metadata: FileMetadata = Field(..., description="File metadata")


# File Upload Response
class FileUploadResponse(BaseResponse):
    """Response for file upload endpoint"""
    data: FileData = Field(..., description="Uploaded file data")


# File List Item Schema
class FileListItem(BaseModel):
    """Individual file in list response"""
    file_id: str = Field(..., description="Unique file identifier")
    stored_filename: str = Field(..., description="Stored filename on server")
    original_filename: str = Field(..., description="Original filename from user")
    size: int = Field(..., description="File size in bytes")
    size_mb: float = Field(..., description="File size in MB")
    content_type: str = Field(..., description="File MIME type")
    upload_status: str = Field(..., description="Upload status")
    is_public: bool = Field(..., description="Whether file is public")
    is_image: bool = Field(..., description="Whether file is an image")
    is_pdf: bool = Field(..., description="Whether file is a PDF")
    uploaded_at: str = Field(..., description="Upload timestamp (ISO format)")
    filesystem_exists: bool = Field(..., description="Whether file exists on filesystem")
    user_owned: bool = Field(True, description="Whether file is owned by user")


# Pagination Schema
class PaginationInfo(BaseModel):
    """Pagination information"""
    count: int = Field(..., description="Number of items in current page")
    total_count: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
    has_more: bool = Field(..., description="Whether more items are available")


# File List Data Schema
class FileListData(BaseModel):
    """File list response data"""
    files: List[FileListItem] = Field(..., description="List of files")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    user_id: str = Field(..., description="User ID")
    user_scoped: bool = Field(True, description="Response is user-scoped")


# File List Response
class FileListResponse(BaseResponse):
    """Response for file list endpoint"""
    data: FileListData = Field(..., description="File list data")


# File Info Schema
class FileInfo(BaseModel):
    """Detailed file information"""
    file_id: str = Field(..., description="Unique file identifier")
    stored_filename: str = Field(..., description="Stored filename on server")
    original_filename: str = Field(..., description="Original filename from user")
    size: int = Field(..., description="File size in bytes")
    size_mb: float = Field(..., description="File size in MB")
    content_type: str = Field(..., description="File MIME type")
    file_hash: str = Field(..., description="SHA-256 hash of file content")
    upload_status: str = Field(..., description="Upload status")
    is_public: bool = Field(..., description="Whether file is public")
    is_image: bool = Field(..., description="Whether file is an image")
    is_pdf: bool = Field(..., description="Whether file is a PDF")
    uploaded_at: str = Field(..., description="Upload timestamp (ISO format)")
    updated_at: str = Field(..., description="Last update timestamp (ISO format)")
    owner_id: str = Field(..., description="File owner ID")
    filesystem_exists: bool = Field(..., description="Whether file exists on filesystem")
    database_integrated: bool = Field(True, description="Database integration enabled")
    access_validated: bool = Field(True, description="Access validation performed")


# File Info Response
class FileInfoResponse(BaseResponse):
    """Response for file info endpoint"""
    data: FileInfo = Field(..., description="File information")


# File Delete Data Schema
class FileDeleteData(BaseModel):
    """File deletion response data"""
    file_id: str = Field(..., description="Deleted file ID")
    original_filename: str = Field(..., description="Original filename")
    filesystem_deleted: bool = Field(..., description="Whether file was deleted from filesystem")
    database_updated: bool = Field(..., description="Whether database was updated")


# File Delete Response
class FileDeleteResponse(BaseResponse):
    """Response for file delete endpoint"""
    data: FileDeleteData = Field(..., description="Deletion result data")


# Admin File List Item Schema
class AdminFileListItem(FileListItem):
    """File item in admin list (includes owner info)"""
    owner_id: str = Field(..., description="File owner ID")
    admin_visible: bool = Field(True, description="Visible to admin")


# Admin File List Data Schema
class AdminFileListData(BaseModel):
    """Admin file list response data"""
    files: List[AdminFileListItem] = Field(..., description="List of all files")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    admin_access: bool = Field(True, description="Admin access granted")
    requested_by: str = Field(..., description="Admin user email")


# Admin File List Response
class AdminFileListResponse(BaseResponse):
    """Response for admin file list endpoint"""
    data: AdminFileListData = Field(..., description="Admin file list data")


# Upload Statistics Schema
class UploadStats(BaseModel):
    """Upload system statistics"""
    total_files: int = Field(..., description="Total number of files")
    total_size_bytes: int = Field(..., description="Total size in bytes")
    total_size_mb: float = Field(..., description="Total size in MB")
    active_users: int = Field(..., description="Number of users with files")
    file_types: Dict[str, int] = Field(..., description="File type distribution")
    average_file_size_mb: float = Field(..., description="Average file size in MB")
    admin_access: bool = Field(True, description="Admin access granted")
    generated_by: str = Field(..., description="Admin user email")


# Upload Stats Response
class UploadStatsResponse(BaseResponse):
    """Response for upload statistics endpoint"""
    data: UploadStats = Field(..., description="Upload statistics")


# Health Check Schema
class HealthCheckData(BaseModel):
    """Health check response data"""
    service: str = Field("upload", description="Service name")
    status: str = Field("healthy", description="Service status")
    checks: Dict[str, bool] = Field(..., description="Health check results")


# Health Check Response
class HealthCheckResponse(BaseResponse):
    """Response for health check endpoint"""
    data: HealthCheckData = Field(..., description="Health check data")


# Error Response Schema
class ErrorResponse(BaseResponse):
    """Error response schema"""
    success: bool = Field(False, description="Request failed")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Error details (debug mode only)")
    error_code: Optional[str] = Field(None, description="Error code")
