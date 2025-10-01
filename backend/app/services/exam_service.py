"""
Exam Service
Business logic for exam generation and management
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.processors.document_processor import DocumentProcessor
from app.genai.service import GenAIService
from app.repositories.exam_repository import ExamRepository

logger = logging.getLogger(__name__)


class ExamService:
    """Service for handling exam-related business logic"""
    
    def __init__(
            self, 
            db_session: AsyncSession,
            genai_service: Optional[GenAIService] = None
            ):
        """Initialize service with required dependencies"""
        self.db_session = db_session
        self.exam_repository = ExamRepository(db_session)
        self.document_processor = DocumentProcessor()
        self.genai_service = genai_service or GenAIService()
        logger.info("ExamService initialized")
    
    async def generate_exam_from_text(
        self,
        file_content: str,
        num_questions: int = 10,
        subject: Optional[str] = None,
        *,
        ai_provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        language: Optional[str] = None,
        difficulty: Optional[str] = None,
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
        
        # Generate exam via GenAIService (YAML + provider factory)
        logger.info("Starting exam generation with GenAIService...")
        from app.schemas.exam_schemas import ExamGenerationRequest
        req = ExamGenerationRequest(
            content=file_content,
            question_count=num_questions,
            subject=subject,
            ai_provider=ai_provider or 'gemini',
            temperature=temperature,
            max_tokens=max_tokens,
            language=language,
            difficulty=difficulty or 'medium',
        )
        gen_result = await self.genai_service.generate_exam(req)

        if not gen_result.get('success'):
            error_msg = gen_result.get('error') or 'Generation failed'
            logger.error(f"GenAIService error: {error_msg}")
            raise Exception(error_msg)

        questions = gen_result.get('questions', [])
        questions_count = len(questions)
        logger.info(f"Successfully generated {questions_count} questions")

        result = {
            'message': 'Exam generated successfully',
            'exam_data': {
                'title': subject or 'Generated Exam',
                'questions': questions,
            },
            'metadata': {
                'source_type': 'text_content',
                'text_length': text_length,
                'questions_generated': questions_count,
                'subject': subject,
                'generation_method': 'GenAIService'
            }
        }

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
        creator_id = exam_data.get('creator_id')
        
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
            exam_data = {
                'title': exam_title,
                'description': description,
                'duration_minutes': duration_minutes,
                'creator_id': creator_id
            }

            exam = await self.exam_repository.create_exam_with_questions(
                exam_data=exam_data,
                questions_data=questions
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


    async def list_user_exams(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all exams created by specific user (SECURE)
        
        Args:
            user_id: ID of the user (REQUIRED)
            
        Returns:
            List of user's exams ONLY
        """
        logger.info(f"Listing exams for user: {user_id}")
        
        try:
            # ALWAYS filter by user - no optional logic
            exams = await self.exam_repository.get_exams_by_creator(user_id)
            
            result = []
            for exam in exams:
                result.append({
                    'id': exam.id,
                    'title': exam.title,
                    'description': exam.description,
                    'duration_minutes': exam.duration_minutes,
                    'total_questions': exam.total_questions,
                    'is_public': exam.is_public,
                    'status': exam.status,
                    'created_at': exam.created_at.isoformat() if exam.created_at else None,
                    'updated_at': exam.updated_at.isoformat() if exam.updated_at else None
                })
            
            logger.info(f"Found {len(result)} exams for user: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error listing exams for user {user_id}: {e}")
            raise ValueError(f"Failed to list user exams: {str(e)}")
    
    async def list_all_exams_admin(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get ALL exams (ADMIN ONLY)
        
        Args:
            skip: Number of records to skip  
            limit: Maximum number of records
            
        Returns:
            List of ALL exams (admin access)
        """
        logger.info("Admin listing all exams")
        
        try:
            exams = await self.exam_repository.get_all_exams(skip, limit)
            
            result = []
            for exam in exams:
                result.append({
                    'id': exam.id,
                    'title': exam.title,
                    'description': exam.description,
                    'creator_id': exam.creator_id,  # Include creator info for admin
                    'duration_minutes': exam.duration_minutes,
                    'total_questions': exam.total_questions,
                    'is_public': exam.is_public,
                    'status': exam.status,
                    'created_at': exam.created_at.isoformat() if exam.created_at else None,
                    'updated_at': exam.updated_at.isoformat() if exam.updated_at else None
                })
            
            logger.info(f"Found {len(result)} total exams for admin")
            return result
            
        except Exception as e:
            logger.error(f"Error listing all exams for admin: {e}")
            raise ValueError(f"Failed to list all exams: {str(e)}")