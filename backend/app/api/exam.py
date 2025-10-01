from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database.connection import get_db_session
from ..services.exam_service import ExamService
from ..schemas.exam_schemas import (
    ExamGenerationRequest, SaveExamRequest,
    QuestionResponse, ExamGenerationResponse,
    SaveExamResponse
)
from app.core.rate_limit import (
    rate_limit_exam_generation,
    rate_limit_general,
    rate_limit_read_only,
)
from ..auth import CurrentUser, require_exam_access, AdminUser  
from ..models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/exam", tags=["exam"])

@router.post("/generate", response_model=ExamGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_exam(
    request: ExamGenerationRequest,
    current_user: User = CurrentUser, 
    db: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(rate_limit_exam_generation()),
):
    """
    Generate exam questions from document content
    🔒 REQUIRES AUTHENTICATION
    """
    try:
        logger.info(f"User {current_user.email} generating exam for subject: {request.subject}")
        
        # initialize exam service
        exam_service = ExamService(db)

        # generate exam via GenAI pipeline
        result = await exam_service.generate_exam_from_text(
            file_content=request.content,
            num_questions=request.question_count,
            subject=request.subject,
            ai_provider=request.ai_provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            language=request.language,
            difficulty=request.difficulty,
        )

        # Extract exam data 
        exam_data = result.get('exam_data')
        questions = exam_data.get('questions', [])

        question_response = []
        for q in questions:
            question_response.append(QuestionResponse(
                question_text=q.get('question_text', ''),
                options=q.get('options', []),
                correct_answer=q.get('correct_answer', ''),
                explanation=q.get('explanation')
            ))
        
        return ExamGenerationResponse(
            success=True,
            questions=question_response,
            metadata={
                'total_questions': len(question_response),
                'difficulty': request.difficulty or 'medium',
                'estimated_duration': 10,
                'ai_provider': request.ai_provider,
                'generated_at': __import__('datetime').datetime.now().isoformat(),
                'usage': None
            },
            error=None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Error generating exam for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/save", response_model=SaveExamResponse, status_code=status.HTTP_201_CREATED)
async def save_exam(
    request: SaveExamRequest,
    current_user: User = CurrentUser,
    db: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(rate_limit_general()),
):
    """
    Save exam to database
    🔒 REQUIRES AUTHENTICATION - User can only save their own exams
    """
    try:
        logger.info(f"User {current_user.email} saving exam: {request.title}")
        
        # initialize exam service
        exam_service = ExamService(db) 

        exam_data = {
            'title': request.title,
            'description': request.description,
            'questions': request.questions,
            'duration_minutes': request.duration_minutes,
            'creator_id': current_user.id  # ← LINK TO USER
        }

        # save exam
        result = await exam_service.save_exam(exam_data)

        return SaveExamResponse(
            id=result.get('exam_id'),
            title=request.title,
            message=result.get('message')
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Error saving exam for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{exam_id}", status_code=status.HTTP_200_OK)
async def get_exam(
    exam_id: str,
    current_user: User = Depends(require_exam_access),  # ← OWNERSHIP CHECK
    db: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(rate_limit_read_only()),
):
    """
    Get exam by ID
    🔒 REQUIRES AUTHENTICATION + OWNERSHIP CHECK
    """
    try:
        logger.info(f"User {current_user.email} accessing exam: {exam_id}")
        
        # initialize exam service
        exam_service = ExamService(db) 

        # get exam (ownership already checked by dependency)
        result = await exam_service.get_exam_by_id(exam_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )

        return {
            'id': result.get('id'),
            'title': result.get('title'),
            'description': result.get('description'),
            'questions': result.get('questions', []),
            'duration_minutes': result.get('duration_minutes'),
            'created_at': result.get('created_at'),
            'is_public': result.get('is_public'),
            'creator_id': result.get('creator_id')
        }
    
    except HTTPException as e:
        raise e
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Error getting exam {exam_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", status_code=status.HTTP_200_OK)
async def list_user_exams(
    current_user: User = CurrentUser,
    db: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(rate_limit_read_only()),
):
    """
    List current user's exams ONLY
    🔒 REQUIRES AUTHENTICATION - Returns only user's own exams
    """
    try:
        logger.info(f"User {current_user.email} listing their own exams")
        
        exam_service = ExamService(db)
        exams = await exam_service.list_user_exams(current_user.id)  # ALWAYS user-scoped
        
        return {
            "exams": exams,
            "count": len(exams),
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Error listing exams for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/admin/all", status_code=status.HTTP_200_OK)
async def list_all_exams_admin(
    skip: int = 0,
    limit: int = 100,
    admin_user: User = AdminUser,  # ADMIN only
    db: AsyncSession = Depends(get_db_session),
    _rate_limit: None = Depends(rate_limit_read_only()),
):
    """
    List ALL exams (ADMIN ONLY)
    🔒 REQUIRES ADMIN ROLE
    """
    try:
        logger.info(f"Admin {admin_user.email} listing all exams")
        
        exam_service = ExamService(db)
        exams = await exam_service.list_all_exams_admin(skip, limit)
        
        return {
            "exams": exams,
            "count": len(exams),
            "total_available": len(exams),
            "admin_access": True
        }
        
    except Exception as e:
        logger.error(f"Error listing all exams for admin {admin_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )