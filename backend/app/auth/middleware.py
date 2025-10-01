"""
JWT Authentication Middleware
Core authentication logic for token validation and user retrieval
"""

import logging
from typing import Optional
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


class AuthenticationError(HTTPException):
    """Custom authentication error with proper headers"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials],
    db: AsyncSession
) -> User:
    """
    Extract and validate JWT token, return current authenticated user
    
    Args:
        credentials: HTTP Bearer token from request header
        db: Database session
        
    Returns:
        User: Authenticated user object
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    # Check if token is provided
    if not credentials:
        logger.warning("No authentication token provided")
        raise AuthenticationError("Authentication token required")
    
    token = credentials.credentials
    
    try:
        # Verify JWT token
        payload = verify_token(token, expected_type="access")
        if not payload:
            logger.warning("Invalid or expired JWT token")
            raise AuthenticationError("Invalid or expired token")
        
        # Extract user ID from token
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token missing user ID (sub)")
            raise AuthenticationError("Invalid token format")
        
        # Get user from database
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        
        if not user:
            logger.warning(f"User not found for ID: {user_id}")
            raise AuthenticationError("User not found")
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user attempted access: {user.email}")
            raise AuthenticationError("Account is inactive")
        
        # Check if email is verified
        if not user.email_verified:
            logger.warning(f"Unverified user attempted access: {user.email}")
            raise AuthenticationError("Email verification required")
        
        logger.debug(f"User authenticated successfully: {user.email}")
        return user
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise AuthenticationError("Authentication failed")


async def get_current_active_user(user: User) -> User:
    """
    Ensure user is active and verified
    (Already checked in get_current_user, but kept for clarity)
    """
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials],
    db: AsyncSession
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    Used for endpoints that work for both authenticated and anonymous users
    
    Returns:
        User or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except AuthenticationError:
        # For optional auth, ignore auth errors
        return None