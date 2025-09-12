import os
import logging
from typing import Dict

from .base import ProcessingResult
from .pdf_processor import PDFProcessor
from .docx_processor import DOCXProcessor
from .txt_processor import TXTProcessor

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Simple document processor - route to right processor"""
    
    def __init__(self):
        self.processors = {
            '.pdf': PDFProcessor(),
            '.docx': DOCXProcessor(), 
            '.txt': TXTProcessor()
        }
    
    async def extract_text(self, file_path: str) -> ProcessingResult:
        """Extract text from any supported document"""
        try:
            # Get file extension
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            # Find processor
            processor = self.processors.get(ext)
            if not processor:
                return ProcessingResult(
                    success=False,
                    content="",
                    error_message=f"Unsupported file type: {ext}"
                )
            
            # Process file
            logger.info(f"Processing {ext} file: {file_path}")
            result = await processor.extract_text(file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return ProcessingResult(
                success=False,
                content="",
                error_message=f"Processing error: {str(e)}"
            )
    
    def get_supported_extensions(self) -> set:
        """Get all supported file extensions"""
        return set(self.processors.keys())