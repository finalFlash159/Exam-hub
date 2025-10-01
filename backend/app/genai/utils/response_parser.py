"""
Shared utilities for parsing and normalizing AI responses.

This module extracts common JSON parsing logic used across multiple AI clients
to eliminate code duplication and maintain consistency.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResponseParser:
    """
    Unified response parser for AI-generated exam questions.

    Handles:
    - JSON extraction from markdown-wrapped responses
    - JSON escape sequence fixing
    - Question normalization to unified schema
    """

    @staticmethod
    def parse_json_response(response_text: str) -> List[Dict[str, Any]]:
        """
        Extract and parse JSON array from AI response text.

        Handles common issues:
        - Markdown code fences (```json ... ```)
        - Extra whitespace and text around JSON
        - Malformed escape sequences

        Args:
            response_text: Raw text response from AI provider

        Returns:
            List of parsed question dictionaries

        Raises:
            ValueError: If JSON cannot be parsed after all attempts
        """
        if not response_text or not response_text.strip():
            logger.warning("Empty response text provided")
            return []

        # First attempt: direct JSON parsing
        try:
            data = ResponseParser._extract_json_array(response_text)
            if data:
                return data
        except json.JSONDecodeError:
            pass

        # Second attempt: clean markdown and try again
        try:
            cleaned = ResponseParser._clean_markdown(response_text)
            cleaned = ResponseParser._fix_json_escapes(cleaned)
            data = ResponseParser._extract_json_array(cleaned)
            if data:
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Unable to parse JSON from response: {e}")
            logger.debug(f"Problematic response text: {response_text[:500]}...")
            return []

        logger.error("All JSON parsing attempts failed")
        return []

    @staticmethod
    def _extract_json_array(text: str) -> List[Dict[str, Any]]:
        """
        Extract JSON array from text, handling both standalone and embedded JSON.

        Args:
            text: Text potentially containing JSON array

        Returns:
            Parsed list of dictionaries

        Raises:
            json.JSONDecodeError: If parsing fails
        """
        # Try to find array bounds
        json_start = text.find("[")
        json_end = text.rfind("]") + 1

        if json_start >= 0 and json_end > json_start:
            json_str = text[json_start:json_end]
            data = json.loads(json_str)
        else:
            # Assume entire text is JSON
            data = json.loads(text)

        # Ensure we have a list
        if not isinstance(data, list):
            logger.warning(f"Expected JSON array, got {type(data).__name__}")
            return []

        return data

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """
        Remove markdown code fences and extra formatting.

        Args:
            text: Raw response text

        Returns:
            Cleaned text without markdown
        """
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        return text.strip()

    @staticmethod
    def _fix_json_escapes(text: str) -> str:
        """
        Fix common JSON escape sequence issues in AI responses.

        Args:
            text: JSON text with potentially malformed escapes

        Returns:
            Text with corrected escape sequences
        """
        try:
            fixes = {
                '\\"': '"',
                "\\n": " ",
                "\\r": " ",
                "\\t": " ",
                "\\\\": "\\",
                "\\/": "/",
            }
            for old, new in fixes.items():
                text = text.replace(old, new)

            # Remove invalid escape sequences (keep only valid JSON escapes)
            text = re.sub(r'\\(?![\"\\/bfnrtu])', '', text)
            return text
        except Exception as e:
            logger.warning(f"Error fixing JSON escapes: {e}")
            return text

    @staticmethod
    def normalize_questions(
        questions: List[Dict[str, Any]],
        provider: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """
        Normalize question dictionaries to unified schema.

        Expected output format:
        {
            "question_text": str,
            "options": List[str] (exactly 4 items),
            "correct_answer": str (A/B/C/D),
            "explanation": str
        }

        Args:
            questions: List of raw question dictionaries from AI
            provider: Name of AI provider (for logging)

        Returns:
            List of normalized question dictionaries
        """
        normalized: List[Dict[str, Any]] = []

        for i, q in enumerate(questions):
            try:
                normalized_q = ResponseParser._normalize_single_question(q, i, provider)
                if normalized_q:
                    normalized.append(normalized_q)
            except Exception as exc:
                logger.error(f"[{provider}] Error normalizing question {i}: {exc}")
                continue

        logger.info(f"[{provider}] Normalized {len(normalized)}/{len(questions)} questions")
        return normalized

    @staticmethod
    def _normalize_single_question(
        q: Dict[str, Any],
        index: int,
        provider: str
    ) -> Optional[Dict[str, Any]]:
        """
        Normalize a single question to unified schema.

        Args:
            q: Raw question dictionary
            index: Question index (for logging)
            provider: Provider name (for logging)

        Returns:
            Normalized question dict or None if validation fails
        """
        # Extract question text (try multiple field names)
        question_text = (
            q.get("question_text")
            or q.get("question")
            or q.get("text")
            or q.get("question_content")
        )

        if not question_text or not str(question_text).strip():
            logger.warning(f"[{provider}] Question {index} missing text field")
            return None

        # Extract and normalize options
        options = ResponseParser._normalize_options(q.get("options", []), index, provider)
        if len(options) < 4:
            logger.warning(
                f"[{provider}] Question {index} has insufficient options: {len(options)}/4"
            )
            return None

        # Extract correct answer
        correct_answer = ResponseParser._normalize_answer(
            q.get("correct_answer") or q.get("answer") or "A",
            index,
            provider
        )

        # Extract explanation
        explanation = ResponseParser._normalize_explanation(
            q.get("explanation"),
            index,
            provider
        )

        return {
            "question_text": str(question_text).strip(),
            "options": options[:4],  # Ensure exactly 4 options
            "correct_answer": correct_answer,
            "explanation": explanation,
        }

    @staticmethod
    def _normalize_options(
        raw_options: Any,
        index: int,
        provider: str
    ) -> List[str]:
        """
        Normalize options to list of strings.

        Handles:
        - List of strings: ["option1", "option2", ...]
        - List of dicts: [{"text": "option1"}, {"label": "A", "text": "option2"}, ...]
        - Other formats (log warning and return empty)

        Args:
            raw_options: Raw options from AI response
            index: Question index (for logging)
            provider: Provider name (for logging)

        Returns:
            List of option strings
        """
        if not isinstance(raw_options, list):
            logger.warning(
                f"[{provider}] Question {index} options not a list: {type(raw_options)}"
            )
            return []

        options: List[str] = []

        for opt in raw_options:
            if isinstance(opt, dict):
                # Extract text from dict (try multiple keys)
                text = opt.get("text") or opt.get("content") or opt.get("value") or ""
                options.append(str(text).strip())
            elif isinstance(opt, str):
                options.append(opt.strip())
            else:
                options.append(str(opt).strip())

        # Filter out empty options
        options = [opt for opt in options if opt]
        return options

    @staticmethod
    def _normalize_answer(answer: Any, index: int, provider: str) -> str:
        """
        Normalize correct answer to A/B/C/D format.

        Args:
            answer: Raw answer value (could be "A", "a", 0, "option text", etc.)
            index: Question index (for logging)
            provider: Provider name (for logging)

        Returns:
            Normalized answer (A/B/C/D), defaults to "A" if invalid
        """
        answer_str = str(answer).strip().upper()

        # Handle numeric indices (0-3 -> A-D)
        if answer_str.isdigit():
            num = int(answer_str)
            if 0 <= num <= 3:
                return chr(65 + num)  # 0->A, 1->B, etc.

        # Handle letter format
        if len(answer_str) == 1 and answer_str in ["A", "B", "C", "D"]:
            return answer_str

        # Invalid format - default to A and log warning
        logger.warning(
            f"[{provider}] Question {index} has invalid answer format: '{answer}', "
            f"defaulting to 'A'"
        )
        return "A"

    @staticmethod
    def _normalize_explanation(
        explanation: Any,
        index: int,
        provider: str
    ) -> str:
        """
        Normalize explanation to string.

        Handles:
        - String: return as-is
        - Dict with locale keys: extract first available
        - None/empty: return empty string

        Args:
            explanation: Raw explanation value
            index: Question index (for logging)
            provider: Provider name (for logging)

        Returns:
            Normalized explanation string
        """
        if explanation is None:
            return ""

        if isinstance(explanation, dict):
            # Try common locale keys
            for key in ["en", "vi", "text", "content"]:
                if key in explanation and explanation[key]:
                    return str(explanation[key]).strip()
            return ""

        return str(explanation).strip()