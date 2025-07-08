"""
Exam Hub FastAPI Application
Main application file with modular structure
"""

import os
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import core modules
from core.logging_config import setup_logging
from core.config import configure_gemini

# Import API routers
from api import upload_router, exam_router, health_router

# Setup logging
logger = setup_logging()


def setup_background_gemini():
    """Setup Gemini API in background thread for faster startup"""
    def background_gemini_test():
        try:
            configure_gemini()
            logger.info("Background Gemini initialization completed")
    except Exception as e:
            logger.warning(f"Background Gemini initialization failed: {e}")

    logger.info("Starting server with background Gemini initialization...")
    threading.Thread(target=background_gemini_test, daemon=True).start()
    logger.info("Server startup optimized")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Exam Hub API",
        description="API để tạo và quản lý bài kiểm tra từ tài liệu",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


# Initialize background services
setup_background_gemini()

# Create FastAPI app
app = create_app()
logger.info("FastAPI application initialized")

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Exam Hub API v2.0 - FastAPI",
        "description": "API để tạo bài kiểm tra từ tài liệu sử dụng AI",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "2.0.0"
    }


# Include API routers
app.include_router(health_router, prefix="", tags=["health"])
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(exam_router, prefix="/api", tags=["exam"])

logger.info("All API routers configured successfully")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    logger.info("Starting FastAPI server...")
    logger.info(f"Server will be available at: http://0.0.0.0:{port}")
    logger.info(f"API Documentation: http://0.0.0.0:{port}/docs")
    logger.info(f"Redoc Documentation: http://0.0.0.0:{port}/redoc")
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
