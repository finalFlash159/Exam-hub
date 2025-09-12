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
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/exam", tags=["exam"])

@router.post("/generate", response_model=ExamGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_exam(
    request: ExamGenerationRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Generate exam questions from document content
    """
    try:
        # initialize exam service
        exam_service = ExamService(db)

        # generate exam
        result = await exam_service.generate_exam_from_text(
            file_content=request.file_content,
            num_questions=request.num_questions,
            subject=request.subject
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
            questions=question_response,
            subject=request.subject,
            total_questions=len(question_response)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.post("/save", response_model=SaveExamResponse, status_code=status.HTTP_201_CREATED)
async def save_exam(
    request: SaveExamRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Save exam to database
    """
    try:
        # initialize exam service
        exam_service = ExamService(db) 

        exam_data = {
            'title': request.title,
            'description': request.description,
            'questions': request.questions,
            'duration_minutes': request.duration_minutes
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{exam_id}", status_code=status.HTTP_200_OK)
async def get_exam(
    exam_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get exam by ID
    """
    try:
        # initialize exam service
        exam_service = ExamService(db) 

        # get exam
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
            'is_public': result.get('is_public')
        }
    
    except HTTPException as e:
        raise e
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )