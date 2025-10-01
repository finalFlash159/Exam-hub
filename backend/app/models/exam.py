"""
Exam-related database models
Defines the structure for exams, questions, and related entities
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, JSON, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel


class DifficultyLevel(str, enum.Enum):
    """Enum for question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium" 
    HARD = "hard"


class ExamStatus(str, enum.Enum):
    """Enum for exam status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Exam(BaseModel):
    """
    Exam model
    Represents a complete exam with metadata
    """
    __tablename__ = "exams"
    
    # Basic info
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creator_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    # Exam settings
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    passing_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status and visibility
    status: Mapped[ExamStatus] = mapped_column(
        SQLEnum(ExamStatus), 
        default=ExamStatus.DRAFT,
        nullable=False
    )
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    source_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    generation_method: Mapped[str] = mapped_column(String(50), default="manual")
    
    # Legacy compatibility
    legacy_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)
    legacy_file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    questions: Mapped[List["Question"]] = relationship(
        "Question", 
        back_populates="exam",
        cascade="all, delete-orphan"
    )
    
    # Creator relationship
    creator: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[creator_id],
        back_populates="created_exams"
    )
    
    def __repr__(self) -> str:
        return f"<Exam(id={self.id}, title='{self.title}', questions={self.total_questions})>"


class Question(BaseModel):
    """
    Question model
    Represents a single question in an exam
    """
    __tablename__ = "questions"
    
    # Foreign key to exam
    exam_id: Mapped[str] = mapped_column(String(36), ForeignKey("exams.id"), nullable=False)
    
    # Question content
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), default="multiple_choice")
    
    # Options (stored as JSON for flexibility)
    options: Mapped[dict] = mapped_column(JSON, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Additional info
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        SQLEnum(DifficultyLevel),
        default=DifficultyLevel.MEDIUM
    )
    
    # Ordering
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Points/scoring
    points: Mapped[int] = mapped_column(Integer, default=1)
    
    # Relationships
    exam: Mapped["Exam"] = relationship("Exam", back_populates="questions")
    
    def __repr__(self) -> str:
        return f"<Question(id={self.id}, exam_id={self.exam_id}, text='{self.question_text[:50]}...')>"


class ExamAttempt(BaseModel):
    """
    Exam attempt model
    Tracks when users attempt exams (for future user system)
    """
    __tablename__ = "exam_attempts"
    
    # Foreign keys
    exam_id: Mapped[str] = mapped_column(String(36), ForeignKey("exams.id"), nullable=False)
    # user_id will be added in Phase 5 when we add authentication
    
    # Attempt data
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Results
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    percentage: Mapped[Optional[float]] = mapped_column(nullable=True)
    passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Answers (stored as JSON)
    answers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="in_progress")
    
    # Relationships
    exam: Mapped["Exam"] = relationship("Exam")
    
    def __repr__(self) -> str:
        return f"<ExamAttempt(id={self.id}, exam_id={self.exam_id}, score={self.score})>" 