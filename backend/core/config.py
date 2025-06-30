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
    """Cấu hình và test Gemini API connection"""
    logger.info("Bắt đầu cấu hình Gemini API...")
    
    settings = get_settings()
    api_key = settings["gemini_api_key"]
    
    logger.debug(f"API key được tìm thấy: {bool(api_key)}")
    
    if not api_key:
        logger.error("Không tìm thấy GEMINI_API_KEY trong environment variables hoặc file .env")
        logger.error("Vui lòng set environment variable GEMINI_API_KEY trên Railway")
        raise Exception("Không tìm thấy GEMINI_API_KEY trong environment variables")
    
    try:
        logger.info("Đang khởi tạo ChatGoogleGenerativeAI...")
        # Test kết nối với LangChain
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        logger.debug("ChatGoogleGenerativeAI đã được khởi tạo")
        
        # Test ping
        logger.info("Đang test kết nối với Gemini...")
        test_response = llm.invoke([HumanMessage(content="Ping")])
        logger.info(f"Test response từ Gemini: {test_response.content[:50]}...")
        logger.info("Kết nối Gemini API thành công qua LangChain")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi kết nối Gemini API: {e}")
        logger.exception("Chi tiết lỗi:")
        raise 