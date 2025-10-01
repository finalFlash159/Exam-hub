import pytest
from app.genai.utils.response_parser import ResponseParser


class TestResponseParser:
    """Test JSON parsing và normalization."""

    def setup_method(self):
        self.parser = ResponseParser()

    # ========== Test Group 1: JSON Parsing ==========

    def test_parse_clean_json_array(self):
        """Test case cơ bản: JSON array sạch sẽ."""

        # ARRANGE: Prepare input
        json_str = '''[
            {
                "question_text": "What is 2+2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "B",
                "explanation": "Basic math"
            }
        ]'''

        # ACT: Parse
        result = self.parser.parse_json_response(json_str)

        # ASSERT: Verify
        assert len(result) == 1
        assert result[0]["question_text"] == "What is 2+2?"
        assert len(result[0]["options"]) == 4
        assert result[0]["correct_answer"] == "B"

    def test_parse_markdown_wrapped_json(self):
        """AI models thường wrap JSON trong markdown code blocks."""

        json_str = '''```json
        [
            {
                "question_text": "Test question",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A"
            }
        ]
        ```'''

        # Parser phải tự remove ``` wrapper
        result = self.parser.parse_json_response(json_str)

        assert len(result) == 1
        assert result[0]["question_text"] == "Test question"

    def test_parse_json_with_surrounding_text(self):
        """AI có thể thêm text explanation xung quanh JSON."""

        json_str = '''Here are your exam questions as requested:

        [{"question_text": "Q1", "options": ["A","B","C","D"], "correct_answer": "A"}]

        I hope these questions meet your requirements!'''

        # Parser tìm [...] trong text
        result = self.parser.parse_json_response(json_str)

        assert len(result) == 1

    def test_parse_empty_string(self):
        """Empty input → empty list (không crash)."""

        result = self.parser.parse_json_response("")

        assert result == []

    def test_parse_invalid_json(self):
        """Malformed JSON → empty list (không crash)."""

        result = self.parser.parse_json_response("{invalid: json: here")

        assert result == []

    def test_parse_non_array_json(self):
        """Nếu không phải array → return empty."""

        json_str = '{"single": "object"}'

        result = self.parser.parse_json_response(json_str)

        assert result == []

    # ========== Test Group 2: Question Normalization ==========

    def test_normalize_with_string_options(self):
        """Options là list of strings (format phổ biến nhất)."""

        questions = [{
            "question_text": "Capital of France?",
            "options": ["Paris", "London", "Berlin", "Madrid"],
            "correct_answer": "A",
            "explanation": "Paris is correct"
        }]

        normalized = self.parser.normalize_questions(questions, provider="test")

        assert len(normalized) == 1
        q = normalized[0]
        assert q["question_text"] == "Capital of France?"
        assert q["options"] == ["Paris", "London", "Berlin", "Madrid"]
        assert q["correct_answer"] == "A"
        assert q["explanation"] == "Paris is correct"

    def test_normalize_with_dict_options(self):
        """Options là list of dicts với label + text."""

        questions = [{
            "question_text": "Q1",
            "options": [
                {"label": "A", "text": "Answer A"},
                {"label": "B", "text": "Answer B"},
                {"label": "C", "text": "Answer C"},
                {"label": "D", "text": "Answer D"}
            ],
            "correct_answer": "A"
        }]

        normalized = self.parser.normalize_questions(questions, provider="test")

        # Chỉ extract text, drop labels
        assert normalized[0]["options"] == ["Answer A", "Answer B", "Answer C", "Answer D"]

    def test_normalize_answer_uppercase(self):
        """Lowercase answer → uppercase."""
        q = {"question_text": "Q", "options": ["A","B","C","D"], "correct_answer": "a"}
        normalized = self.parser.normalize_questions([q], "test")
        assert normalized[0]["correct_answer"] == "A"

    def test_normalize_answer_index_to_letter(self):
        """Numeric index → letter (0=A, 1=B, etc)."""
        test_cases = [
            (0, "A"),
            (1, "B"),
            (2, "C"),
            (3, "D"),
        ]

        for index, expected_letter in test_cases:
            q = {"question_text": "Q", "options": ["A","B","C","D"], "correct_answer": index}
            normalized = self.parser.normalize_questions([q], "test")
            assert normalized[0]["correct_answer"] == expected_letter

    def test_normalize_invalid_answer_defaults_to_a(self):
        """Invalid answer → default A."""
        q = {"question_text": "Q", "options": ["A","B","C","D"], "correct_answer": "invalid"}
        normalized = self.parser.normalize_questions([q], "test")
        assert normalized[0]["correct_answer"] == "A"

    def test_filter_missing_text(self):
        """Question without text → filtered out."""
        questions = [
            {"question_text": "Valid", "options": ["A","B","C","D"], "correct_answer": "A"},
            {"question_text": "", "options": ["A","B","C","D"], "correct_answer": "A"},  # Invalid
        ]

        normalized = self.parser.normalize_questions(questions, "test")

        assert len(normalized) == 1

    def test_filter_insufficient_options(self):
        """Question với < 4 options → filtered."""
        questions = [
            {"question_text": "Valid", "options": ["A","B","C","D"], "correct_answer": "A"},
            {"question_text": "Invalid", "options": ["A","B"], "correct_answer": "A"},  # Only 2
        ]

        normalized = self.parser.normalize_questions(questions, "test")

        assert len(normalized) == 1

    def test_limit_to_4_options(self):
        """Nếu > 4 options → chỉ lấy 4 đầu."""
        q = {"question_text": "Q", "options": ["A","B","C","D","E","F"], "correct_answer": "A"}
        normalized = self.parser.normalize_questions([q], "test")
        assert len(normalized[0]["options"]) == 4

    def test_normalize_explanation_string(self):
        """Explanation là string → keep as-is."""
        q = {"question_text": "Q", "options": ["A","B","C","D"], "correct_answer": "A", "explanation": "Simple text"}
        normalized = self.parser.normalize_questions([q], "test")
        assert normalized[0]["explanation"] == "Simple text"

    def test_normalize_explanation_dict(self):
        """Explanation là dict (multi-language) → extract first available."""
        q = {
            "question_text": "Q",
            "options": ["A","B","C","D"],
            "correct_answer": "A",
            "explanation": {"en": "English", "vi": "Tiếng Việt"}
        }
        normalized = self.parser.normalize_questions([q], "test")
        # Should extract "en" first
        assert normalized[0]["explanation"] in ["English", "Tiếng Việt"]

    def test_normalize_missing_explanation(self):
        """Không có explanation → empty string."""
        q = {"question_text": "Q", "options": ["A","B","C","D"], "correct_answer": "A"}
        normalized = self.parser.normalize_questions([q], "test")
        assert normalized[0]["explanation"] == ""