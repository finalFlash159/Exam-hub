"""
FastAPI Application Factory
Main entry point for the refactored Exam Hub API
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Will be implemented in future phases
# from app.core.config import get_settings
# from app.core.logging import setup_logging
# from app.api.endpoints import router as api_router

def create_app() -> FastAPI:
    """
    Application factory function
    Creates and configures the FastAPI application
    """
    
    app = FastAPI(
        title="Exam Hub API",
        description="Refactored API for creating and managing exams from documents",
        version="3.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Will be configured from settings later
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
            "architecture": "layered"
        }

    # Health check
    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok", "version": "3.0.0"}

    # TODO: In future phases, add:
    # - API routers
    # - Database initialization
    # - Authentication middleware
    # - Error handlers
    # - Logging setup

    return app

# For backward compatibility with current app.py
app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True) 