"""
Integration test for ExamService with GenAIService
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.exam_service import ExamService
from app.genai.service import GenAIService
from app.schemas.exam_schemas import ExamGenerationRequest


# setup test class
class TestExamServiceIntegration:

    def setup_method(self):
        self.mock_db_session = MagicMock()
        self.mock_genai_service = MagicMock(spec=GenAIService)
        self.exam_service = ExamService(
            db_session=self.mock_db_session,
            genai_service=self.mock_genai_service
        )
    
    @pytest.mark.asyncio
    async def test_generate_exam_from_text_success(self):
        """Test generate exam thành công."""
        # ARRANGE: Chuẩn bị data
        file_content = "Python is a programming language. " * 10  # Đủ dài (>100 chars)
        
        # Mock GenAIService trả về response giả
        mock_response = {
            'success': True,
            'questions': [
                {
                    'question_text': 'What is Python?',
                    'options': ['A. Language', 'B. Snake', 'C. Tool', 'D. Framework'],
                    'correct_answer': 'A',
                    'explanation': 'Python is a programming language'
                }
            ],
            'error': None
        }
        self.mock_genai_service.generate_exam = AsyncMock(return_value=mock_response)
        
        # ACT: Gọi method
        result = await self.exam_service.generate_exam_from_text(
            file_content=file_content,
            num_questions=1,
            subject="Python"
        )
        
        # ASSERT: Kiểm tra kết quả
        assert result is not None  # Kết quả không được None

        # Check structure (kiểm tra có đủ keys không)
        assert 'message' in result  # Phải có message
        assert 'exam_data' in result  # Phải có exam_data
        assert 'metadata' in result  # Phải có metadata

        # Check exam_data bên trong
        assert 'title' in result['exam_data']  # exam_data phải có title
        assert 'questions' in result['exam_data']  # exam_data phải có questions

        # Check questions
        questions = result['exam_data']['questions']
        assert isinstance(questions, list)  # questions phải là list
        assert len(questions) > 0  # questions phải có ít nhất 1 câu

        # Check question structure (kiểm tra câu hỏi đầu tiên)
        first_question = questions[0]
        assert 'question_text' in first_question  # Phải có text
        assert 'options' in first_question  # Phải có options
        assert 'correct_answer' in first_question  # Phải có đáp án đúng
        assert 'explanation' in first_question  # Phải có giải thích

        # Check metadata
        metadata = result['metadata']
        assert metadata['source_type'] == 'text_content'  # Check giá trị cụ thể
        assert metadata['questions_generated'] == len(questions)  # Số câu phải khớp

    @pytest.mark.asyncio
    async def test_generate_exam_with_short_content_raises_error(self):
        """Test với content quá ngắn phải raise ValueError."""
        # ARRANGE: Content < 100 chars
        file_content = "Short content"  # Chỉ 13 ký tự

        # ACT & ASSERT: Expect raise ValueError
        with pytest.raises(ValueError, match="Insufficient content"):
            await self.exam_service.generate_exam_from_text(
                file_content=file_content,
                num_questions=1
            )

    @pytest.mark.asyncio
    async def test_generate_exam_when_genai_returns_error(self):
        """Test khi GenAIService trả về error."""
        # ARRANGE
        file_content = "Python programming content. " * 10

        # Mock GenAIService trả về error
        mock_response = {
            'success': False,
            'questions': [],
            'error': 'API rate limit exceeded'
        }
        self.mock_genai_service.generate_exam = AsyncMock(return_value=mock_response)

        # ACT & ASSERT: Expect raise Exception
        with pytest.raises(Exception, match="API rate limit exceeded"):
            await self.exam_service.generate_exam_from_text(
                file_content=file_content,
                num_questions=5
            )

    @pytest.mark.asyncio
    async def test_generate_exam_passes_parameters_correctly(self):
        """Test ExamService truyền đúng parameters xuống GenAIService."""
        # ARRANGE
        file_content = "Test content for parameter verification. " * 5

        # Mock response
        mock_response = {
            'success': True,
            'questions': [
                {
                    'question_text': 'Test question?',
                    'options': ['A. One', 'B. Two', 'C. Three', 'D. Four'],
                    'correct_answer': 'A',
                    'explanation': 'Test explanation'
                }
            ],
            'error': None
        }
        self.mock_genai_service.generate_exam = AsyncMock(return_value=mock_response)

        # ACT: Gọi với nhiều parameters
        await self.exam_service.generate_exam_from_text(
            file_content=file_content,
            num_questions=10,
            subject="Mathematics",
            ai_provider="openai",
            temperature=0.8,
            max_tokens=2000,
            language="vi",
            difficulty="hard"
        )

        # ASSERT: Verify mock được gọi với đúng parameters
        self.mock_genai_service.generate_exam.assert_called_once()

        # Lấy arguments được truyền vào mock
        call_args = self.mock_genai_service.generate_exam.call_args
        request_arg = call_args[0][0]  # Argument đầu tiên là ExamGenerationRequest

        # Verify các fields trong request
        assert request_arg.content == file_content
        assert request_arg.question_count == 10
        assert request_arg.subject == "Mathematics"
        assert request_arg.ai_provider == "openai"
        assert request_arg.temperature == 0.8
        assert request_arg.max_tokens == 2000
        assert request_arg.language == "vi"
        assert request_arg.difficulty == "hard"