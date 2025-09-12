import os
import logging

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from .base import BaseProcessor, ProcessingResult

logger = logging.getLogger(__name__)


class PDFProcessor(BaseProcessor):
    """Simple PDF text extractor"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.pdf'}
        
        if fitz is None:
            raise ImportError("PyMuPDF required: pip install PyMuPDF")
    
    async def extract_text(self, file_path: str) -> ProcessingResult:
        """Extract text from PDF - simple and clean"""
        try:
            if not os.path.exists(file_path):
                return ProcessingResult(
                    success=False,
                    content="",
                    error_message=f"File not found: {file_path}"
                )
            
            text = ""
            with fitz.open(file_path) as pdf:
                for page in pdf:
                    text += page.get_text()
            
            text = text.strip()
            if not text:
                return ProcessingResult(
                    success=False,
                    content="",
                    error_message="No text content found in PDF"
                )
            
            logger.info(f"Extracted {len(text)} chars from PDF")
            return ProcessingResult(success=True, content=text)
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ProcessingResult(
                success=False,
                content="",
                error_message=f"PDF processing error: {str(e)}"
            )