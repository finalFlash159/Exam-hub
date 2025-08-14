import os
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from core.config import get_settings
from document_processor import DocumentProcessor

router = APIRouter(prefix="/api", tags=["upload"])
logger = logging.getLogger(__name__)

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload và xử lý file document"""
    settings = get_settings()
    
    logger.info(f"Received upload request - filename: {file.filename}")
    logger.debug(f"Content type: {file.content_type}")

    if not file.filename:
        logger.warning("No filename provided")
        raise HTTPException(status_code=400, detail="No selected file")

    if not allowed_file(file.filename, settings["allowed_extensions"]):
        logger.warning(f"File type not allowed: {file.filename}")
        raise HTTPException(status_code=400, detail="File type not allowed")

    # Kiểm tra kích thước file
    logger.debug("Reading file content...")
    content = await file.read()
    file_size = len(content)
    logger.info(f"File size: {file_size} bytes")
    
    if file_size > settings["max_upload_size"]:
        logger.warning(f"File too large: {file_size} > {settings['max_upload_size']}")
        raise HTTPException(status_code=413, detail="File too large")

    # Tạo thư mục upload nếu chưa có
    upload_folder = settings["upload_folder"]
    os.makedirs(upload_folder, exist_ok=True)
    
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(upload_folder, unique_filename)
    logger.debug(f"Generated unique filename: {unique_filename}")

    try:
        # Lưu file
        logger.debug(f"Saving file to: {file_path}")
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"File saved successfully: {file_path}")

        # Xử lý document
        logger.info("Starting document processing...")
        processor = DocumentProcessor()
        extracted_text = processor.extract_text(file_path)
        text_length = len(extracted_text)
        logger.info(f"Document processed - extracted {text_length} characters")

        response_data = {
            'message': 'File uploaded successfully',
            'file_id': unique_filename,
            'text_length': text_length
        }
        logger.debug(f"Response data: {response_data}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=f'Server error: {str(e)}') 