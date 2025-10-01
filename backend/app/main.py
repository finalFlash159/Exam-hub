import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from app.api.auth import router as auth_router
from app.api.exam import router as exam_router
from app.api.upload import router as upload_router
from app.database.redis import RedisManager
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Database lifespan management
    Handles startup and shutdown events for database connections
    """
    # Startup
    logger.info("🚀 Starting up Exam Hub API...")
    
    # Init Database
    try:
        from app.database.connection import init_database
        logger.info("Initializing database...")
        success = await init_database()
        
        if success:
            logger.info("✅ Database initialized successfully")
        else:
            logger.error("❌ Database initialization failed")
  
    except Exception as e:
        logger.error(f"❌ Database startup error: {e}")
    
    # Init Redis
    try:
        if settings.rate_limit_enabled:
            logger.info("Initializing Redis connection...")
            await RedisManager.connect()

            redis_healthy = await RedisManager.health_check()
            if redis_healthy:
                logger.info("✅ Redis connected successfully")
                
                # Init fastapi-limiter
                try:
                    redis_client = await RedisManager.get_redis()
                    await FastAPILimiter.init(redis_client)
                    logger.info("✅ FastAPI Limiter initialized successfully")
                except Exception as e:
                    logger.error(f"❌ FastAPI Limiter initialization failed: {e}")
            else:
                logger.error("❌ Redis connection failed")
                logger.warning("Rate limiting will be disabled")
        else:
            logger.info("Rate limiting is disabled in settings")
    except Exception as e:
        logger.error(f"❌ Redis startup error: {e}")
        logger.warning("Rate limiting will be disabled")
             
    # App is running
    logger.info("🎯 Exam Hub API is ready!")
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Exam Hub API...")

    # Close Redis connection
    try:
        if settings.rate_limit_enabled:
            logger.info("Closing Redis connection...")
            await RedisManager.disconnect()
            logger.info("✅ Redis connection closed")
    except Exception as e:
        logger.error(f"❌ Redis shutdown error: {e}")
    
    try:
        from app.database.connection import close_database
        logger.info("Closing database connections...")
        await close_database()
        logger.info("✅ Database connections closed")
        
    except Exception as e:
        logger.error(f"❌ Database shutdown error: {e}")
    
    logger.info("👋 Exam Hub API shutdown complete")


def create_app() -> FastAPI:
    """
    Application factory function
    Creates and configures the FastAPI application with lifespan management
    """
    
    app = FastAPI(
        title="Exam Hub API",
        description="Refactored API for creating and managing exams from documents",
        version="3.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,  # From settings (specific origins only)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        return {
            "message": "Exam Hub API v3.0 - Refactored Architecture",
            "description": "Clean architecture with services, repositories, and database integration",
            "docs": "/docs",
            "redoc": "/redoc",
            "version": "3.0.0",
            "architecture": "layered",
            "status": "running"
        }

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health():
        """Health check endpoint with database and Redis status"""
        try:
            from app.database.connection import check_database_connection
            from app.core.config import settings
            
            # Check database
            db_status = await check_database_connection()
            
            # Check Redis (only if rate limiting is enabled)
            redis_status = None
            rate_limiting_status = "disabled"
            
            if settings.rate_limit_enabled:
                redis_status = await RedisManager.health_check()
                rate_limiting_status = "enabled" if redis_status else "error"
            
            # Overall status:
            # - healthy: DB ok, Redis ok (when enabled)
            # - degraded: DB ok, Redis error (if enabled)
            # - unhealthy: DB error
            if not db_status:
                overall_status = "unhealthy"
            elif settings.rate_limit_enabled and not redis_status:
                overall_status = "degraded"
            else:
                overall_status = "healthy"
            
            components = {
                "api": "ok",
                "database": "ok" if db_status else "error",
                "rate_limiting": rate_limiting_status
            }
            
            # Include Redis status only if rate limiting is enabled
            if settings.rate_limit_enabled:
                components["redis"] = "ok" if redis_status else "error"
            
            return {
                "status": overall_status,
                "version": "3.0.0",
                "components": components
            }
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                "status": "unhealthy",
                "version": "3.0.0",
                "error": str(e)
            }

    # Include API routers (routers already have their own prefixes)
    app.include_router(auth_router)
    app.include_router(exam_router)
    app.include_router(upload_router)
    
    logger.info("✅ FastAPI application created with all routers")
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 5001
    port = int(os.environ.get("PORT", 5001))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"🌟 Starting Exam Hub API on {host}:{port}")
    
    uvicorn.run(
        "app.main:app", 
        host=host, 
        port=port, 
        reload=True,
        log_level="info"
    )