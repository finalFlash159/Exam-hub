"""
Configuration management for Exam Hub API v3.0
Handles environment variables, database, and API settings
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
        # Environment
        self.env = os.getenv('ENV', 'development')
        self.debug = self.env == 'development'
        
        # API settings
        self.api_title = "Exam Hub API"
        self.api_version = "3.0.0"
        self.api_description = "Clean architecture API for exam generation"
        
        # Security
        self.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

        # Email configuration (Brevo)
        self.brevo_api_key = os.getenv('BREVO_API_KEY', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@examhub.com')
        self.from_name = os.getenv('FROM_NAME', 'Exam Hub')
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')

        # Brevo template settings
        self.verification_email_template_id = os.getenv('VERIFICATION_EMAIL_TEMPLATE_ID', '')
        self.password_reset_template_id = os.getenv('PASSWORD_RESET_TEMPLATE_ID', '')
                
        # AI/LLM
        self.gemini_api_key = self._get_gemini_api_key()
        
        # File upload
        self.upload_folder = "uploads"
        self.allowed_extensions = {'pdf', 'docx'}
        self.max_upload_size = 16 * 1024 * 1024  # 16MB
        
        # Database
        self.database_url = self._get_database_url()
        self.database_echo = self.debug
        
        # Paths
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        project_root = os.path.dirname(backend_dir)
        self.questions_dir = os.path.join(project_root, "exam-app", "src", "data", "questions")
        
        # Logging
        self.log_level = "DEBUG" if self.debug else "INFO"
    
    def _get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key from environment variables"""
        return os.getenv("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    def _get_database_url(self) -> str:
        """Get database URL from environment or use SQLite default"""
        # Try PostgreSQL first (production)
        if all([
            os.getenv("DB_HOST"),
            os.getenv("DB_NAME"),
            os.getenv("DB_USER"),
            os.getenv("DB_PASSWORD")
        ]):
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT", "5432")
            name = os.getenv("DB_NAME")
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")
            return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
        
        # Fallback to SQLite (development)
        db_path = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./exam_hub.db")
        if db_path.startswith("sqlite"):
            return db_path
        return "sqlite+aiosqlite:///./exam_hub.db"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            "env": self.env,
            "debug": self.debug,
            "api_title": self.api_title,
            "api_version": self.api_version,
            "database_url": self.database_url,
            "gemini_api_key": self.gemini_api_key,
            "upload_folder": self.upload_folder,
            "allowed_extensions": self.allowed_extensions,
            "max_upload_size": self.max_upload_size,
            "questions_dir": self.questions_dir,
            "log_level": self.log_level
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
            model="gemini-2.0-flash-exp",
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
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.1
        )
    except Exception as e:
        logger.error(f"Failed to create Gemini instance: {e}")
        return None 