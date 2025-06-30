import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def get_settings():
    """Get application settings"""
    # Try to get API key from environment variables first (Railway), then from .env file (local)
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    return {
        "env": os.getenv('ENV', 'production'),
        "gemini_api_key": gemini_api_key,
        "upload_folder": "uploads",
        "allowed_extensions": {'pdf', 'docx'},
        "max_upload_size": 16 * 1024 * 1024,  # 16MB
        "questions_dir": "../exam-app/src/data/questions"
    }

def configure_gemini():
    """Cấu hình và test Gemini API connection - LAZY LOAD"""
    logger.info("Bắt đầu cấu hình Gemini API...")
    
    settings = get_settings()
    api_key = settings["gemini_api_key"]
    
    logger.debug(f"API key được tìm thấy: {bool(api_key)}")
    
    if not api_key:
        logger.warning("Không tìm thấy GEMINI_API_KEY trong environment variables hoặc file .env")
        logger.warning("Gemini API sẽ không khả dụng. Vui lòng set environment variable GEMINI_API_KEY trên Railway")
        return False  # Return False instead of raising exception
    
    try:
        logger.info("Đang khởi tạo ChatGoogleGenerativeAI...")
        # Test kết nối với LangChain - SKIP PING FOR FASTER STARTUP
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        logger.debug("ChatGoogleGenerativeAI đã được khởi tạo")
        
        # SKIP TEST PING - Just return success if instance created
        logger.info("Gemini API instance created successfully (test connection skipped for faster startup)")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi kết nối Gemini API: {e}")
        logger.exception("Chi tiết lỗi:")
        return False  # Don't raise, just return False 