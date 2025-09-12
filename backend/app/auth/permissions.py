"""
Authorization and Permission Management
Role-based access control and resource ownership validation
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.database.connection import get_db_session
# Removed circular import: from .dependencies import current_user_dependency
from .middleware import AuthorizationError, get_current_user, security

logger = logging.getLogger(__name__)


# Inline dependency to avoid circular import
async def current_user_dependency_inline(
    credentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Inline dependency to get current authenticated user (avoids circular import)"""
    return await get_current_user(credentials, db)


def require_role(required_role: UserRole):
    """
    Create a dependency that requires specific user role
    
    Args:
        required_role: Required user role (USER, ADMIN)
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(
        current_user: User = Depends(current_user_dependency_inline)
    ) -> User:
        if current_user.role != required_role:
            logger.warning(
                f"User {current_user.email} (role: {current_user.role}) "
                f"attempted to access {required_role} endpoint"
            )
            raise AuthorizationError(f"Requires {required_role.value} role")
        
        logger.debug(f"Role check passed for user: {current_user.email}")
        return current_user
    
    return role_checker


def require_admin():
    """Dependency that requires ADMIN role"""
    return require_role(UserRole.ADMIN)


async def check_exam_ownership(
    exam_id: str,
    current_user: User,
    db: AsyncSession
) -> bool:
    """
    Check if user owns exam or can access it (public exams)
    
    Args:
        exam_id: Exam ID to check
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        bool: True if user can access exam
    """
    try:
        # Import here to avoid circular imports
        from app.repositories.exam_repository import ExamRepository
        
        exam_repo = ExamRepository(db)
        exam = await exam_repo.get_by_id(exam_id)
        
        if not exam:
            logger.warning(f"Exam not found: {exam_id}")
            return False
        
        # Admin can access all exams
        if current_user.role == UserRole.ADMIN:
            logger.debug(f"Admin {current_user.email} accessing exam {exam_id}")
            return True
        
        # Owner can access their exam
        if exam.creator_id == current_user.id:
            logger.debug(f"Owner {current_user.email} accessing exam {exam_id}")
            return True
        
        # Anyone can access public exams
        if exam.is_public:
            logger.debug(f"User {current_user.email} accessing public exam {exam_id}")
            return True
        
        logger.warning(
            f"User {current_user.email} denied access to private exam {exam_id} "
            f"(owner: {exam.creator_id})"
        )
        return False
        
    except Exception as e:
        logger.error(f"Error checking exam ownership: {e}")
        return False


def create_exam_access_dependency():
    """
    Factory function to create exam access dependency
    This allows the dependency to access path parameters
    """
    async def require_exam_access(
        exam_id: str,  # Path parameter will be injected
        current_user: User = Depends(current_user_dependency_inline),
        db: AsyncSession = Depends(get_db_session)
    ) -> User:
        """
        Dependency that requires exam access (ownership or public)
        
        Args:
            exam_id: Exam ID from path parameter
            current_user: Current authenticated user
            db: Database session
            
        Returns:
            User: Current user if access is allowed
            
        Raises:
            HTTPException: If access is denied
        """
        has_access = await check_exam_ownership(exam_id, current_user, db)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only access your own exams or public exams."
            )
        
        return current_user
    
    return require_exam_access

# Create the dependency
require_exam_access = create_exam_access_dependency()


# Ready-to-use dependencies
AdminUser = Depends(require_admin())