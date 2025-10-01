import json
from typing import Dict, Any
from datetime import datetime
from .base import BaseAIClient


class MockClient(BaseAIClient):
    """Mock client for testing. Returns fake raw response."""

    async def generate_exam(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # Return raw JSON response (like real providers would)
        mock_questions = [
            {
                "question_text": "What is the capital of France?",
                "options": ["Paris", "London", "Berlin", "Madrid"],
                "correct_answer": "A",
                "explanation": "Paris is the capital of France"
            }
        ]

        return {
            "success": True,
            "raw_response": json.dumps(mock_questions),  # Raw JSON string like real API
            "metadata": {
                "ai_provider": "mock",
                "model": "mock-v1.0",
                "generated_at": datetime.now().isoformat(),
            },
            "error": None
        }

    def is_configured(self) -> bool:
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "provider": "mock",
            "model": "mock-v1.0",
            "supports_json": True,
            "supports_streaming": False,
            "max_tokens": 2000,
        }

    async def health_check(self) -> bool:
        return True