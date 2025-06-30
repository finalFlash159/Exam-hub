import os
import logging
from fastapi import APIRouter
from models import ConnectionResponse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@router.get("/api/test-connection", response_model=ConnectionResponse)
async def test_connection():
    """Test kết nối đến Gemini API"""
    logger.info("Testing Gemini API connection...")
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        logger.debug(f"API key available: {bool(api_key)}")
        
        if not api_key:
            logger.warning("No GEMINI_API_KEY found")
            return ConnectionResponse(
                status='error',
                backend=True,
                gemini=False,
                message='Không tìm thấy GEMINI_API_KEY'
            )
        
        # Test kết nối với LangChain
        logger.info("Creating ChatGoogleGenerativeAI instance...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        logger.debug("LLM instance created successfully")
        
        logger.info("Sending ping to Gemini API...")
        response = await llm.ainvoke([HumanMessage(content="Ping")])
        logger.info(f"Gemini response: {response.content[:50]}...")

        logger.info("Gemini API connection test successful")
        return ConnectionResponse(
            status='success',
            backend=True,
            gemini=True,
            message='Kết nối thành công đến Gemini API qua LangChain'
        )
    except Exception as e:
        logger.error(f"Gemini API connection failed: {str(e)}")
        logger.exception("Full error traceback:")
        return ConnectionResponse(
            status='error',
            backend=True,
            gemini=False,
            message=f'Lỗi: {str(e)}'
        ) 