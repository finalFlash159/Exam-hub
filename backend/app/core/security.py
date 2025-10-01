"""
Security utilities for password hashing and JWT token management
Handles authentication and authorization security concerns
"""

import re
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__type="ID",
    argon2__time_cost=2,
    argon2__memory_cost=102_400,
    argon2__parallelism=4,
)


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password complexity
    Returns: (is_valid, error_message)

    Requirements:
    - At least 8 characters
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one digit
    - At least one special character (@$!%*?&...)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    if not re.search(r'[^a-zA-Z0-9]', password):
        return False, "Password must contain at least one special character"
    return True, ""


def get_password_hash(password: str) -> str:
    """Hash password using Argon2"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise ValueError("Failed to hash password")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        return pwd_context.verify(password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token (30 minutes)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))

    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc)
    })
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], remember_me: bool = False) -> str:
    """Create JWT refresh token (7 days default, 30 days if remember_me)"""
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (timedelta(days=30) if remember_me else timedelta(days=7))
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.now(timezone.utc)
        })
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise ValueError("Failed to create refresh token")


def verify_token(token: str, expected_type: str = None) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"verify_exp": True}
        )
        if expected_type and payload.get("type") != expected_type:
            return None
        return payload
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        return None
