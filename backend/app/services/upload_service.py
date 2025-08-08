"""
Upload Service  
Business logic for file upload, validation, and processing
"""

import os
import uuid
import logging
from typing import Dict, Any

from fastapi import UploadFile

# Temporarily use old config import during migration
try:
    from app.core.config import get_settings
except ImportError:
    from core.config import get_settings

logger = logging.getLogger(__name__)


class UploadService:
    """Service for handling file upload business logic"""
    
    def __init__(self):
        """Initialize upload service"""
        logger.info("UploadService initialized")
    
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
    
    async def save_uploaded_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Save uploaded file with validation and processing
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            Dict containing file info and metadata
            
        Raises:
            ValueError: For validation errors
            Exception: For file operation errors
        """
        logger.info(f"Processing upload request - filename: {file.filename}")
        logger.debug(f"Content type: {file.content_type}")
        
        # Get settings
        settings = get_settings()
        
        # Validate filename
        if not file.filename:
            logger.warning("No filename provided")
            raise ValueError("No selected file")
        
        # Validate file extension
        if not self.is_allowed_file(file.filename, settings["allowed_extensions"]):
            logger.warning(f"File type not allowed: {file.filename}")
            raise ValueError("File type not allowed")
        
        # Read and validate file size
        logger.debug("Reading file content...")
        content = await file.read()
        file_size = len(content)
        logger.info(f"File size: {file_size} bytes")
        
        if file_size > settings["max_upload_size"]:
            logger.warning(f"File too large: {file_size} > {settings['max_upload_size']}")
            raise ValueError("File too large")
        
        if file_size == 0:
            logger.warning("Empty file received")
            raise ValueError("Empty file not allowed")
        
        # Prepare upload directory
        upload_folder = settings["upload_folder"]
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        logger.debug(f"Generated unique filename: {unique_filename}")
        logger.debug(f"Full save path: {file_path}")
        
        # Save file
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
            logger.info(f"File saved successfully: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            # Clean up partial file if it exists
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            raise Exception(f"Failed to save file: {str(e)}")
        
        # Verify file was saved correctly
        if not os.path.exists(file_path):
            logger.error("File was not saved successfully")
            raise Exception("File save verification failed")
        
        saved_size = os.path.getsize(file_path)
        if saved_size != file_size:
            logger.error(f"File size mismatch: expected {file_size}, got {saved_size}")
            # Clean up incorrect file
            try:
                os.remove(file_path)
            except:
                pass
            raise Exception("File save verification failed - size mismatch")
        
        # Prepare response
        result = {
            'message': 'File uploaded successfully',
            'file_id': unique_filename,
            'original_filename': file.filename,
            'size': file_size,
            'content_type': file.content_type,
            'metadata': {
                'upload_folder': upload_folder,
                'save_path': file_path,
                'extension': file_extension,
                'validation_passed': True
            }
        }
        
        logger.info(f"Upload completed successfully: {unique_filename}")
        return result
    
    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete uploaded file
        
        Args:
            file_id: ID of file to delete
            
        Returns:
            Dict with deletion result
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For deletion errors
        """
        logger.info(f"Delete file request: {file_id}")
        
        # Get file path
        settings = get_settings()
        upload_folder = settings["upload_folder"]
        file_path = os.path.join(upload_folder, file_id)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found for deletion: {file_path}")
            raise FileNotFoundError(f"File not found: {file_id}")
        
        # Delete file
        try:
            os.remove(file_path)
            logger.info(f"File deleted successfully: {file_path}")
            
            return {
                'message': 'File deleted successfully',
                'file_id': file_id,
                'deleted': True
            }
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise Exception(f"Failed to delete file: {str(e)}")
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        Get information about uploaded file
        
        Args:
            file_id: ID of file to get info for
            
        Returns:
            Dict with file information
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        logger.debug(f"Get file info request: {file_id}")
        
        # Get file path
        settings = get_settings()
        upload_folder = settings["upload_folder"]
        file_path = os.path.join(upload_folder, file_id)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_id}")
        
        # Get file stats
        file_stats = os.stat(file_path)
        
        return {
            'file_id': file_id,
            'file_path': file_path,
            'size': file_stats.st_size,
            'created_at': file_stats.st_ctime,
            'modified_at': file_stats.st_mtime,
            'exists': True
        } 