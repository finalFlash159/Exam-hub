from pydantic import BaseModel
from typing import Dict, Any

class ExamGenerationRequest(BaseModel):
    """Request model cho việc tạo đề thi"""
    file_id: str
    exam_title: str = "Generated Exam"
    question_count: int = 10

class SaveExamRequest(BaseModel):
    """Request model cho việc lưu đề thi"""
    exam_data: Dict[str, Any]

class ConnectionResponse(BaseModel):
    """Response model cho test connection"""
    status: str
    backend: bool
    gemini: bool
    message: str 