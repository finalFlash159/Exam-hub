# import
from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum

from app.schemas.exam_schemas import AIProvider

class BaseAIClient(ABC):
    @abstractmethod
    async def health_check(self) -> bool:
        pass
    
    @abstractmethod
    async def generate_exam(self, prompt: str, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        pass