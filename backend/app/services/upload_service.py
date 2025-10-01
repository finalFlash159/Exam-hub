import os
import uuid
import logging
import hashlib
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.repositories.file_repository import FileRepository
from app.models.file import UploadedFile, FileStatus
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)


class UploadService:
    """Service for handling file upload business logic with database integration"""
    
    def __init__(self, db: AsyncSession):
        """Initialize upload service with database session"""
        self.db = db
        self.file_repo = FileRepository(db)
        self.document_service = DocumentService(db)
        logger.info("UploadService initialized with database session")
    
    def is_allowed_file(self, filename: str, allowed_extensions: set) -> bool:
        """
        Check if file extension is allowed
        
        Args:
            filename: Name of the file
            allowed_extensions: Set of allowed extensions
            
        Returns:
            True if file extension is allowed
        """
        if not filename or '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in allowed_extensions
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and special character issues
        
        Args:
            filename: Original filename from user
            
        Returns:
            Sanitized filename safe for filesystem
        """
        if not filename:
            return "unnamed_file"
        
        # Extract extension first
        name, ext = os.path.splitext(filename)

        # Remove dangerous characters, keep only alphanumeric, hyphens, underscores (NO DOTS)
        # This prevents path traversal attacks with sequences like ../
        safe_name = re.sub(r'[^\w\-]', '_', name)

        # Only allow alphanumeric characters in extension, ensure single dot prefix
        safe_ext = ''
        if ext:
            # Remove leading dots and sanitize extension
            ext_clean = ext.lstrip('.')
            safe_ext = '.' + re.sub(r'[^\w]', '', ext_clean)

        # Remove leading/trailing underscores
        safe_name = safe_name.strip('_')
        
        # Ensure name is not empty
        if not safe_name:
            safe_name = "file"
        
        # Limit length (filesystem limits)
        max_name_length = 100
        if len(safe_name) > max_name_length:
            safe_name = safe_name[:max_name_length]
        
        # Combine name and extension
        sanitized = safe_name + safe_ext
        
        logger.debug(f"Sanitized filename: '{filename}' -> '{sanitized}'")
        return sanitized
    
    def calculate_file_hash(self, content: bytes) -> str:
        """
        Calculate SHA-256 hash of file content with memory optimization
        
        Args:
            content: File content as bytes
            
        Returns:
            SHA-256 hash as hex string
        """
        # For large files (>50MB), use streaming hash to save memory
        large_file_threshold = 50 * 1024 * 1024  # 50MB
        
        if len(content) > large_file_threshold:
            logger.debug("Using streaming hash for large file")
            hasher = hashlib.sha256()
            chunk_size = 8192  # 8KB chunks
            
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                hasher.update(chunk)
            
            return hasher.hexdigest()
        else:
            return hashlib.sha256(content).hexdigest()
    
    async def check_duplicate_file(self, file_hash: str, user_id: str) -> Optional[UploadedFile]:
        """
        Check if file with same hash already exists for user
        
        Args:
            file_hash: SHA-256 hash of file content
            user_id: ID of current user
            
        Returns:
            Existing file record if duplicate found
        """
        try:
            # Check for duplicate file (same hash, same user)
            existing_file = await self.file_repo.get_by_hash(file_hash)
            
            if existing_file and existing_file.owner_id == user_id:
                logger.info(f"Duplicate file detected for user {user_id}: {existing_file.original_filename}")
                return existing_file
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking duplicate file: {e}")
            return None
    
    def validate_file_content_type(self, file: UploadFile, content: bytes) -> str:
        """
        Validate and determine actual file content type
        
        Args:
            file: FastAPI UploadFile object
            content: File content bytes
            
        Returns:
            Validated content type
        """
        declared_type = file.content_type or "application/octet-stream"
        
        # Basic magic number detection for common types
        if content.startswith(b'\x89PNG'):
            actual_type = "image/png"
        elif content.startswith(b'\xff\xd8\xff'):
            actual_type = "image/jpeg"
        elif content.startswith(b'%PDF'):
            actual_type = "application/pdf"
        elif content.startswith(b'GIF8'):
            actual_type = "image/gif"
        else:
            actual_type = declared_type
        
        # Log discrepancy for security monitoring
        if declared_type != actual_type:
            logger.warning(f"Content type mismatch: declared={declared_type}, actual={actual_type}")
        
        return actual_type
    
    async def save_uploaded_file(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """
        Save uploaded file with validation, processing, and database integration
        Enhanced with security fixes and performance optimizations
        
        Args:
            file: FastAPI UploadFile object
            user_id: ID of user uploading the file
            
        Returns:
            Dict containing file info and metadata
            
        Raises:
            ValueError: For validation errors
            Exception: For file operation errors
        """
        logger.info(f"Processing upload request for user {user_id} - filename: {file.filename}")
        
        # Get settings
        settings = get_settings()
        
        # Validate filename
        if not file.filename:
            logger.warning("No filename provided")
            raise ValueError("No selected file")
        
        # Sanitize filename for security
        safe_filename = self.sanitize_filename(file.filename)
        
        # Validate file extension
        if not self.is_allowed_file(safe_filename, settings["allowed_extensions"]):
            logger.warning(f"File type not allowed: {safe_filename}")
            raise ValueError("File type not allowed")
        
        # Read and validate file content
        logger.debug("Reading file content...")
        try:
            content = await file.read()
        except Exception as e:
            logger.error(f"Failed to read file content: {e}")
            raise ValueError("Failed to read file content")
        
        file_size = len(content)
        logger.info(f"File size: {file_size} bytes ({round(file_size / 1024 / 1024, 2)} MB)")
        
        # Validate file size
        if file_size > settings["max_upload_size"]:
            logger.warning(f"File too large: {file_size} > {settings['max_upload_size']}")
            raise ValueError(f"File too large. Maximum size: {settings['max_upload_size']} bytes")
        
        if file_size == 0:
            logger.warning("Empty file received")
            raise ValueError("Empty file not allowed")
        
        # Validate content type
        validated_content_type = self.validate_file_content_type(file, content)
        
        # Calculate file hash for duplicate detection
        logger.debug("Calculating file hash...")
        try:
            file_hash = self.calculate_file_hash(content)
            logger.debug(f"File hash: {file_hash}")
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {e}")
            raise ValueError("File processing failed")
        
        # Check for duplicate files
        duplicate_file = await self.check_duplicate_file(file_hash, user_id)
        if duplicate_file:
            logger.info(f"Returning existing file instead of duplicate: {duplicate_file.stored_filename}")
            return {
                'message': 'File already exists (duplicate detected)',
                'file_id': duplicate_file.id,
                'stored_filename': duplicate_file.stored_filename,
                'original_filename': duplicate_file.original_filename,
                'size': duplicate_file.size,
                'size_mb': duplicate_file.size_mb,
                'content_type': duplicate_file.content_type,
                'user_id': user_id,
                'uploaded_at': duplicate_file.created_at.isoformat(),
                'duplicate': True,
                'existing_file': True
            }
        
        # Prepare upload directory
        upload_folder = settings["upload_folder"]
        try:
            os.makedirs(upload_folder, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create upload directory: {e}")
            raise Exception("Upload directory setup failed")
        
        # Generate unique filename
        file_extension = os.path.splitext(safe_filename)[1]
        file_uuid = uuid.uuid4().hex
        stored_filename = f"{user_id[:8]}_{file_uuid}_{safe_filename}"
        file_path = os.path.join(upload_folder, stored_filename)
        
        logger.debug(f"Generated stored filename: {stored_filename}")
        logger.debug(f"Full save path: {file_path}")
        
        # Start database transaction
        try:
            # Create database record first (with UPLOADING status)
            file_record = await self.file_repo.create_file_record(
                original_filename=file.filename,  # Keep original for reference
                stored_filename=stored_filename,
                file_path=file_path,
                size=file_size,
                content_type=validated_content_type,
                owner_id=user_id,
                file_hash=file_hash,
                upload_status=FileStatus.UPLOADING  # Start with UPLOADING status
            )
            logger.info(f"Created database record for file: {file_record.id}")
            
            # Save file to filesystem
            try:
                with open(file_path, 'wb') as f:
                    f.write(content)
                logger.info(f"File saved to filesystem: {file_path}")
                
            except Exception as e:
                logger.error(f"Error saving file to filesystem: {e}")
                # Cleanup database record on filesystem error
                try:
                    await self.file_repo.delete_file_record(file_record.id, user_id)
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup database record: {cleanup_error}")
                raise Exception(f"File save failed: {type(e).__name__}") from e
            
            # Verify file was saved correctly
            if not os.path.exists(file_path):
                logger.error("File was not saved successfully")
                await self.file_repo.update_status(file_record.id, FileStatus.FAILED, "File save verification failed")
                raise Exception("File save verification failed")
            
            saved_size = os.path.getsize(file_path)
            if saved_size != file_size:
                logger.error(f"File size mismatch: expected {file_size}, got {saved_size}")
                # Clean up incorrect file
                try:
                    os.remove(file_path)
                    await self.file_repo.update_status(file_record.id, FileStatus.FAILED, "File size mismatch")
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup corrupted file: {cleanup_error}")
                raise Exception("File save verification failed")
            
            # Update database record to COMPLETED
            try:
                await self.file_repo.update_status(file_record.id, FileStatus.COMPLETED)
                logger.info(f"File upload completed successfully: {file_record.id}")
                
            except Exception as e:
                logger.error(f"Failed to update file status to completed: {e}")
                # File is saved but status update failed - log but don't fail the upload
                logger.warning("File saved successfully but status update failed")
            
            # Prepare response
            result = {
                'message': 'File uploaded successfully',
                'file_id': file_record.id,
                'stored_filename': stored_filename,
                'original_filename': file.filename,
                'sanitized_filename': safe_filename,
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'content_type': validated_content_type,
                'user_id': user_id,
                'uploaded_at': file_record.created_at.isoformat(),
                'file_hash': file_hash,
                'is_image': file_record.is_image,
                'is_pdf': file_record.is_pdf,
                'metadata': {
                    'upload_folder': upload_folder,
                    'extension': file_extension,
                    'validation_passed': True,
                    'user_scoped': True,
                    'database_integrated': True,
                    'security_enhanced': True
                }
            }
            
            logger.info(f"Upload completed successfully for user {user_id}: {file_record.id}")
            return result
            
        except ValueError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            logger.error(f"Upload failed for user {user_id}: {e}")
            # Generic error message for security
            raise Exception("File upload failed")
    
    async def delete_file(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete uploaded file (with ownership validation and database cleanup)
        
        Args:
            file_id: ID of file to delete (database ID, not filename)
            user_id: ID of user requesting deletion
            
        Returns:
            Dict with deletion result
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If user doesn't own the file
            Exception: For deletion errors
        """
        logger.info(f"Delete file request from user {user_id}: {file_id}")
        
        # Get file record from database
        try:
            file_record = await self.file_repo.get_by_id(file_id)
            if not file_record:
                raise FileNotFoundError("File not found")
            
            # Check ownership
            if file_record.owner_id != user_id:
                logger.warning(f"Unauthorized delete attempt: user {user_id} tried to delete file {file_id} owned by {file_record.owner_id}")
                raise PermissionError("Access denied")
            
            logger.info(f"Deleting file: {file_record.stored_filename}")
            
        except (FileNotFoundError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"Error getting file record for deletion: {e}")
            raise Exception("File deletion failed")
        
        # Delete from filesystem
        filesystem_deleted = False
        if os.path.exists(file_record.file_path):
            try:
                os.remove(file_record.file_path)
                filesystem_deleted = True
                logger.info(f"File deleted from filesystem: {file_record.file_path}")
            except Exception as e:
                logger.error(f"Error deleting file from filesystem: {e}")
                # Continue with database cleanup even if filesystem deletion fails
        else:
            logger.warning(f"File not found in filesystem: {file_record.file_path}")
        
        # Update database record (soft delete)
        try:
            success = await self.file_repo.delete_file_record(file_id, user_id)
            if not success:
                raise Exception("Database deletion failed")
            
            logger.info(f"File record marked as deleted: {file_id}")
            
        except Exception as e:
            logger.error(f"Error updating database record for deletion: {e}")
            raise Exception("File deletion failed")
        
        return {
            'message': 'File deleted successfully',
            'file_id': file_id,
            'stored_filename': file_record.stored_filename,
            'original_filename': file_record.original_filename,
            'deleted': True,
            'filesystem_deleted': filesystem_deleted,
            'database_updated': True
        }
    
    async def get_file_info(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get information about uploaded file (with ownership validation)
        
        Args:
            file_id: ID of file to get info for (database ID)
            user_id: ID of user requesting file info
            
        Returns:
            Dict with file information
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If user doesn't own the file
        """
        logger.debug(f"Get file info request from user {user_id}: {file_id}")
        
        # Get file record from database
        try:
            file_record = await self.file_repo.get_by_id(file_id)
            if not file_record:
                raise FileNotFoundError("File not found")
            
            # Check ownership
            if file_record.owner_id != user_id:
                logger.warning(f"Unauthorized access attempt: user {user_id} tried to access file {file_id} owned by {file_record.owner_id}")
                raise PermissionError("Access denied")
            
        except (FileNotFoundError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"Error getting file record: {e}")
            raise Exception("Failed to get file information")
        
        # Check filesystem existence
        file_exists = os.path.exists(file_record.file_path)
        if not file_exists:
            logger.warning(f"File missing from filesystem: {file_record.file_path}")
        
        return {
            'file_id': file_record.id,
            'stored_filename': file_record.stored_filename,
            'original_filename': file_record.original_filename,
            'size': file_record.size,
            'size_mb': file_record.size_mb,
            'content_type': file_record.content_type,
            'file_hash': file_record.file_hash,
            'upload_status': file_record.upload_status.value,
            'is_public': file_record.is_public,
            'is_image': file_record.is_image,
            'is_pdf': file_record.is_pdf,
            'uploaded_at': file_record.created_at.isoformat(),
            'updated_at': file_record.updated_at.isoformat(),
            'owner_id': file_record.owner_id,
            'filesystem_exists': file_exists,
            'database_integrated': True,
            'access_validated': True
        }
    
    async def list_user_files(self, user_id: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        List files owned by specific user (database-driven)
        
        Args:
            user_id: ID of user to list files for
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            Dict with user's files and metadata
        """
        logger.info(f"Listing files for user: {user_id} (skip={skip}, limit={limit})")
        
        try:
            # Get files from database
            files = await self.file_repo.get_user_files(
                owner_id=user_id,
                skip=skip,
                limit=limit,
                status_filter=None  # Include all statuses except deleted (handled in repo)
            )
            
            # Get total count
            total_count = await self.file_repo.count_user_files(user_id)
            
            # Format file information
            file_list = []
            for file_record in files:
                if file_record.upload_status != FileStatus.DELETED:  # Extra safety check
                    file_exists = os.path.exists(file_record.file_path)
                    file_list.append({
                        "file_id": file_record.id,
                        "stored_filename": file_record.stored_filename,
                        "original_filename": file_record.original_filename,
                        "size": file_record.size,
                        "size_mb": file_record.size_mb,
                        "content_type": file_record.content_type,
                        "upload_status": file_record.upload_status.value,
                        "is_public": file_record.is_public,
                        "is_image": file_record.is_image,
                        "is_pdf": file_record.is_pdf,
                        "uploaded_at": file_record.created_at.isoformat(),
                        "filesystem_exists": file_exists,
                        "user_owned": True
                    })
            
            logger.info(f"Found {len(file_list)} files for user {user_id}")
            return {
                "files": file_list,
                "count": len(file_list),
                "total_count": total_count,
                "skip": skip,
                "limit": limit,
                "user_id": user_id,
                "user_scoped": True,
                "database_integrated": True
            }
            
        except Exception as e:
            logger.error(f"Error listing files for user {user_id}: {e}")
            raise Exception("Failed to list user files")
    
    async def list_all_files_admin(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        List ALL files (Admin only) - database-driven
        
        Args:
            skip: Number of records to skip  
            limit: Maximum number of records
            
        Returns:
            Dict with all files and metadata
        """
        logger.info(f"Admin listing all files (skip={skip}, limit={limit})")
        
        try:
            # Get all files from database (admin access)
            from sqlalchemy import select, func
            
            result = await self.db.execute(
                select(UploadedFile)
                .where(UploadedFile.upload_status != FileStatus.DELETED)
                .offset(skip)
                .limit(limit)
                .order_by(UploadedFile.created_at.desc())
            )
            files = result.scalars().all()
            
            # Get total count
            count_result = await self.db.execute(
                select(func.count(UploadedFile.id))
                .where(UploadedFile.upload_status != FileStatus.DELETED)
            )
            total_count = count_result.scalar() or 0
            
            # Format file information
            file_list = []
            for file_record in files:
                file_exists = os.path.exists(file_record.file_path)
                file_list.append({
                    "file_id": file_record.id,
                    "stored_filename": file_record.stored_filename,
                    "original_filename": file_record.original_filename,
                    "size": file_record.size,
                    "size_mb": file_record.size_mb,
                    "content_type": file_record.content_type,
                    "upload_status": file_record.upload_status.value,
                    "is_public": file_record.is_public,
                    "owner_id": file_record.owner_id,
                    "uploaded_at": file_record.created_at.isoformat(),
                    "filesystem_exists": file_exists,
                    "admin_visible": True
                })
            
            logger.info(f"Admin found {len(file_list)} total files")
            return {
                "files": file_list,
                "count": len(file_list),
                "total_count": total_count,
                "skip": skip,
                "limit": limit,
                "admin_access": True,
                "database_integrated": True
            }
            
        except Exception as e:
            logger.error(f"Error listing all files for admin: {e}")
            raise Exception("Failed to list all files")
        
    async def process_file_content(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Manually trigger content processing for uploaded file
        
        Args:
            file_id: ID of file to process
            user_id: ID of user who owns the file
            
        Returns:
            Processing result with status and details
        """
        try:
            logger.info(f"Manual processing triggered for file {file_id} by user {user_id}")
            
            # Delegate to DocumentService
            result = await self.document_service.process_uploaded_file(file_id, user_id)
            
            logger.info(f"Processing completed for file {file_id}: {result.get('success', False)}")
            return result
            
        except Exception as e:
            error_msg = f"Error processing file {file_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "file_id": file_id,
                "error": error_msg
            }

    async def get_file_content(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get extracted content from processed file
        
        Args:
            file_id: ID of file to get content from
            user_id: ID of user who owns the file
            
        Returns:
            Dict with content or error message
        """
        try:
            logger.info(f"Getting content for file {file_id} by user {user_id}")
            
            # Get content through DocumentService
            content = await self.document_service.get_file_content(file_id, user_id)
            
            if content:
                return {
                    "success": True,
                    "file_id": file_id,
                    "content": content,
                    "content_length": len(content)
                }
            else:
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": "No content found or file not processed yet"
                }
                
        except Exception as e:
            error_msg = f"Error getting content for file {file_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "file_id": file_id,
                "error": error_msg
            }
    
    async def get_processing_status(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get processing status for uploaded file
        
        Args:
            file_id: ID of file to check status
            user_id: ID of user who owns the file
            
        Returns:
            Dict with processing status details
        """
        try:
            logger.info(f"Getting processing status for file {file_id} by user {user_id}")
            
            # Get status through DocumentService
            status = await self.document_service.get_processing_status(file_id, user_id)
            
            if status:
                return {
                    "success": True,
                    "file_id": file_id,
                    **status  # Unpack all status details
                }
            else:
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": "File not found or access denied"
                }
                
        except Exception as e:
            error_msg = f"Error getting status for file {file_id}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "file_id": file_id,
                "error": error_msg
            }