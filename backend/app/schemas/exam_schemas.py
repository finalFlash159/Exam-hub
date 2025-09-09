from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

class ExamGenerationRequest(BaseModel):
    file_content: str
    num_questions: int = 10
    subject: Optional[str] = None

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

class ExamGenerationResponse(BaseModel):
    questions: List[QuestionResponse]
    subject: Optional[str] = None
    total_questions: int

class SaveExamResponse(BaseModel):
    id: str
    title: str
    message: str = "Exam saved successfully"