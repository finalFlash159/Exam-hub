"""
Exam Hub FastAPI Application
Main application file with modular structure
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import core modules
from core.logging_config import setup_logging
from core.config import configure_gemini

# Import API routers
from api import upload_router, exam_router, health_router

# Setup logging
logger = setup_logging()

# Initialize Gemini
logger.info("Khởi động server và cấu hình Gemini API...")
gemini_configured = configure_gemini()
if gemini_configured:
    logger.info("Cấu hình Gemini hoàn tất")
else:
    logger.warning("Gemini API chưa được cấu hình - một số tính năng sẽ không khả dụng")

# Create FastAPI app
logger.info("Khởi tạo FastAPI application...")
app = FastAPI(
    title="Exam Hub API",
    description="API để tạo và quản lý bài kiểm tra",
    version="2.0.0"
)
logger.info("FastAPI app đã được khởi tạo")

# Configure CORS
logger.info("Cấu hình CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware đã được cấu hình")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Exam Hub API v2.0 - FastAPI", "docs": "/docs"}

# Simple health check (backup)
@app.get("/health")
async def simple_health():
    """Simple health check endpoint"""
    return {"status": "ok", "service": "exam-hub-api"}

# Include routers
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(exam_router)

logger.info("✅ All routers included successfully")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    logger.info("Starting FastAPI server...")
    logger.info(f"Server will be available at: http://0.0.0.0:{port}")
    logger.info(f"API Documentation: http://0.0.0.0:{port}/docs")
    logger.info(f"Redoc Documentation: http://0.0.0.0:{port}/redoc")
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
