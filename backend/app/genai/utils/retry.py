"""
Retry logic utilities for AI API calls.

Handles transient failures with exponential backoff.
"""

import asyncio
import logging
from typing import Any, Callable, Optional, Type, Tuple
from functools import wraps
from http.client import RemoteDisconnected
from urllib.error import URLError

logger = logging.getLogger(__name__)


# Define retryable exceptions (transient errors only)
TRANSIENT_EXCEPTIONS = (
    ConnectionError,      # Network connection errors
    TimeoutError,         # Timeout errors
    asyncio.TimeoutError, # Async timeout errors
    RemoteDisconnected,   # HTTP connection dropped
    URLError,             # URL/network errors
    OSError,              # OS-level I/O errors (includes network)
)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
        timeout: Optional[float] = 60.0,
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of attempts (including initial)
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff calculation
            timeout: Total timeout for operation in seconds (None = no timeout)
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.timeout = timeout

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.initial_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


# Default configurations by provider
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=10.0,
    timeout=60.0,
)

OPENAI_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=10.0,
    timeout=60.0,
)

GEMINI_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=2.0,
    max_delay=15.0,
    timeout=90.0,
)


async def retry_with_backoff(
    func: Callable,
    *args: Any,
    config: Optional[RetryConfig] = None,
    retryable_exceptions: Tuple[Type[Exception], ...] = TRANSIENT_EXCEPTIONS,
    context: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """
    Execute async function with retry and exponential backoff.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        config: Retry configuration (uses default if None)
        retryable_exceptions: Tuple of exception types to retry on
        context: Context string for logging (e.g., "OpenAI API call")
        **kwargs: Keyword arguments for func

    Returns:
        Result from func

    Raises:
        Last exception if all retries exhausted
        asyncio.TimeoutError: If operation exceeds timeout
    """
    config = config or DEFAULT_RETRY_CONFIG
    context_str = f" ({context})" if context else ""
    last_exception: Optional[Exception] = None

    for attempt in range(config.max_attempts):
        try:
            # Apply timeout if configured
            if config.timeout:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=config.timeout
                )
            else:
                return await func(*args, **kwargs)

        except asyncio.TimeoutError as e:
            last_exception = e
            logger.warning(
                f"Timeout{context_str} on attempt {attempt + 1}/{config.max_attempts} "
                f"(timeout={config.timeout}s)"
            )
            if attempt + 1 >= config.max_attempts:
                logger.error(f"All retry attempts exhausted{context_str} due to timeout")
                raise

        except retryable_exceptions as e:
            last_exception = e
            is_last_attempt = (attempt + 1 >= config.max_attempts)

            if is_last_attempt:
                logger.error(
                    f"Final attempt failed{context_str}: {type(e).__name__}: {e}"
                )
                raise
            else:
                delay = config.get_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{config.max_attempts} failed{context_str}: "
                    f"{type(e).__name__}: {e}. Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)

        except Exception as e:
            # Non-retryable exception - fail immediately
            logger.error(
                f"Non-retryable error{context_str}: {type(e).__name__}: {e}"
            )
            raise

    # Should not reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError(f"Unexpected retry loop exit{context_str}")


def with_retry(
    config: Optional[RetryConfig] = None,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    context: Optional[str] = None,
):
    """
    Decorator to add retry logic to async functions.

    Args:
        config: Retry configuration
        retryable_exceptions: Tuple of exception types to retry on
        context: Context string for logging

    Example:
        @with_retry(config=OPENAI_RETRY_CONFIG, context="OpenAI generation")
        async def generate_exam(prompt: str) -> dict:
            # ... implementation
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                func,
                *args,
                config=config,
                retryable_exceptions=retryable_exceptions,
                context=context or func.__name__,
                **kwargs,
            )
        return wrapper
    return decorator