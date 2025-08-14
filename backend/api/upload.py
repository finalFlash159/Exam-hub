import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.upload_service import UploadService

router = APIRouter(prefix="/api", tags=["upload"])
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # initialize upload service
        upload_service = UploadService()

        # call service method
        result = await upload_service.save_uploaded_file(file)

        return result
    
    except ValueError as e:
        # Validation error
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    