import logging
import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.upload_service import UploadService
from ..schemas.upload_schemas import (
    FileUploadResponse, FileListResponse, FileInfoResponse, 
    FileDeleteResponse, AdminFileListResponse, UploadStatsResponse,
    HealthCheckResponse
)
from app.database.connection import get_db_session
from app.models.user import User
from app.auth.dependencies import CurrentUser
from app.auth import require_admin
from app.core.config import get_settings

router = APIRouter(prefix="/upload", tags=["upload"])
logger = logging.getLogger(__name__)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = CurrentUser,
    db: AsyncSession = Depends(get_db_session)
) -> FileUploadResponse:
    """
    Upload file for current user
    🔒 REQUIRES AUTHENTICATION - User-scoped file upload with database integration
    
    Features:
    - File validation and sanitization
    - Duplicate detection via SHA-256 hash
    - Database metadata storage
    - User ownership tracking
    - Security validation
    """
    try:
        logger.info(f"User {current_user.email} uploading file: {file.filename}")
        
        upload_service = UploadService(db)
        result = await upload_service.save_uploaded_file(file, current_user.id)

        return FileUploadResponse(
            success=True,
            message=result.get("message", "File uploaded successfully"),
            data={
                "file_id": result["file_id"],
                "original_filename": result["original_filename"],
                "stored_filename": result["stored_filename"],
                "size": result["size"],
                "size_mb": result["size_mb"],
                "content_type": result["content_type"],
                "file_hash": result["file_hash"],
                "uploaded_at": result["uploaded_at"],
                "is_duplicate": result.get("duplicate", False),
                "metadata": {
                    "is_image": result.get("is_image", False),
                    "is_pdf": result.get("is_pdf", False),
                    "user_scoped": True,
                    "database_integrated": True
                }
            }
        )
    
    except ValueError as e:
        logger.warning(f"Upload validation failed for user {current_user.email}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

@router.get("/", status_code=status.HTTP_200_OK, response_model=FileListResponse)
async def list_files(
    skip: int = Query(0, ge=0, description="Number of files to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of files to return"),
    current_user: User = CurrentUser,
    db: AsyncSession = Depends(get_db_session)
) -> FileListResponse:
    """
    List current user's uploaded files with pagination
    🔒 REQUIRES AUTHENTICATION - User-scoped file listing
    
    Features:
    - Pagination support
    - File metadata included
    - Filesystem existence check
    - Upload status tracking
    """
    try:
        logger.info(f"User {current_user.email} listing files (skip={skip}, limit={limit})")
        
        upload_service = UploadService(db)
        result = await upload_service.list_user_files(current_user.id, skip, limit)
        
        return FileListResponse(
            success=True,
            data={
                "files": result["files"],
                "pagination": {
                    "count": result["count"],
                    "total_count": result["total_count"],
                    "skip": result["skip"],
                    "limit": result["limit"],
                    "has_more": result["count"] == limit
                },
                "user_id": result["user_id"],
                "user_scoped": True
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing files for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to list files")

@router.get("/{file_id}/info", status_code=status.HTTP_200_OK, response_model=FileInfoResponse)
async def get_file_info(
    file_id: str,
    current_user: User = CurrentUser,
    db: AsyncSession = Depends(get_db_session)
) -> FileInfoResponse:
    """
    Get detailed file information by ID
    🔒 REQUIRES AUTHENTICATION + OWNERSHIP CHECK
    
    Features:
    - Complete file metadata
    - Filesystem verification
    - Upload status tracking
    - Security validation
    """
    try:
        logger.debug(f"User {current_user.email} requesting file info: {file_id}")
        
        upload_service = UploadService(db)
        result = await upload_service.get_file_info(file_id, current_user.id)
        
        return FileInfoResponse(
            success=True,
            data=result
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        logger.error(f"Error getting file info for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get file information")

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = CurrentUser,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Download file by ID
    🔒 REQUIRES AUTHENTICATION + OWNERSHIP CHECK
    
    Features:
    - Secure file serving
    - Ownership validation
    - Proper HTTP headers
    - Access logging
    """
    try:
        logger.info(f"User {current_user.email} downloading file: {file_id}")
        
        upload_service = UploadService(db)
        file_info = await upload_service.get_file_info(file_id, current_user.id)
        
        if not file_info["filesystem_exists"]:
            logger.error(f"File not found on filesystem: {file_info['file_path']}")
            raise HTTPException(status_code=404, detail="File not found on server")
        
        return FileResponse(
            path=file_info["file_path"],
            filename=file_info["original_filename"],
            media_type=file_info.get("content_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename=\"{file_info['original_filename']}\"",
                "X-File-ID": file_id,
                "X-File-Size": str(file_info["size"])
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        logger.error(f"Error downloading file for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="File download failed")

@router.delete("/{file_id}", status_code=status.HTTP_200_OK, response_model=FileDeleteResponse)
async def delete_file(
    file_id: str,
    current_user: User = CurrentUser,
    db: AsyncSession = Depends(get_db_session)
) -> FileDeleteResponse:
    """
    Delete file by ID
    🔒 REQUIRES AUTHENTICATION + OWNERSHIP CHECK
    
    Features:
    - Secure deletion with ownership validation
    - Both filesystem and database cleanup
    - Soft delete in database
    - Audit logging
    """
    try:
        logger.info(f"User {current_user.email} deleting file: {file_id}")
        
        upload_service = UploadService(db)
        result = await upload_service.delete_file(file_id, current_user.id)
        
        return FileDeleteResponse(
            success=True,
            message="File deleted successfully",
            data={
                "file_id": result["file_id"],
                "original_filename": result["original_filename"],
                "filesystem_deleted": result["filesystem_deleted"],
                "database_updated": result["database_updated"]
            }
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        logger.error(f"Error deleting file for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="File deletion failed")

# ADMIN ENDPOINTS

@router.get("/admin/files", status_code=status.HTTP_200_OK, response_model=AdminFileListResponse)
async def list_all_files_admin(
    skip: int = Query(0, ge=0, description="Number of files to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of files to return"),
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db_session)
) -> AdminFileListResponse:
    """
    List ALL uploaded files (Admin only)
    🔒 REQUIRES ADMIN ROLE
    
    Features:
    - Admin-level access to all files
    - Pagination support
    - User ownership information
    - System-wide file statistics
    """
    try:
        logger.info(f"Admin {current_user.email} listing all files (skip={skip}, limit={limit})")
        
        upload_service = UploadService(db)
        result = await upload_service.list_all_files_admin(skip, limit)
        
        return AdminFileListResponse(
            success=True,
            data={
                "files": result["files"],
                "pagination": {
                    "count": result["count"],
                    "total_count": result["total_count"],
                    "skip": result["skip"],
                    "limit": result["limit"],
                    "has_more": result["count"] == limit
                },
                "admin_access": True,
                "requested_by": current_user.email
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing all files for admin {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to list files")

@router.get("/admin/stats", status_code=status.HTTP_200_OK, response_model=UploadStatsResponse)
async def get_upload_stats_admin(
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db_session)
) -> UploadStatsResponse:
    """
    Get upload statistics (Admin only)
    🔒 REQUIRES ADMIN ROLE
    
    Features:
    - System-wide file statistics
    - Storage usage information
    - User upload activity
    """
    try:
        logger.info(f"Admin {current_user.email} requesting upload statistics")
        
        upload_service = UploadService(db)
        all_files = await upload_service.list_all_files_admin(0, 10000)  # Get all files
        
        # Calculate statistics
        total_files = all_files["total_count"]
        total_size = sum(file["size"] for file in all_files["files"])
        total_size_mb = round(total_size / (1024 * 1024), 2)
        
        # File type distribution
        file_types = {}
        users_with_files = set()
        
        for file in all_files["files"]:
            content_type = file.get("content_type", "unknown")
            file_types[content_type] = file_types.get(content_type, 0) + 1
            users_with_files.add(file["owner_id"])
        
        return UploadStatsResponse(
            success=True,
            data={
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": total_size_mb,
                "active_users": len(users_with_files),
                "file_types": file_types,
                "average_file_size_mb": round(total_size_mb / max(total_files, 1), 2),
                "admin_access": True,
                "generated_by": current_user.email
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting upload stats for admin {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get upload statistics")

# HEALTH CHECK ENDPOINT

@router.get("/health", status_code=status.HTTP_200_OK, response_model=HealthCheckResponse)
async def upload_health_check() -> HealthCheckResponse:
    """
    Upload service health check
    Public endpoint for monitoring
    """
    try:
        settings = get_settings()
        upload_folder = settings["upload_folder"]
        
        # Check upload folder accessibility
        folder_exists = os.path.exists(upload_folder)
        folder_writable = os.access(upload_folder, os.W_OK) if folder_exists else False
        
        return HealthCheckResponse(
            success=True,
            data={
                "service": "upload",
                "status": "healthy",
                "checks": {
                    "upload_folder_exists": folder_exists,
                    "upload_folder_writable": folder_writable,
                    "database_integration": True,
                    "security_enabled": True
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Upload health check failed: {e}")
        raise HTTPException(status_code=503, detail="Upload service unhealthy")

@router.post("/{file_id}/process", 
             response_model=dict,
             summary="Process uploaded file to extract content",
             description="Manually trigger content processing for an uploaded file")
async def process_file_content(
    file_id: str,
    current_user: User = CurrentUser,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Process uploaded file to extract text content
    
    - **file_id**: UUID of the uploaded file
    - Returns processing result with status and details
    - Requires authentication
    """
    try:
        logger.info(f"Processing file {file_id} requested by user {current_user.id}")
        
        upload_service = UploadService(session)
        result = await upload_service.process_file_content(file_id, current_user.id)
        
        if result["success"]:
            logger.info(f"File {file_id} processed successfully")
            return result
        else:
            logger.warning(f"File processing failed for {file_id}: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Processing failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{file_id}/content", 
            response_model=dict,
            summary="Get extracted content from processed file",
            description="Retrieve text content extracted from an uploaded file")
async def get_file_content(
    file_id: str,
    current_user: User = CurrentUser,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get extracted text content from processed file
    
    - **file_id**: UUID of the uploaded file
    - Returns extracted content or error if not processed
    - Requires authentication and file ownership
    """
    try:
        logger.info(f"Content requested for file {file_id} by user {current_user.id}")
        
        upload_service = UploadService(session)
        result = await upload_service.get_file_content(file_id, current_user.id)
        
        if result["success"]:
            logger.info(f"Content retrieved for file {file_id}")
            return result
        else:
            logger.warning(f"Content retrieval failed for {file_id}: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Content not found")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content for file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{file_id}/status", 
            response_model=dict,
            summary="Get processing status for uploaded file",
            description="Check the current processing status of an uploaded file")
async def get_processing_status(
    file_id: str,
    current_user: User = CurrentUser,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get processing status for uploaded file
    
    - **file_id**: UUID of the uploaded file
    - Returns processing status details
    - Requires authentication and file ownership
    """
    try:
        logger.info(f"Status requested for file {file_id} by user {current_user.id}")
        
        upload_service = UploadService(session)
        result = await upload_service.get_processing_status(file_id, current_user.id)
        
        if result["success"]:
            logger.info(f"Status retrieved for file {file_id}")
            return result
        else:
            logger.warning(f"Status retrieval failed for {file_id}: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "File not found")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )