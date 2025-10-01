from typing import Dict, Type, List, Any, Optional
import logging
from .base import BaseAIClient
from .mock_client import MockClient
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from app.schemas.exam_schemas import AIProvider

logger = logging.getLogger(__name__)

class AIClientFactory:
    """
    Factory class for creating and managing AI clients

    Responsibilities:
    - Create appropriate client instances based on provider
    - Validate client configurations
    - Discover available and healthy clients
    - Centralize client instantiation logic
    - Cache client instances for reuse
    """

    # Registry of available client classes
    _clients: Dict[AIProvider, Type[BaseAIClient]] = {
        AIProvider.MOCK: MockClient,
        AIProvider.OPENAI: OpenAIClient,
        AIProvider.GEMINI: GeminiClient,
    }

    # Cache for client instances (provider -> client)
    _client_cache: Dict[AIProvider, BaseAIClient] = {}
    
    @classmethod
    def create_client(cls, provider: AIProvider, *, use_cache: bool = True) -> BaseAIClient:
        """
        Create and return configured AI client instance (with caching).

        Args:
            provider: AI provider enum (OPENAI, GEMINI, MOCK)
            use_cache: Whether to use cached instance if available (default: True)

        Returns:
            BaseAIClient: Configured client instance

        Raises:
            ValueError: If provider not supported or not properly configured
        """
        # Check cache first
        if use_cache and provider in cls._client_cache:
            logger.debug(f"Returning cached client for provider: {provider.value}")
            return cls._client_cache[provider]

        logger.info(f"Creating new AI client for provider: {provider.value}")

        # Check if provider is supported
        if provider not in cls._clients:
            available_providers = list(cls._clients.keys())
            raise ValueError(
                f"Unsupported AI provider: {provider.value}. "
                f"Available providers: {[p.value for p in available_providers]}"
            )

        # Get client class and instantiate
        client_class = cls._clients[provider]

        try:
            client = client_class()
            logger.info(f"Successfully created {provider.value} client instance")
        except Exception as e:
            logger.error(f"Failed to create {provider.value} client: {e}", exc_info=True)
            raise ValueError(f"Failed to create {provider.value} client: {e}")

        # Validate client configuration
        if not client.is_configured():
            logger.error(f"{provider.value} client is not properly configured")
            raise ValueError(
                f"{provider.value} client is not properly configured. "
                f"Please check your API keys and settings."
            )

        # Cache the client instance
        if use_cache:
            cls._client_cache[provider] = client
            logger.debug(f"Cached client instance for provider: {provider.value}")

        logger.info(f"{provider.value} client created and configured successfully")
        return client

    @classmethod
    def clear_cache(cls, provider: Optional[AIProvider] = None) -> None:
        """
        Clear cached client instances.

        Args:
            provider: Specific provider to clear, or None to clear all
        """
        if provider is None:
            cls._client_cache.clear()
            logger.info("Cleared all cached client instances")
        elif provider in cls._client_cache:
            del cls._client_cache[provider]
            logger.info(f"Cleared cached client for provider: {provider.value}")

    @classmethod
    def get_cached_client(cls, provider: AIProvider) -> Optional[BaseAIClient]:
        """
        Get cached client instance without creating new one.

        Args:
            provider: AI provider enum

        Returns:
            Cached client instance or None if not cached
        """
        return cls._client_cache.get(provider)
    
    @classmethod
    async def get_available_clients(cls) -> List[Dict[str, Any]]:
        """
        Discover all available and healthy AI clients
        
        Returns:
            List[Dict]: List of client information with health status
            
        Example response:
        [
            {
                "provider": "mock",
                "is_configured": True,
                "is_healthy": True,
                "status": "available",
                "capabilities": {...}
            },
            {
                "provider": "openai", 
                "is_configured": False,
                "is_healthy": False,
                "status": "not_configured",
                "error": "API key not provided"
            }
        ]
        """
        logger.info("Discovering available AI clients...")
        available_clients = []
        
        for provider, client_class in cls._clients.items():
            client_info = {
                "provider": provider.value,
                "is_configured": False,
                "is_healthy": False,
                "status": "unknown",
                "capabilities": {},
                "error": None
            }
            
            try:
                # Try to create client instance
                client = client_class()
                
                # Check if configured
                is_configured = client.is_configured()
                client_info["is_configured"] = is_configured
                
                if is_configured:
                    # Check health if configured
                    is_healthy = await client.health_check()
                    client_info["is_healthy"] = is_healthy
                    
                    if is_healthy:
                        # Get capabilities if healthy
                        capabilities = client.get_capabilities()
                        client_info["capabilities"] = capabilities
                        client_info["status"] = "available"
                        logger.info(f"{provider.value} client is available and healthy")
                    else:
                        client_info["status"] = "configured_but_unhealthy"
                        client_info["error"] = "Health check failed"
                        logger.warning(f"{provider.value} client configured but unhealthy")
                else:
                    client_info["status"] = "not_configured"
                    client_info["error"] = "Missing configuration (API keys, etc.)"
                    logger.warning(f"{provider.value} client not configured")
                    
            except Exception as e:
                client_info["status"] = "error"
                client_info["error"] = str(e)
                logger.error(f"Error checking {provider.value} client: {e}")
            
            available_clients.append(client_info)
        
        # Sort by availability (available first)
        available_clients.sort(key=lambda x: (
            x["status"] != "available",  # Available first
            x["provider"]  # Then alphabetically
        ))
        
        logger.info(f"Discovery complete. Found {len(available_clients)} providers")
        return available_clients
    
    @classmethod
    def get_supported_providers(cls) -> List[AIProvider]:
        """
        Get list of supported AI providers
        
        Returns:
            List[AIProvider]: List of supported provider enums
        """
        return list(cls._clients.keys())
    
    @classmethod
    def is_provider_supported(cls, provider: AIProvider) -> bool:
        """
        Check if a provider is supported
        
        Args:
            provider: AI provider to check
            
        Returns:
            bool: True if supported, False otherwise
        """
        return provider in cls._clients
    
    @classmethod
    def register_client(cls, provider: AIProvider, client_class: Type[BaseAIClient]) -> None:
        """
        Register a new client class (for extensibility)
        
        Args:
            provider: AI provider enum
            client_class: Client class implementing BaseAIClient
        """
        if not issubclass(client_class, BaseAIClient):
            raise ValueError(f"Client class must inherit from BaseAIClient")
        
        cls._clients[provider] = client_class
        logger.info(f"Registered new client: {provider.value} -> {client_class.__name__}")
    
    @classmethod
    async def health_check_all(cls) -> Dict[str, bool]:
        """
        Quick health check for all configured clients (uses cached instances).

        Returns:
            Dict[str, bool]: Provider name -> health status
        """
        health_status = {}

        for provider in cls._clients.keys():
            try:
                # Use cache to avoid creating new instances each time
                client = cls.create_client(provider, use_cache=True)
                is_healthy = await client.health_check()
                health_status[provider.value] = is_healthy
            except Exception as e:
                logger.debug(f"Health check failed for {provider.value}: {e}")
                health_status[provider.value] = False

        return health_status

# Convenience functions for common operations
async def create_default_client() -> BaseAIClient:
    """
    Create client with default provider from environment variable.

    Falls back to best available client if DEFAULT_AI_PROVIDER not set.
    """
    import os

    # Get default provider from environment
    default_provider_str = os.getenv("DEFAULT_AI_PROVIDER", "").lower()

    # Try to use specified default provider
    if default_provider_str:
        try:
            provider = AIProvider(default_provider_str)
            logger.info(f"Using default AI provider from env: {provider.value}")
            return AIClientFactory.create_client(provider)
        except (ValueError, KeyError) as e:
            logger.warning(f"Invalid DEFAULT_AI_PROVIDER '{default_provider_str}': {e}")

    # Fallback to best available client
    logger.info("DEFAULT_AI_PROVIDER not set, using best available client")
    client = await create_best_available_client()

    if client is None:
        logger.error("No healthy AI clients available, falling back to MOCK")
        return AIClientFactory.create_client(AIProvider.MOCK)

    return client

async def create_best_available_client() -> Optional[BaseAIClient]:
    """
    Create the best available client based on health and capabilities
    
    Priority: OpenAI > Gemini > Mock
    """
    available_clients = await AIClientFactory.get_available_clients()
    
    # Filter only healthy clients
    healthy_clients = [c for c in available_clients if c["is_healthy"]]
    
    if not healthy_clients:
        logger.warning("No healthy AI clients available")
        return None
    
    # Priority order
    priority_order = ["openai", "gemini", "mock"]
    
    for provider_name in priority_order:
        for client_info in healthy_clients:
            if client_info["provider"] == provider_name:
                provider = AIProvider(provider_name)
                return AIClientFactory.create_client(provider)
    
    # Fallback to first healthy client
    first_healthy = healthy_clients[0]
    provider = AIProvider(first_healthy["provider"])
    return AIClientFactory.create_client(provider)