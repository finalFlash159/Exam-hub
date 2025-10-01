import logging
from typing import Any, Dict, Optional
from datetime import datetime

from app.genai.prompts.loader import render as render_prompt
from app.genai.clients.factory import AIClientFactory
from app.genai.utils.response_parser import ResponseParser
from app.genai.utils.retry import retry_with_backoff, OPENAI_RETRY_CONFIG, GEMINI_RETRY_CONFIG
from app.schemas.exam_schemas import ExamGenerationRequest, AIProvider


logger = logging.getLogger(__name__)


class GenAIService:
    """
    Service layer for AI-powered exam generation.

    Responsibilities:
    - Render prompts from YAML templates
    - Get/cache AI clients from factory
    - Execute API calls with retry logic
    - Parse and normalize responses
    - Handle errors and validation
    """

    def __init__(self) -> None:
        self.parser = ResponseParser()
        logger.info("GenAIService initialized")

    async def generate_exam(
        self,
        request: ExamGenerationRequest,
        *,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate exam questions from content.

        This method orchestrates the entire generation flow:
        1. Render prompt from YAML
        2. Get cached client from factory
        3. Call API with retry logic
        4. Parse and normalize response
        5. Return structured result

        Args:
            request: ExamGenerationRequest with content, settings, etc.
            language: Optional locale override

        Returns:
            {
                "success": bool,
                "questions": List[Dict],  # Normalized questions
                "metadata": Dict,
                "error": str | None
            }
        """
        provider_name = (request.ai_provider or "gemini").lower()

        try:
            # Step 1: Render prompt from YAML templates
            prompt, provider_cfg, required_fields = render_prompt(
                template_key="exam_generation",
                provider=provider_name,
                locale=(language or request.language or ""),
                variables={
                    "content": request.content,
                    "question_count": int(request.question_count),
                },
            )

            # Step 2: Get cached client from factory
            provider_enum = AIProvider(provider_name)
            client = AIClientFactory.create_client(provider_enum, use_cache=True)

            # Step 3: Prepare call parameters
            call_params: Dict[str, Any] = {}
            yaml_params = provider_cfg.get("params") or {}
            call_params.update(yaml_params)

            if request.temperature is not None:
                call_params["temperature"] = float(request.temperature)
            if request.max_tokens is not None:
                call_params["max_tokens"] = int(request.max_tokens)

            # Step 4: Call API with retry logic (handled here, not in client)
            retry_config = self._get_retry_config(provider_name)
            raw_result = await retry_with_backoff(
                client.generate_exam,
                prompt,
                config=retry_config,
                context=f"{provider_name} generation",
                **call_params
            )

            # Step 5: Check if API call succeeded
            if not raw_result.get("success"):
                return {
                    "success": False,
                    "questions": [],
                    "metadata": raw_result.get("metadata", {}),
                    "error": raw_result.get("error", "Unknown error from AI provider")
                }

            # Step 6: Parse and normalize raw response
            raw_response = raw_result.get("raw_response", "")
            questions = self._parse_and_normalize(raw_response, provider_name)

            if not questions:
                return {
                    "success": False,
                    "questions": [],
                    "metadata": raw_result.get("metadata", {}),
                    "error": "Failed to parse valid questions from AI response"
                }

            # Step 7: Build final response with enriched metadata
            metadata = raw_result.get("metadata", {}) or {}
            metadata.update({
                "subject": request.subject,
                "requested_questions": request.question_count,
                "total_questions": len(questions),
                "requested_provider": provider_name,
                "generated_at": metadata.get("generated_at") or datetime.now().isoformat(),
            })

            return {
                "success": True,
                "questions": questions,
                "metadata": metadata,
                "error": None
            }

        except Exception as exc:
            logger.error(f"GenAIService error: {exc}", exc_info=True)
            return {
                "success": False,
                "questions": [],
                "metadata": {
                    "ai_provider": provider_name,
                    "generated_at": datetime.now().isoformat(),
                },
                "error": str(exc),
            }

    def _get_retry_config(self, provider: str):
        """Get retry config based on provider."""
        if provider == "openai":
            return OPENAI_RETRY_CONFIG
        elif provider == "gemini":
            return GEMINI_RETRY_CONFIG
        else:
            from app.genai.utils.retry import DEFAULT_RETRY_CONFIG
            return DEFAULT_RETRY_CONFIG

    def _parse_and_normalize(self, raw_response: str, provider: str) -> list:
        """Parse raw JSON response and normalize to unified schema."""
        try:
            # Parse JSON from response (handles markdown wrappers, etc.)
            raw_questions = self.parser.parse_json_response(raw_response)

            # Normalize to unified schema
            normalized = self.parser.normalize_questions(raw_questions, provider=provider)

            return normalized

        except Exception as e:
            logger.error(f"Error parsing response from {provider}: {e}")
            return []