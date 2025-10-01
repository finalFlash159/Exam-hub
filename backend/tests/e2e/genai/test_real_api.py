"""
E2E tests with Real API (OpenAI and Gemini).

These tests call actual APIs and cost money.
Run with: pytest tests/genai/e2e/ -v -s
Skip with: pytest -m "not e2e"
"""

import pytest
import os
from app.genai.service import GenAIService
from app.schemas.exam_schemas import ExamGenerationRequest


# Mark all tests in this module as e2e
pytestmark = pytest.mark.e2e


class TestRealAPIOpenAI:
    """E2E tests với OpenAI API thật."""

    def setup_method(self):
        """Setup trước mỗi test."""
        # Verify API key exists
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not found in environment")

        self.service = GenAIService()

    @pytest.mark.asyncio
    async def test_generate_exam_with_openai(self):
        """Test generate exam với OpenAI API thật."""
        print("\n🔄 Calling OpenAI API (this will take a few seconds)...")

        # ARRANGE: Tạo request với content ngắn để tiết kiệm tokens
        request = ExamGenerationRequest(
            content="Python is a high-level programming language known for its simplicity and readability. "
                   "It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            question_count=2,  # Chỉ 2 câu để tiết kiệm
            ai_provider="openai",
            subject="Python Programming",
            language="en",
            difficulty="easy",
            temperature=0.7
        )

        # ACT: Gọi API thật
        result = await self.service.generate_exam(request)

        # ASSERT: Check response structure
        assert result is not None, "Result should not be None"
        assert result["success"] is True, f"Should succeed, but got error: {result.get('error')}"
        assert result["error"] is None, f"Error should be None, got: {result['error']}"

        # Check questions
        questions = result["questions"]
        assert isinstance(questions, list), "Questions should be a list"
        assert len(questions) > 0, "Should have at least 1 question"

        print(f"✅ Generated {len(questions)} questions from OpenAI")

        # Check first question structure
        first_q = questions[0]
        assert "question_text" in first_q, "Missing question_text"
        assert "options" in first_q, "Missing options"
        assert "correct_answer" in first_q, "Missing correct_answer"
        assert "explanation" in first_q, "Missing explanation"

        # Verify question quality
        assert len(first_q["question_text"]) > 10, "Question text too short"
        assert len(first_q["options"]) == 4, "Should have 4 options"
        assert first_q["correct_answer"] in ["A", "B", "C", "D"], "Invalid answer format"

        print(f"📝 Sample question: {first_q['question_text'][:80]}...")

        # Check metadata
        metadata = result["metadata"]
        assert metadata["ai_provider"] == "openai", "Wrong provider in metadata"
        assert metadata["requested_questions"] == 2, "Wrong question count in metadata"
        assert "generated_at" in metadata, "Missing generated_at timestamp"

        print(f"📊 Metadata: provider={metadata['ai_provider']}, questions={metadata['requested_questions']}")


class TestRealAPIGemini:
    """E2E tests với Gemini API thật."""

    def setup_method(self):
        """Setup trước mỗi test."""
        # Verify API key exists
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not found in environment")

        self.service = GenAIService()

    @pytest.mark.asyncio
    async def test_generate_exam_with_gemini(self):
        """Test generate exam với Gemini API thật."""
        print("\n🔄 Calling Gemini API (this will take a few seconds)...")

        # ARRANGE: Tạo request với content ngắn
        request = ExamGenerationRequest(
            content="JavaScript is a versatile programming language primarily used for web development. "
                   "It enables interactive web pages and is an essential part of web applications.",
            question_count=2,  # Chỉ 2 câu để tiết kiệm
            ai_provider="gemini",
            subject="JavaScript",
            language="en",
            difficulty="medium",
            temperature=0.7
        )

        # ACT: Gọi API thật
        result = await self.service.generate_exam(request)

        # ASSERT: Check response structure
        assert result is not None, "Result should not be None"
        assert result["success"] is True, f"Should succeed, but got error: {result.get('error')}"
        assert result["error"] is None, f"Error should be None, got: {result['error']}"

        # Check questions
        questions = result["questions"]
        assert isinstance(questions, list), "Questions should be a list"
        assert len(questions) > 0, "Should have at least 1 question"

        print(f"✅ Generated {len(questions)} questions from Gemini")

        # Check first question structure
        first_q = questions[0]
        assert "question_text" in first_q, "Missing question_text"
        assert "options" in first_q, "Missing options"
        assert "correct_answer" in first_q, "Missing correct_answer"
        assert "explanation" in first_q, "Missing explanation"

        # Verify question quality
        assert len(first_q["question_text"]) > 10, "Question text too short"
        assert len(first_q["options"]) == 4, "Should have 4 options"
        assert first_q["correct_answer"] in ["A", "B", "C", "D"], "Invalid answer format"

        print(f"📝 Sample question: {first_q['question_text'][:80]}...")

        # Check metadata
        metadata = result["metadata"]
        assert metadata["ai_provider"] == "gemini", "Wrong provider in metadata"
        assert metadata["requested_questions"] == 2, "Wrong question count in metadata"
        assert "generated_at" in metadata, "Missing generated_at timestamp"

        print(f"📊 Metadata: provider={metadata['ai_provider']}, questions={metadata['requested_questions']}")


class TestRealAPIErrorHandling:
    """Test error handling với Real APIs."""

    def setup_method(self):
        """Setup trước mỗi test - tạo service mới."""
        # Clear any cached clients to avoid event loop issues
        from app.genai.clients.factory import AIClientFactory
        AIClientFactory.clear_cache()
        self.service = GenAIService()

    @pytest.mark.asyncio
    async def test_generate_exam_with_vietnamese_content(self):
        """Test với content tiếng Việt."""
        print("\n🔄 Testing Vietnamese content with Gemini...")

        request = ExamGenerationRequest(
            content="Python là một ngôn ngữ lập trình bậc cao, được thiết kế với triết lý mã nguồn rõ ràng và dễ đọc. "
                   "Python hỗ trợ nhiều mô hình lập trình khác nhau.",
            question_count=2,
            ai_provider="gemini",
            language="vi",
            difficulty="easy"
        )

        result = await self.service.generate_exam(request)

        assert result["success"] is True, f"Should handle Vietnamese, got error: {result.get('error')}"
        assert len(result["questions"]) > 0, "Should generate questions from Vietnamese content"

        print(f"✅ Successfully generated {len(result['questions'])} questions from Vietnamese content")

    @pytest.mark.asyncio
    async def test_generate_exam_with_different_difficulties(self):
        """Test với các difficulty levels khác nhau."""
        print("\n🔄 Testing different difficulty levels...")

        for difficulty in ["easy", "medium", "hard"]:
            request = ExamGenerationRequest(
                content="Git is a distributed version control system for tracking changes in source code.",
                question_count=1,
                ai_provider="gemini",
                difficulty=difficulty
            )

            result = await self.service.generate_exam(request)

            assert result["success"] is True, f"Failed for difficulty={difficulty}"
            assert len(result["questions"]) > 0, f"No questions for difficulty={difficulty}"

            print(f"✅ Difficulty '{difficulty}' works correctly")
