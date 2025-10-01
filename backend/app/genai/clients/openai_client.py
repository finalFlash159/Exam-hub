import os
import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from .base import BaseAIClient

try:
    from openai import OpenAI  # type: ignore
    from openai import OpenAIError  # type: ignore
except ImportError:
    OpenAI = None  # type: ignore
    OpenAIError = Exception  # type: ignore


logger = logging.getLogger(__name__)


class OpenAIClient(BaseAIClient):
    """Simple OpenAI API wrapper. Just calls API, no retry/parsing logic."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> None:
        self.api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.model_name: str = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.default_temperature: float = (
            temperature if temperature is not None
            else float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
        )
        self._client: Optional["OpenAI"] = None

    async def health_check(self) -> bool:
        if not self.is_configured():
            return False
        try:
            self._get_client()
            return True
        except Exception:
            return False

    async def generate_exam(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Call OpenAI API and return raw response."""
        if not self.is_configured():
            return {
                "success": False,
                "raw_response": "",
                "metadata": {
                    "ai_provider": "openai",
                    "model": self.model_name,
                    "generated_at": datetime.now().isoformat(),
                },
                "error": "OpenAI API key not configured"
            }

        temperature = float(kwargs.get("temperature", self.default_temperature))
        max_tokens = kwargs.get("max_tokens")

        try:
            response_text = await self._call_api(prompt, temperature, max_tokens)

            return {
                "success": True,
                "raw_response": response_text,
                "metadata": {
                    "ai_provider": "openai",
                    "model": self.model_name,
                    "temperature": temperature,
                    "generated_at": datetime.now().isoformat(),
                },
                "error": None
            }

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "success": False,
                "raw_response": "",
                "metadata": {
                    "ai_provider": "openai",
                    "model": self.model_name,
                    "generated_at": datetime.now().isoformat(),
                },
                "error": f"OpenAI API error: {str(e)}"
            }

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {
                "success": False,
                "raw_response": "",
                "metadata": {
                    "ai_provider": "openai",
                    "model": self.model_name,
                    "generated_at": datetime.now().isoformat(),
                },
                "error": str(e)
            }

    def is_configured(self) -> bool:
        return bool(self.api_key) and OpenAI is not None

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "model": self.model_name,
            "supports_json": True,
            "supports_streaming": False,
            "max_tokens": 4096,
        }

    # Private methods
    def _get_client(self) -> "OpenAI":
        """Lazy init OpenAI SDK client."""
        if self._client is None:
            if OpenAI is None:
                raise RuntimeError("OpenAI SDK not installed")
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    async def _call_api(
        self,
        prompt: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """Run OpenAI API call in thread pool (SDK is sync)."""
        return await asyncio.to_thread(
            self._sync_call_api, prompt, temperature, max_tokens
        )

    def _sync_call_api(
        self,
        prompt: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """Actual sync API call."""
        client = self._get_client()

        params: Dict[str, Any] = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        if max_tokens:
            params["max_tokens"] = int(max_tokens)

        response = client.chat.completions.create(**params)
        content = response.choices[0].message.content if response.choices else ""

        return content or ""