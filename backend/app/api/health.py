from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..database.connection import get_db_session
# from ..models.exam import ConnectionResponse  # Comment out

router = APIRouter(prefix="/health", tags=["health"])

# Tạo schema tạm
from pydantic import BaseModel

class ConnectionResponse(BaseModel):
    status: str
    message: str

@router.get("/")
async def health_check():
    return {"status": "healthy", "message": "Exam Hub API is running"}

@router.get("/gemini")
async def test_gemini_connection():
    try:
        # Tạm thời return success
        return ConnectionResponse(
            status="success",
            message="Gemini API connection test - temporarily disabled"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini connection failed: {str(e)}"
        )

@router.get("/database")
async def test_database_connection(db: AsyncSession = Depends(get_db_session)):
    try:
        # Test database connection
        await db.execute("SELECT 1")
        return {"status": "success", "message": "Database connection successful"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )