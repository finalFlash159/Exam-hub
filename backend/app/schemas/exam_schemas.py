from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ExamGenerationRequest(BaseModel):
    # Core fields (existing)
    content: str  # Renamed from file_content
    question_count: int = 10  # Renamed from num_questions
    subject: Optional[str] = None
    language: Optional[str] = "vi"
    
    # GenAI fields (new)
    exam_title: Optional[str] = None
    difficulty: str = "medium"  # gemini, openai, mock
    ai_provider: str = "gemini"  # gemini, openai, mock
    question_types: List[str] = ["multiple_choice"]  # gemini, openai, mock
    
    # Advanced options (new)
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = None

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v not in ['easy', 'medium', 'hard']:
            raise ValueError("Difficulty must be easy, medium, or hard")
        return v

    @field_validator('ai_provider')
    @classmethod
    def validate_ai_provider(cls, v):
        if v not in ['openai', 'gemini', 'mock']:
            raise ValueError("AI provider must be openai, gemini, or mock")
        return v

class SaveExamRequest(BaseModel):
    title: str
    questions: List[dict]
    description: Optional[str] = None
    duration_minutes: Optional[int] = 30

class QuestionResponse(BaseModel):
    """Single question response for 4-choice multiple choice"""
    question_text: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None

    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError("Must have exactly 4 options")
        return v
    
    @field_validator('correct_answer')
    @classmethod
    def validate_correct_answer(cls, v):
        if v not in ['A', 'B', 'C', 'D']:
            raise ValueError("Correct answer must be A, B, C, or D")
        return v


class ExamMetadata(BaseModel):
    total_questions: int
    difficulty: str
    estimated_duration: int  # minutes
    ai_provider: str
    generated_at: datetime
    usage: Optional[Dict[str, Any]] = None  # tokens, cost

class ExamGenerationResponse(BaseModel):
    success: bool
    questions: List[QuestionResponse]
    metadata: ExamMetadata
    error: Optional[str] = None

class SaveExamResponse(BaseModel):
    id: str
    title: str
    message: str = "Exam saved successfully"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"

class AIProvider(str, Enum):  # Move from genai/clients/base.py
    OPENAI = "openai"
    GEMINI = "gemini"
    MOCK = "mock"

