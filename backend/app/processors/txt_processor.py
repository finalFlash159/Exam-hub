import os
import logging

from .base import BaseProcessor, ProcessingResult

logger = logging.getLogger(__name__)


class TXTProcessor(BaseProcessor):
    """Simple TXT file reader"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.txt'}
    
    async def extract_text(self, file_path: str) -> ProcessingResult:
        """Read text file - try different encodings"""
        try:
            if not os.path.exists(file_path):
                return ProcessingResult(
                    success=False,
                    content="",
                    error_message=f"File not found: {file_path}"
                )
            
            # Try common encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read().strip()
                    
                    if not text:
                        return ProcessingResult(
                            success=False,
                            content="",
                            error_message="Text file is empty"
                        )
                    
                    logger.info(f"Extracted {len(text)} chars from TXT ({encoding})")
                    return ProcessingResult(success=True, content=text)
                    
                except UnicodeDecodeError:
                    continue
            
            return ProcessingResult(
                success=False,
                content="",
                error_message="Could not decode text file with any encoding"
            )
            
        except Exception as e:
            logger.error(f"TXT extraction failed: {e}")
            return ProcessingResult(
                success=False,
                content="",
                error_message=f"TXT processing error: {str(e)}"
            )