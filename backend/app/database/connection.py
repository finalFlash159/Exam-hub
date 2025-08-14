"""
Database connection and session management
Handles SQLAlchemy async engine and session creation
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global variables for engine and session
engine = None
async_session_maker = None


def create_engine():
    """Create SQLAlchemy async engine"""
    global engine
    
    database_url = settings.database_url
    logger.info(f"Creating database engine with URL: {database_url.split('@')[-1] if '@' in database_url else database_url}")
    
    # Engine configuration
    engine_kwargs = {
        "echo": settings.database_echo,
        "future": True
    }
    
    # Special configuration for SQLite
    if "sqlite" in database_url:
        engine_kwargs.update({
            "poolclass": StaticPool,
            "connect_args": {
                "check_same_thread": False,
                "timeout": 20
            }
        })
    
    # Special configuration for PostgreSQL
    elif "postgresql" in database_url:
        engine_kwargs.update({
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 10,
            "max_overflow": 20
        })
    
    engine = create_async_engine(database_url, **engine_kwargs)
    logger.info("Database engine created successfully")
    return engine


def create_session_maker():
    """Create async session maker"""
    global async_session_maker, engine
    
    if engine is None:
        engine = create_engine()
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )
    
    logger.info("Async session maker created")
    return async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session
    Use this in FastAPI dependencies
    """
    global async_session_maker
    
    if async_session_maker is None:
        async_session_maker = create_session_maker()
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database():
    """
    Initialize database (create tables)
    Call this on application startup
    """
    from app.models.base import Base
    # Import all models to ensure they're registered
    from app.models.exam import Exam, Question, ExamAttempt
    
    global engine
    
    if engine is None:
        engine = create_engine()
    
    logger.info("Creating database tables...")
    
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        logger.exception("Database initialization error:")
        return False


async def close_database():
    """
    Close database connections
    Call this on application shutdown
    """
    global engine
    
    if engine:
        logger.info("Closing database connections...")
        await engine.dispose()
        logger.info("Database connections closed")


async def check_database_connection():
    """
    Check if database connection is working
    Returns True if successful, False otherwise
    """
    global engine
    
    if engine is None:
        engine = create_engine()
    
    try:
        async with engine.begin() as conn:
            # Simple query to test connection
            from sqlalchemy import text
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("Database connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False 