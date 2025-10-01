"""
GenAI Module - AI-powered exam generation

Domain-driven module for all generative AI functionality
"""

from .clients import (
    AIClientFactory,
    BaseAIClient,
    MockClient,
    AIProvider,
    create_default_client,
    create_best_available_client
)

__all__ = [
    # Factory and clients
    "AIClientFactory",
    "BaseAIClient", 
    "MockClient",
    "AIProvider",
    "create_default_client",
    "create_best_available_client",
]