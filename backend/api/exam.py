import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from models import ExamGenerationRequest, SaveExamRequest
from app.services.exam_service import ExamService

router = APIRouter(prefix="/api", tags=["exam"])
logger = logging.getLogger(__name__)


@router.post("/generate-exam")
async def generate_exam(request: ExamGenerationRequest) -> Dict[str, Any]:
    """Generate exam questions from uploaded file"""
    try:
        # Initialize exam service
        exam_service = ExamService()
        
        # Call service method
        result = await exam_service.generate_exam_from_file(
            file_id=request.file_id,
            exam_title=request.exam_title,
            question_count=request.question_count
        )

        return result
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail='File not found')
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/save-exam")
async def save_exam(request: SaveExamRequest) -> Dict[str, Any]:
    try:
        # Initialize exam service
        exam_service = ExamService()

        # Call service method
        result = await exam_service.save_exam(request.exam_data)

        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
