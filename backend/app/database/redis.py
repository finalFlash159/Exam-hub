"""
Redis Connection Manager for Rate Limiting and Caching
Handles Redis connection lifecycle with graceful fallback
"""

import os
import logging
from redis import asyncio as aioredis
from typing import Optional

logger = logging.getLogger(__name__)


class RedisManager:
    """Manage Redis connection for the application."""

    _redis_client: Optional[aioredis.Redis] = None

    @classmethod
    async def get_redis(cls) -> aioredis.Redis:
        """
        Get or create Redis client instance.

        Returns:
            Redis client instance
        """
        if cls._redis_client is None:
            await cls.connect()
        return cls._redis_client

    @classmethod
    async def connect(cls) -> None:
        """
        Initialize Redis connection.

        Reads from environment variables:
        - REDIS_URL: Full Redis URL (redis://host:port/db)
        - REDIS_HOST: Redis host (default: localhost)
        - REDIS_PORT: Redis port (default: 6379)
        - REDIS_DB: Redis database number (default: 0)
        - REDIS_PASSWORD: Redis password (optional)
        """
        try:
            # Try full Redis URL first
            redis_url = os.getenv("REDIS_URL")

            if redis_url:
                cls._redis_client = await aioredis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=10
                )
                logger.info(f"Connected to Redis: {redis_url}")
            else:
                # Fallback to individual parameters
                host = os.getenv("REDIS_HOST", "localhost")
                port = int(os.getenv("REDIS_PORT", "6379"))
                db = int(os.getenv("REDIS_DB", "0"))
                password = os.getenv("REDIS_PASSWORD")

                cls._redis_client = await aioredis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    password=password,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=10
                )
                logger.info(f"Connected to Redis: {host}:{port}/{db}")

            # Test connection
            await cls._redis_client.ping()
            logger.info("Redis connection successful")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Rate limiting will be disabled")
            cls._redis_client = None

    @classmethod
    async def disconnect(cls) -> None:
        """Close Redis connection."""
        if cls._redis_client:
            await cls._redis_client.close()
            cls._redis_client = None
            logger.info("Redis connection closed")

    @classmethod
    async def health_check(cls) -> bool:
        """
        Check if Redis is healthy.

        Returns:
            True if Redis is reachable, False otherwise
        """
        try:
            if cls._redis_client is None:
                return False
            await cls._redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# Convenience function
async def get_redis_client() -> Optional[aioredis.Redis]:
    """
    Get Redis client instance.

    Returns:
        Redis client or None if not connected
    """
    try:
        return await RedisManager.get_redis()
    except Exception:
        return None
