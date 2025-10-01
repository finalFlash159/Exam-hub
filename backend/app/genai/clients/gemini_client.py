import os
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from .base import BaseAIClient

try:
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
    from langchain.schema import HumanMessage  # type: ignore
except ImportError:
    ChatGoogleGenerativeAI = None  # type: ignore
    HumanMessage = None  # type: ignore


logger = logging.getLogger(__name__)


class GeminiClient(BaseAIClient):
    """Simple Gemini API wrapper via LangChain. Just calls API, no retry/parsing logic."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> None:
        self.api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.model_name: str = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.default_temperature: float = (
            temperature if temperature is not None
            else float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
        )
        self._llm: Optional[Any] = None

    async def health_check(self) -> bool:
        if not self.is_configured():
            return False
        try:
            self._get_llm()
            return True
        except Exception:
            return False

    async def generate_exam(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Call Gemini API and return raw response."""
        if not self.is_configured():
            return {
                "success": False,
                "raw_response": "",
                "metadata": {
                    "ai_provider": "gemini",
                    "model": self.model_name,
                    "generated_at": datetime.now().isoformat(),
                },
                "error": "Gemini API key not configured"
            }

        temperature = float(kwargs.get("temperature", self.default_temperature))

        try:
            response_text = await self._call_api(prompt, temperature)

            return {
                "success": True,
                "raw_response": response_text,
                "metadata": {
                    "ai_provider": "gemini",
                    "model": self.model_name,
                    "temperature": temperature,
                    "generated_at": datetime.now().isoformat(),
                },
                "error": None
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            return {
                "success": False,
                "raw_response": "",
                "metadata": {
                    "ai_provider": "gemini",
                    "model": self.model_name,
                    "generated_at": datetime.now().isoformat(),
                },
                "error": str(e)
            }

    def is_configured(self) -> bool:
        return bool(self.api_key) and ChatGoogleGenerativeAI is not None

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "provider": "gemini",
            "model": self.model_name,
            "supports_json": True,
            "supports_streaming": False,
            "max_tokens": 8192,
        }

    # Private methods
    def _get_llm(self) -> Any:
        """Lazy init LangChain Gemini client."""
        if self._llm is None:
            if ChatGoogleGenerativeAI is None:
                raise RuntimeError("LangChain Google GenAI not installed")
            self._llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=self.default_temperature,
            )
        return self._llm

    async def _call_api(self, prompt: str, temperature: float) -> str:
        """Call Gemini API via LangChain."""
        llm = self._get_llm()
        messages = [HumanMessage(content=prompt)] if HumanMessage else [prompt]

        # Use async if available
        if hasattr(llm, "ainvoke"):
            response = await llm.ainvoke(messages)
        else:
            response = llm.invoke(messages)

        content = getattr(response, "content", "")
        return content or ""