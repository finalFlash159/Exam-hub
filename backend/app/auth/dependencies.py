"""
FastAPI Authentication Dependencies
Ready-to-use Depends() objects for route protection
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.connection import get_db_session
from .middleware import (
    security, 
    get_current_user, 
    get_current_active_user,
    get_optional_user
)
from app.models.user import User
# Removed circular import: from .permissions import require_admin


async def current_user_dependency(
    credentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Dependency to get current authenticated user"""
    return await get_current_user(credentials, db)


async def current_active_user_dependency(
    user: User = Depends(current_user_dependency)
) -> User:
    """Dependency to get current active user"""
    return await get_current_active_user(user)


async def optional_user_dependency(
    credentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """Dependency to get optional user (None if not authenticated)"""
    return await get_optional_user(credentials, db)


# Ready-to-use dependencies
CurrentUser = Depends(current_user_dependency)
CurrentActiveUser = Depends(current_active_user_dependency)  
OptionalUser = Depends(optional_user_dependency)

# AdminUser moved to __init__.py to avoid circular import