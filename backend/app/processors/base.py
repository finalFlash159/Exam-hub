# app/processors/base.py
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class ProcessingResult:
    """Simple processing result"""
    success: bool
    content: str
    error_message: Optional[str] = None


class BaseProcessor(ABC):
    """Simple base processor interface"""
    
    def __init__(self):
        self.supported_extensions: set = set()
    
    @abstractmethod
    async def extract_text(self, file_path: str) -> ProcessingResult:
        """Extract text from file - that's it!"""
        pass
    
    def supports_file(self, file_path: str) -> bool:
        """Check if processor supports this file type"""
        import os
        extension = os.path.splitext(file_path)[1].lower()
        return extension in self.supported_extensions