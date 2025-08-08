"""
Configuration management for Exam Hub API
Handles environment variables, settings, and API initialization
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    """Application settings configuration"""
    
    def __init__(self):
        self.env = os.getenv('ENV', 'production')
        self.gemini_api_key = self._get_gemini_api_key()
        self.upload_folder = "uploads"
        self.allowed_extensions = {'pdf', 'docx'}
        self.max_upload_size = 16 * 1024 * 1024  # 16MB
        # Calculate path to frontend questions directory
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        project_root = os.path.dirname(backend_dir)
        self.questions_dir = os.path.join(project_root, "exam-app", "src", "data", "questions")
    
    def _get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key from environment variables"""
        return os.getenv("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            "env": self.env,
            "gemini_api_key": self.gemini_api_key,
            "upload_folder": self.upload_folder,
            "allowed_extensions": self.allowed_extensions,
            "max_upload_size": self.max_upload_size,
            "questions_dir": self.questions_dir
        }


# Global settings instance
settings = Settings()


def get_settings() -> Dict[str, Any]:
    """Get application settings"""
    return settings.to_dict()


def configure_gemini() -> bool:
    """
    Configure and test Gemini API connection with lazy loading
    Returns: bool - True if successful, False if failed
    """
    logger.info("Initializing Gemini API configuration...")
    
    api_key = settings.gemini_api_key
    logger.debug(f"API key status: {'Found' if api_key else 'Missing'}")
    
    if not api_key:
        logger.warning("GEMINI_API_KEY not found in environment variables")
        logger.warning("Please set GEMINI_API_KEY environment variable")
        logger.warning("Gemini API functionality will be unavailable")
        return False
    
    try:
        logger.info("Creating ChatGoogleGenerativeAI instance...")
        
        # Create Gemini instance with optimized settings
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        
        logger.info("Gemini API instance created successfully")
        logger.info("Connection test skipped for faster startup")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Gemini API: {e}")
        logger.exception("Detailed error:")
        return False


def create_gemini_instance() -> Optional[ChatGoogleGenerativeAI]:
    """
    Create a new Gemini API instance for use
    Returns: ChatGoogleGenerativeAI instance or None if failed
    """
    api_key = settings.gemini_api_key
    
    if not api_key:
        logger.error("Cannot create Gemini instance: API key not configured")
        return None
    
    try:
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
    except Exception as e:
        logger.error(f"Failed to create Gemini instance: {e}")
        return None 