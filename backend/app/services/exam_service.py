"""
Exam Service
Business logic for exam generation and management
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.document_processor import DocumentProcessor
from app.utils.ai_generator import ExamGenerator
from app.repositories.exam_repository import ExamRepository

logger = logging.getLogger(__name__)


class ExamService:
    """Service for handling exam-related business logic"""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize service with required dependencies"""
        self.db_session = db_session
        self.exam_repository = ExamRepository(db_session)
        self.document_processor = DocumentProcessor()
        self.ai_generator = ExamGenerator()
        logger.info("ExamService initialized")
    
    async def generate_exam_from_text(
        self, 
        file_content: str,
        num_questions: int = 10,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate exam questions directly from text content
        
        Args:
            file_content: Text content to generate exam from
            num_questions: Number of questions to generate
            subject: Optional subject/topic for better context
            
        Returns:
            Dict containing exam data and metadata
            
        Raises:
            ValueError: If content is insufficient
            Exception: For other generation errors
        """
        logger.info(f"Generate exam from text - questions: {num_questions}, subject: {subject}")
        
        # Validate content length
        text_length = len(file_content.strip())
        if text_length < 100:
            logger.warning(f"Text too short: {text_length} characters")
            raise ValueError("Insufficient content to generate questions")
        
        logger.info(f"Processing {text_length} characters of text content")
        
        # Generate exam using AI
        logger.info("Starting exam generation with LLM...")
        exam_title = subject or "Generated Exam"
        
        exam_data = await self.ai_generator.generate_from_text_async(
            file_content, 
            exam_title, 
            num_questions
        )
        
        # Validate generation result
        if isinstance(exam_data, dict) and "error" in exam_data:
            logger.error(f"LLM generation error: {exam_data['details']}")
            raise Exception(f"Failed to generate questions: {exam_data['details']}")
        
        questions_count = len(exam_data.get('questions', []))
        logger.info(f"Successfully generated {questions_count} questions")
        
        # Return structured response
        result = {
            'message': 'Exam generated successfully',
            'exam_data': exam_data,
            'metadata': {
                'source_type': 'text_content',
                'text_length': text_length,
                'questions_generated': questions_count,
                'subject': subject,
                'generation_method': 'LLM'
            }
        }
        
        logger.debug("Text-based exam generation completed successfully")
        return result
    
    async def save_exam(self, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save exam to database
        
        Args:
            exam_data: Complete exam data to save
            
        Returns:
            Dict with save result and exam ID
            
        Raises:
            ValueError: If exam data is invalid
            Exception: For save errors
        """
        logger.info("Starting save exam process...")
        
        # Extract exam details
        exam_title = exam_data.get('title', 'Generated Exam')
        description = exam_data.get('description', '')
        questions = exam_data.get('questions', [])
        duration_minutes = exam_data.get('duration_minutes')
        
        logger.info(f"Saving exam: '{exam_title}' with {len(questions)} questions")
        
        # Validate exam data
        if not questions:
            logger.error("No questions provided")
            raise ValueError("No questions to save")
        
        if not exam_title.strip():
            logger.error("No exam title provided")
            raise ValueError("Exam title is required")
        
        # Save to database using repository
        try:
            exam = await self.exam_repository.create_exam_with_questions(
                title=exam_title,
                description=description,
                questions=questions,
                duration_minutes=duration_minutes
            )
            
            logger.info(f"Exam saved successfully with ID: {exam.id}")
            
            # Return save result
            result = {
                'success': True,
                'message': f"Exam '{exam_title}' saved successfully",
                'exam_id': exam.id,
                'metadata': {
                    'questions_count': len(questions),
                    'duration_minutes': duration_minutes,
                    'save_method': 'database'
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error saving exam: {e}")
            raise Exception(f"Failed to save exam: {str(e)}")
    
    async def get_exam_by_id(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """
        Get exam by ID
        
        Args:
            exam_id: ID of exam to retrieve
            
        Returns:
            Exam data if found, None otherwise
        """
        logger.info(f"Getting exam by ID: {exam_id}")
        
        try:
            exam = await self.exam_repository.get_by_id(exam_id)
            if not exam:
                logger.warning(f"Exam not found: {exam_id}")
                return None
            
            logger.info(f"Successfully retrieved exam: {exam.title}")
            return {
                'id': exam.id,
                'title': exam.title,
                'description': exam.description,
                'questions': exam.questions,
                'duration_minutes': exam.duration_minutes,
                'created_at': exam.created_at,
                'is_public': exam.is_public
            }
            
        except Exception as e:
            logger.error(f"Error getting exam {exam_id}: {e}")
            raise Exception(f"Failed to retrieve exam: {str(e)}")
    
    async def list_exams(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        List all available exams
        
        Args:
            skip: Number of exams to skip
            limit: Maximum number of exams to return
            
        Returns:
            List of exam summaries with pagination info
        """
        logger.info(f"Listing exams - skip: {skip}, limit: {limit}")
        
        try:
            exams = await self.exam_repository.list_exams(skip=skip, limit=limit)
            total_count = await self.exam_repository.count_exams()
            
            exam_summaries = [
                {
                    'id': exam.id,
                    'title': exam.title,
                    'description': exam.description,
                    'questions_count': len(exam.questions) if exam.questions else 0,
                    'duration_minutes': exam.duration_minutes,
                    'created_at': exam.created_at,
                    'is_public': exam.is_public
                }
                for exam in exams
            ]
            
            logger.info(f"Successfully retrieved {len(exam_summaries)} exams")
            
            return {
                'exams': exam_summaries,
                'total_count': total_count,
                'skip': skip,
                'limit': limit,
                'has_more': skip + len(exam_summaries) < total_count
            }
            
        except Exception as e:
            logger.error(f"Error listing exams: {e}")
            raise Exception(f"Failed to list exams: {str(e)}")