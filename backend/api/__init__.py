from .upload import router as upload_router
from .exam import router as exam_router
from .health import router as health_router

__all__ = ["upload_router", "exam_router", "health_router"] 