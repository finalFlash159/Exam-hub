"""
Exam Repository
Handles database operations for exam-related entities
"""

import logging
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.exam import Exam, Question, ExamAttempt, ExamStatus
from .base import BaseRepository

logger = logging.getLogger(__name__)


class ExamRepository(BaseRepository[Exam]):
    """Repository for exam operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Exam, session)
    
    async def create_exam_with_questions(
        self, 
        exam_data: Dict[str, Any], 
        questions_data: List[Dict[str, Any]]
    ) -> Exam:
        """
        Create exam with questions in a single transaction
        
        Args:
            exam_data: Exam fields
            questions_data: List of question fields
            
        Returns:
            Created exam with questions
        """
        try:
            # Create exam
            exam = await self.create(**exam_data)
            
            # Create questions
            for i, question_data in enumerate(questions_data):
                question_data.update({
                    'exam_id': exam.id,
                    'order_index': i + 1
                })
                question_repo = QuestionRepository(self.session)
                await question_repo.create(**question_data)
            
            # Update total questions count
            exam.total_questions = len(questions_data)
            await self.session.commit()
            
            # Reload with questions
            result = await self.session.execute(
                select(Exam)
                .options(selectinload(Exam.questions))
                .where(Exam.id == exam.id)
            )
            exam_with_questions = result.scalar_one()
            
            self.logger.info(f"Created exam '{exam.title}' with {len(questions_data)} questions")
            return exam_with_questions
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to create exam with questions: {e}")
            raise
    
    async def get_with_questions(self, exam_id: str) -> Optional[Exam]:
        """
        Get exam with all questions loaded
        
        Args:
            exam_id: Exam ID
            
        Returns:
            Exam with questions if found, None otherwise
        """
        try:
            result = await self.session.execute(
                select(Exam)
                .options(selectinload(Exam.questions))
                .where(Exam.id == exam_id)
            )
            exam = result.scalar_one_or_none()
            
            if exam:
                self.logger.debug(f"Found exam '{exam.title}' with {len(exam.questions)} questions")
            
            return exam
            
        except Exception as e:
            self.logger.error(f"Failed to get exam with questions for ID {exam_id}: {e}")
            raise
    
    async def get_by_legacy_id(self, legacy_id: int) -> Optional[Exam]:
        """
        Get exam by legacy ID (for migration compatibility)
        
        Args:
            legacy_id: Legacy exam ID
            
        Returns:
            Exam if found, None otherwise
        """
        try:
            result = await self.session.execute(
                select(Exam).where(Exam.legacy_id == legacy_id)
            )
            exam = result.scalar_one_or_none()
            
            if exam:
                self.logger.debug(f"Found exam by legacy ID {legacy_id}: {exam.title}")
            
            return exam
            
        except Exception as e:
            self.logger.error(f"Failed to get exam by legacy ID {legacy_id}: {e}")
            raise
    
    async def get_published_exams(self, skip: int = 0, limit: int = 100) -> List[Exam]:
        """
        Get published and public exams
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of published exams
        """
        try:
            result = await self.session.execute(
                select(Exam)
                .where(
                    Exam.status == ExamStatus.PUBLISHED,
                    Exam.is_public == True
                )
                .offset(skip)
                .limit(limit)
                .order_by(Exam.created_at.desc())
            )
            exams = result.scalars().all()
            
            self.logger.debug(f"Retrieved {len(exams)} published exams")
            return list(exams)
            
        except Exception as e:
            self.logger.error(f"Failed to get published exams: {e}")
            raise
    
    async def search_by_title(self, title_search: str, limit: int = 20) -> List[Exam]:
        """
        Search exams by title
        
        Args:
            title_search: Search term for title
            limit: Maximum results
            
        Returns:
            List of matching exams
        """
        try:
            result = await self.session.execute(
                select(Exam)
                .where(Exam.title.ilike(f"%{title_search}%"))
                .limit(limit)
                .order_by(Exam.created_at.desc())
            )
            exams = result.scalars().all()
            
            self.logger.debug(f"Found {len(exams)} exams matching title: {title_search}")
            return list(exams)
            
        except Exception as e:
            self.logger.error(f"Failed to search exams by title '{title_search}': {e}")
            raise
    
    async def get_exam_stats(self, exam_id: str) -> Dict[str, Any]:
        """
        Get exam statistics
        
        Args:
            exam_id: Exam ID
            
        Returns:
            Dict with exam statistics
        """
        try:
            # Get exam with questions
            exam = await self.get_with_questions(exam_id)
            if not exam:
                return {}
            
            # Get attempt count
            attempt_result = await self.session.execute(
                select(func.count(ExamAttempt.id))
                .where(ExamAttempt.exam_id == exam_id)
            )
            attempt_count = attempt_result.scalar() or 0
            
            # Calculate average difficulty
            difficulties = [q.difficulty.value for q in exam.questions]
            difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
            avg_difficulty = sum(difficulty_map.get(d, 2) for d in difficulties) / len(difficulties) if difficulties else 2
            
            stats = {
                "id": exam.id,
                "title": exam.title,
                "total_questions": exam.total_questions,
                "total_attempts": attempt_count,
                "duration_minutes": exam.duration_minutes,
                "status": exam.status.value,
                "is_public": exam.is_public,
                "average_difficulty": round(avg_difficulty, 2),
                "created_at": exam.created_at.isoformat(),
                "updated_at": exam.updated_at.isoformat()
            }
            
            self.logger.debug(f"Generated stats for exam: {exam.title}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get exam stats for ID {exam_id}: {e}")
            raise


class QuestionRepository(BaseRepository[Question]):
    """Repository for question operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Question, session)
    
    async def get_by_exam_id(self, exam_id: str) -> List[Question]:
        """
        Get all questions for an exam
        
        Args:
            exam_id: Exam ID
            
        Returns:
            List of questions ordered by order_index
        """
        try:
            result = await self.session.execute(
                select(Question)
                .where(Question.exam_id == exam_id)
                .order_by(Question.order_index)
            )
            questions = result.scalars().all()
            
            self.logger.debug(f"Retrieved {len(questions)} questions for exam {exam_id}")
            return list(questions)
            
        except Exception as e:
            self.logger.error(f"Failed to get questions for exam {exam_id}: {e}")
            raise
    
    async def reorder_questions(self, exam_id: str, question_ids: List[str]) -> bool:
        """
        Reorder questions in an exam
        
        Args:
            exam_id: Exam ID
            question_ids: List of question IDs in new order
            
        Returns:
            True if successful
        """
        try:
            for i, question_id in enumerate(question_ids):
                await self.update(question_id, order_index=i + 1)
            
            self.logger.info(f"Reordered {len(question_ids)} questions for exam {exam_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to reorder questions for exam {exam_id}: {e}")
            raise


class ExamAttemptRepository(BaseRepository[ExamAttempt]):
    """Repository for exam attempt operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(ExamAttempt, session)
    
    async def get_by_exam_id(self, exam_id: str) -> List[ExamAttempt]:
        """
        Get all attempts for an exam
        
        Args:
            exam_id: Exam ID
            
        Returns:
            List of exam attempts
        """
        try:
            result = await self.session.execute(
                select(ExamAttempt)
                .where(ExamAttempt.exam_id == exam_id)
                .order_by(ExamAttempt.created_at.desc())
            )
            attempts = result.scalars().all()
            
            self.logger.debug(f"Retrieved {len(attempts)} attempts for exam {exam_id}")
            return list(attempts)
            
        except Exception as e:
            self.logger.error(f"Failed to get attempts for exam {exam_id}: {e}")
            raise 