"""
GenAI Clients Module

Provides AI client implementations and factory for creating clients
"""

from .base import BaseAIClient
from .mock_client import MockClient
from .factory import AIClientFactory, create_default_client, create_best_available_client
from app.schemas.exam_schemas import AIProvider

__all__ = [
    # Base classes
    "BaseAIClient",
    "AIProvider",
    
    # Client implementations
    "MockClient",
    
    # Factory
    "AIClientFactory",
    "create_default_client", 
    "create_best_available_client",
]