import logging
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.exam import Exam, Question, ExamAttempt
from .base import BaseRepository

logger = logging.getLogger(__name__)


class ExamRepository(BaseRepository[Exam]):
    """Repository for exam operations with clean architecture"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Exam, session)
    
    async def get_by_id(self, id: str) -> Optional[Exam]:
        """
        Get exam by ID with questions loaded
        Override base method to include relationship loading
        """
        try:
            result = await self.session.execute(
                select(Exam)
                .options(selectinload(Exam.questions))
                .where(Exam.id == id)
            )
            instance = result.scalar_one_or_none()
            
            if instance:
                self.logger.debug(f"Found exam '{instance.title}' with {len(instance.questions)} questions")
            else:
                self.logger.debug(f"No exam found with ID: {id}")
                
            return instance
            
        except Exception as e:
            self.logger.error(f"Error getting exam by ID {id}: {e}")
            raise
    
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
            Created exam with questions loaded
        """
        try:
            # Create exam
            exam = await self.create(**exam_data)
            
            # Create questions
            question_repo = QuestionRepository(self.session)
            for i, question_data in enumerate(questions_data):
                question_data.update({
                    'exam_id': exam.id,
                    'order_index': i + 1
                })
                await question_repo.create(**question_data)
            
            # Update total questions count
            exam.total_questions = len(questions_data)
            await self.session.commit()
            
            # Return exam with questions loaded
            return await self.get_by_id(exam.id)
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to create exam with questions: {e}")
            raise
    
    async def get_exams_by_creator(self, creator_id: str) -> List[Exam]:
        """
        Get exams created by specific user (SECURE - user-scoped)
        
        Args:
            creator_id: ID of the exam creator (REQUIRED)
            
        Returns:
            List of exams created by the user ONLY
        """
        try:
            result = await self.session.execute(
                select(Exam)
                .where(Exam.creator_id == creator_id)  # ALWAYS filter by user
                .order_by(Exam.created_at.desc())
            )
            exams = result.scalars().all()
            
            self.logger.debug(f"Found {len(exams)} exams for creator: {creator_id}")
            return list(exams)
            
        except Exception as e:
            self.logger.error(f"Failed to get exams for creator {creator_id}: {e}")
            raise
    
    async def get_all_exams(self, skip: int = 0, limit: int = 100) -> List[Exam]:
        """
        Get ALL exams (ADMIN ONLY - no user filtering)
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of ALL exams (admin access)
        """
        try:
            result = await self.session.execute(
                select(Exam)
                .offset(skip)
                .limit(limit)
                .order_by(Exam.created_at.desc())
            )
            exams = result.scalars().all()
            
            self.logger.debug(f"Retrieved {len(exams)} exams for admin (skip={skip}, limit={limit})")
            return list(exams)
            
        except Exception as e:
            self.logger.error(f"Failed to list all exams: {e}")
            raise
    
    async def count_exams(self) -> int:
        """
        Count total number of exams
        
        Returns:
            Total exam count
        """
        try:
            result = await self.session.execute(
                select(func.count(Exam.id))
            )
            count = result.scalar() or 0
            
            self.logger.debug(f"Total exam count: {count}")
            return count
            
        except Exception as e:
            self.logger.error(f"Failed to count exams: {e}")
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