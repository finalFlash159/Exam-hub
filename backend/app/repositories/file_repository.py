import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import UploadedFile, FileStatus, StorageType, ProcessingStatus
from .base import BaseRepository

logger = logging.getLogger(__name__)


class FileRepository(BaseRepository[UploadedFile]):
    """Repository for file operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(UploadedFile, session)
    
    async def create_file_record(
        self,
        original_filename: str,
        stored_filename: str,
        file_path: str,
        size: int,
        content_type: str,
        owner_id: str,
        file_hash: Optional[str] = None,
        **kwargs
    ) -> UploadedFile:
        """
        Create file record in database
        
        Args:
            original_filename: Original name of uploaded file
            stored_filename: Unique filename used for storage
            file_path: Full path where file is stored
            size: File size in bytes
            content_type: MIME type of file
            owner_id: ID of user who uploaded file
            file_hash: SHA-256 hash of file content
            **kwargs: Additional fields
            
        Returns:
            Created file record
        """
        try:
            file_data = {
                'original_filename': original_filename,
                'stored_filename': stored_filename,
                'file_path': file_path,
                'size': size,
                'content_type': content_type,
                'owner_id': owner_id,
                'file_hash': file_hash,
                'upload_status': FileStatus.COMPLETED,
                'storage_type': StorageType.LOCAL,
                **kwargs
            }
            
            file_record = await self.create(**file_data)
            
            self.logger.info(f"Created file record: {stored_filename} for user {owner_id}")
            return file_record
            
        except Exception as e:
            self.logger.error(f"Failed to create file record: {e}")
            raise
    
    async def get_user_files(
        self, 
        owner_id: str, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[FileStatus] = None
    ) -> List[UploadedFile]:
        """
        Get files owned by specific user
        
        Args:
            owner_id: ID of file owner
            skip: Number of records to skip
            limit: Maximum number of records
            status_filter: Optional status filter
            
        Returns:
            List of user's files
        """
        try:
            query = select(UploadedFile).where(UploadedFile.owner_id == owner_id)
            
            if status_filter:
                query = query.where(UploadedFile.upload_status == status_filter)
            
            query = query.offset(skip).limit(limit).order_by(UploadedFile.created_at.desc())
            
            result = await self.session.execute(query)
            files = result.scalars().all()
            
            self.logger.debug(f"Retrieved {len(files)} files for user {owner_id}")
            return list(files)
            
        except Exception as e:
            self.logger.error(f"Failed to get files for user {owner_id}: {e}")
            raise
    
    async def get_by_stored_filename(self, stored_filename: str) -> Optional[UploadedFile]:
        """
        Get file by stored filename
        
        Args:
            stored_filename: Unique stored filename
            
        Returns:
            File record if found
        """
        try:
            result = await self.session.execute(
                select(UploadedFile).where(UploadedFile.stored_filename == stored_filename)
            )
            file_record = result.scalar_one_or_none()
            
            if file_record:
                self.logger.debug(f"Found file record: {stored_filename}")
            else:
                self.logger.debug(f"No file record found: {stored_filename}")
            
            return file_record
            
        except Exception as e:
            self.logger.error(f"Error getting file by stored filename {stored_filename}: {e}")
            raise
    
    async def get_by_hash(self, file_hash: str) -> Optional[UploadedFile]:
        """
        Get file by hash (for duplicate detection)
        
        Args:
            file_hash: SHA-256 hash of file content
            
        Returns:
            Existing file with same hash
        """
        try:
            result = await self.session.execute(
                select(UploadedFile).where(
                    and_(
                        UploadedFile.file_hash == file_hash,
                        UploadedFile.upload_status == FileStatus.COMPLETED
                    )
                )
            )
            file_record = result.scalar_one_or_none()
            
            if file_record:
                self.logger.debug(f"Found duplicate file with hash: {file_hash}")
            
            return file_record
            
        except Exception as e:
            self.logger.error(f"Error checking file hash {file_hash}: {e}")
            raise

    async def get_file_by_id(self, file_id: str, user_id: str) -> Optional[UploadedFile]:
        """
        Get file by ID with user ownership validation
        Returns None if file not found or user doesn't own it
        """
        try:
            stmt = (
                select(UploadedFile)
                .where(
                    and_(
                        UploadedFile.id == file_id,
                        UploadedFile.owner_id == user_id,
                        UploadedFile.upload_status != FileStatus.DELETED
                    )
                )
            )
            
            result = await self.session.execute(stmt)
            file_record = result.scalar_one_or_none()
            
            if file_record:
                self.logger.debug(f"Found file {file_id} for user {user_id}")
            else:
                self.logger.debug(f"File {file_id} not found or not owned by user {user_id}")
            
            return file_record
            
        except Exception as e:
            self.logger.error(f"Failed to get file {file_id} for user {user_id}: {e}")
            return None
    
    async def update_status(
        self, 
        file_id: str, 
        status: FileStatus, 
        error_message: Optional[str] = None
    ) -> Optional[UploadedFile]:
        """
        Update file upload status
        
        Args:
            file_id: ID of file to update
            status: New status
            error_message: Error message if status is FAILED
            
        Returns:
            Updated file record
        """
        try:
            file_record = await self.get_by_id(file_id)
            if not file_record:
                return None
            
            file_record.upload_status = status
            if error_message:
                file_record.error_message = error_message
            
            await self.session.commit()
            
            self.logger.info(f"Updated file {file_id} status to {status}")
            return file_record
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to update file status: {e}")
            raise
    
    async def delete_file_record(self, file_id: str, owner_id: str) -> bool:
        """
        Delete file record (with ownership check)
        
        Args:
            file_id: ID of file to delete
            owner_id: ID of file owner
            
        Returns:
            True if deleted successfully
        """
        try:
            file_record = await self.session.execute(
                select(UploadedFile).where(
                    and_(
                        UploadedFile.id == file_id,
                        UploadedFile.owner_id == owner_id
                    )
                )
            )
            file_record = file_record.scalar_one_or_none()
            
            if not file_record:
                self.logger.warning(f"File not found or access denied: {file_id}")
                return False
            
            # Soft delete - mark as deleted
            file_record.upload_status = FileStatus.DELETED
            await self.session.commit()
            
            self.logger.info(f"Deleted file record: {file_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to delete file record {file_id}: {e}")
            raise
    
    async def count_user_files(self, owner_id: str) -> int:
        """
        Count total files for user
        
        Args:
            owner_id: ID of file owner
            
        Returns:
            Total file count
        """
        try:
            result = await self.session.execute(
                select(func.count(UploadedFile.id)).where(
                    and_(
                        UploadedFile.owner_id == owner_id,
                        UploadedFile.upload_status != FileStatus.DELETED
                    )
                )
            )
            count = result.scalar() or 0
            
            self.logger.debug(f"User {owner_id} has {count} files")
            return count
            
        except Exception as e:
            self.logger.error(f"Failed to count files for user {owner_id}: {e}")
            raise
    
    async def update_processing_status(self, file_id: str, status: ProcessingStatus, error_message: Optional[str] = None) -> bool:
        try:
            # Get file and ensure it exists
            file_record = await self.get_by_id(file_id)
            if not file_record:
                self.logger.warning(f"File not found for processing status update: {file_id}")
                return False

            # update processing fields
            file_record.processing_status = status
            if error_message:
                file_record.processing_error = error_message
            
            # Set timestamp fields
            if status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
                file_record.processed_at = datetime.now(timezone.utc)
            
            await self.session.commit()

            self.logger.info(f"Updated processing status for file {file_id}: {status}")
            return True
        
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to update processing status for file {file_id}: {e}")
            return False
        
    async def save_extracted_content(
            self, 
            file_id: str, 
            content: str, 
            user_id: str
        ) -> bool:
            """Save extracted text content for a file"""
            try:                
                # Get file and validate ownership
                file_record = await self.get_file_by_id(file_id, user_id)
                if not file_record:
                    self.logger.warning(f"File not found or access denied: {file_id} for user {user_id}")
                    return False
                
                # Update content fields
                file_record.extracted_content = content
                file_record.content_length = len(content)
                file_record.processing_status = ProcessingStatus.COMPLETED
                file_record.processed_at = datetime.now(timezone.utc)
                file_record.processing_error = None  # Clear any previous errors
                
                await self.session.commit()
                
                self.logger.info(f"Saved extracted content for file {file_id}: {len(content)} characters")
                return True
                
            except Exception as e:
                await self.session.rollback()
                self.logger.error(f"Failed to save extracted content for file {file_id}: {e}")
                return False
    
    async def get_files_pending_processing(
        self, 
        limit: int = 10
    ) -> List[UploadedFile]:
        """Get files that are pending processing"""
        try:
            stmt = (
                select(UploadedFile)
                .where(
                    and_(
                        UploadedFile.processing_status == ProcessingStatus.PENDING,
                        UploadedFile.upload_status == FileStatus.COMPLETED
                    )
                )
                .order_by(UploadedFile.created_at.asc())
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            files = result.scalars().all()
            
            self.logger.debug(f"Found {len(files)} files pending processing")
            return list(files)
            
        except Exception as e:
            self.logger.error(f"Failed to get files pending processing: {e}")
            return []
    
    async def get_file_content(
        self, 
        file_id: str, 
        user_id: str
    ) -> Optional[str]:
        """Get extracted content for a file (user-scoped)"""
        try:
            # Get file and validate ownership
            file_record = await self.get_file_by_id(file_id, user_id)
            if not file_record:
                self.logger.warning(f"File not found or access denied: {file_id} for user {user_id}")
                return None
            
            # Check if content is available
            if file_record.processing_status != ProcessingStatus.COMPLETED:
                self.logger.info(f"File {file_id} not yet processed: {file_record.processing_status}")
                return None
            
            return file_record.extracted_content
            
        except Exception as e:
            self.logger.error(f"Failed to get file content for {file_id}: {e}")
            return None
    
    async def get_processing_status(
        self, 
        file_id: str, 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get processing status information for a file"""
        try:
            # Get file and validate ownership
            file_record = await self.get_file_by_id(file_id, user_id)
            if not file_record:
                self.logger.warning(f"File not found or access denied: {file_id} for user {user_id}")
                return None
            
            return {
                "file_id": file_record.id,
                "processing_status": file_record.processing_status.value,
                "content_length": file_record.content_length,
                "processing_error": file_record.processing_error,
                "processed_at": file_record.processed_at.isoformat() if file_record.processed_at else None,
                "has_content": bool(file_record.extracted_content)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get processing status for {file_id}: {e}")
            return None
