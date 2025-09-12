import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.processors import DocumentProcessor, ProcessingResult
from app.repositories.file_repository import FileRepository
from app.models.file import ProcessingStatus

logger = logging.getLogger(__name__)

class DocumentService:
    """Service for document processing business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_repo = FileRepository(db)
        self.document_processor = DocumentProcessor()
        self.logger = logger

    async def process_uploaded_file(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Process uploaded file and extract content
        
        Args:
            file_id: ID of file to process
            user_id: ID of user who owns the file
                    
        Returns:
            Processing result with status and details
        """
        try:
            self.logger.info(f"Starting document processing for file: {file_id}")
            
            # Get file record
            file_record = await self.file_repo.get_file_by_id(file_id, user_id)
            if not file_record:
                error_msg = f"File not found: {file_id}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": error_msg
                }
            
            # Check if file is ready for processing
            if file_record.processing_status != ProcessingStatus.PENDING:
                self.logger.info(f"File {file_id} already processed: {file_record.processing_status}")
                return {
                    "success": True,
                    "file_id": file_id,
                    "status": file_record.processing_status.value,
                    "message": "File already processed"
                }
            
            # Update status to PROCESSING
            await self.file_repo.update_processing_status(
                file_id, 
                ProcessingStatus.PROCESSING
            )
            
            # Extract content using processors
            processing_result = await self._extract_file_content(file_record)
            
            # Update database with results
            if processing_result["success"]:
                await self._save_processing_success(file_record, processing_result)
                return {
                    "success": True,
                    "file_id": file_id,
                    "content_length": len(processing_result["content"]),
                    "processing_time": processing_result.get("processing_time", 0),
                    "message": "Document processed successfully"
                }
            else:
                await self._save_processing_failure(file_record, processing_result["error"])
                return {
                    "success": False,
                    "file_id": file_id,
                    "error": processing_result["error"],
                    "message": "Document processing failed"
                }
                
        except Exception as e:
            error_msg = f"Unexpected error processing file {file_id}: {str(e)}"
            self.logger.error(error_msg)
            
            # Update status to FAILED
            try:
                await self.file_repo.update_processing_status(
                    file_id, 
                    ProcessingStatus.FAILED, 
                    error_msg
                )
            except:
                pass  # Don't fail if we can't update status
            
            return {
                "success": False,
                "file_id": file_id,
                "error": error_msg
            }
    
    async def _extract_file_content(self, file_record) -> Dict[str, Any]:
        """Extract content from file using processors"""
        try:
            file_path = file_record.file_path
            
            # Check if file exists on filesystem
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found on filesystem: {file_path}"
                }
            
            self.logger.info(f"Extracting content from: {file_path}")
            
            # Use document processor to extract content
            result = await self.document_processor.extract_text(file_path)
            
            if result.success:
                self.logger.info(f"Successfully extracted {len(result.content)} characters")
                return {
                    "success": True,
                    "content": result.content,
                    "content_length": len(result.content)
                }
            else:
                self.logger.error(f"Content extraction failed: {result.error_message}")
                return {
                    "success": False,
                    "error": result.error_message or "Content extraction failed"
                }
                
        except Exception as e:
            error_msg = f"Error during content extraction: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _save_processing_success(self, file_record, processing_result: Dict[str, Any]):
        """Save successful processing results to database"""
        try:
            content = processing_result["content"]
            
            # Save extracted content
            success = await self.file_repo.save_extracted_content(
                file_record.id,
                content,
                file_record.owner_id
            )
            
            if success:
                self.logger.info(f"Saved processing results for file: {file_record.id}")
            else:
                self.logger.error(f"Failed to save processing results for file: {file_record.id}")
                
        except Exception as e:
            self.logger.error(f"Error saving processing success: {e}")
            # Re-raise to let caller handle
            raise
    
    async def _save_processing_failure(self, file_record, error_message: str):
        """Save processing failure to database"""
        try:
            await self.file_repo.update_processing_status(
                file_record.id,
                ProcessingStatus.FAILED,
                error_message
            )
            
            self.logger.info(f"Saved processing failure for file: {file_record.id}")
            
        except Exception as e:
            self.logger.error(f"Error saving processing failure: {e}")
            # Don't re-raise - this is cleanup
        
    async def get_file_content(self, file_id: str, user_id: str) -> Optional[str]:
        """Get extracted content for a file"""
        try:
            return await self.file_repo.get_file_content(file_id, user_id)
        except Exception as e:
            self.logger.error(f"Error getting file content: {e}")
            return None
    
    async def get_processing_status(self, file_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get processing status for a file"""
        try:
            return await self.file_repo.get_processing_status(file_id, user_id)
        except Exception as e:
            self.logger.error(f"Error getting processing status: {e}")
            return None
    
    async def reprocess_file(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """Trigger reprocessing of a file"""
        try:
            # Validate file ownership
            file_record = await self.file_repo.get_file_by_id(file_id, user_id)
            if not file_record:
                return {
                    "success": False,
                    "error": "File not found or access denied"
                }
            
            # Reset processing status
            await self.file_repo.update_processing_status(
                file_id, 
                ProcessingStatus.PENDING
            )
            
            # Trigger processing
            return await self.process_uploaded_file(file_id, user_id)
            
        except Exception as e:
            error_msg = f"Error reprocessing file: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def get_pending_files(self, limit: int = 10):
        """Get files pending processing"""
        try:
            return await self.file_repo.get_files_pending_processing(limit)
        except Exception as e:
            self.logger.error(f"Error getting pending files: {e}")
            return []