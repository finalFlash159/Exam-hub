"""
Authentication Module for Exam Hub API

Provides JWT authentication, authorization, and user validation
"""

from .middleware import get_current_user, get_current_active_user
from .dependencies import CurrentUser, CurrentActiveUser, OptionalUser
from .permissions import require_role, require_admin, check_exam_ownership, require_exam_access


# Define AdminUser here to avoid circular import
from fastapi import Depends
AdminUser = Depends(require_admin())

__all__ = [
    # Middleware functions
    "get_current_user",
    "get_current_active_user",
    
    # FastAPI dependencies
    "CurrentUser", 
    "CurrentActiveUser",
    "AdminUser",
    "OptionalUser",
    
    # Permission functions
    "require_role",
    "require_admin", 
    "check_exam_ownership",
    "require_exam_access",
]