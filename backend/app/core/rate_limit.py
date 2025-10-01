import logging
from fastapi import Request, HTTPException
from fastapi_limiter.depends import RateLimiter

logger = logging.getLogger(__name__)

async def get_rate_limit_key(request: Request) -> str:
    """
    Generate unique rate limit key for each user/IP

    Priority:
    1. User ID (authenticated) - from request.state.user
    2. IP Address (anonymous)

    Note:
        This function depends on request.state.user being set by authentication
        middleware for authenticated requests. For anonymous requests, it falls
        back to IP-based rate limiting.

    Returns:
        Unique identifier string (e.g., "user:123" or "ip:127.0.0.1")
    """
    try:
        # Try to get user from request state (set by auth middleware)
        # This creates a soft dependency on authentication middleware
        user = getattr(request.state, "user", None)
        
        if user:
            # Authenticated user: use user ID
            return f"user:{user.id}"
        else:
            # Anonymous user: use IP address
            client_ip = request.client.host if request.client else "unknown"
            return f"ip:{client_ip}"
            
    except Exception as e:
        logger.error(f"Error generating rate limit key: {e}")
        # Fallback to IP
        return f"ip:{request.client.host if request.client else 'unknown'}"
    

# Authentication endpoints (strict limits)
def rate_limit_auth_login():
    """
    Rate limit for login endpoint
    5 requests per minute per user/IP
    """
    return RateLimiter(times=5, seconds=60)


def rate_limit_auth_register():
    """
    Rate limit for registration endpoint
    3 requests per hour per IP
    """
    return RateLimiter(times=3, seconds=3600)


def rate_limit_auth_forgot_password():
    """
    Rate limit for forgot password (send email)
    3 requests per hour per IP - STRICT
    """
    return RateLimiter(times=3, seconds=3600)


def rate_limit_auth_reset_password():
    """
    Rate limit for reset password (with token)
    10 requests per hour per IP - RELAXED
    (token already provides protection)
    """
    return RateLimiter(times=10, seconds=3600)


def rate_limit_auth_verify_email():
    """
    Rate limit for email verification
    5 requests per hour per IP
    """
    return RateLimiter(times=5, seconds=3600)


# Exam generation endpoints (moderate limits)
def rate_limit_exam_generation():
    """
    Rate limit for exam generation
    10 requests per minute per user
    """
    return RateLimiter(times=10, seconds=60)


def rate_limit_exam_upload():
    """
    Rate limit for file upload
    5 requests per minute per user
    """
    return RateLimiter(times=5, seconds=60)


# General API endpoints (relaxed limits)
def rate_limit_general():
    """
    Rate limit for general API endpoints
    100 requests per minute per user/IP
    """
    return RateLimiter(times=100, seconds=60)


def rate_limit_read_only():
    """
    Rate limit for read-only endpoints (GET)
    200 requests per minute per user/IP
    """
    return RateLimiter(times=200, seconds=60)


def create_rate_limit_exceeded_response(request: Request, exc: HTTPException):
    """
    Custom error response when rate limit is exceeded
    
    Returns:
        Detailed error message with retry information
    """
    return {
        "error": "rate_limit_exceeded",
        "message": "Too many requests. Please try again later.",
        "detail": str(exc.detail) if hasattr(exc, 'detail') else "Rate limit exceeded",
        "path": str(request.url.path),
        "status_code": 429
    }


__all__ = [
    "rate_limit_auth_login",
    "rate_limit_auth_register",
    "rate_limit_auth_forgot_password",
    "rate_limit_auth_reset_password",
    "rate_limit_auth_verify_email",
    "rate_limit_exam_generation",
    "rate_limit_exam_upload",
    "rate_limit_general",
    "rate_limit_read_only",
    "get_rate_limit_key",
    "create_rate_limit_exceeded_response",
]