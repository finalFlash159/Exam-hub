import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db_session
from app.services.auth_service import AuthService
from app.schemas.auth_schemas import UserResponse, UserRegisterRequest
from app.schemas.auth_schemas import LoginResponse, UserLoginRequest
from app.schemas.auth_schemas import MessageResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.auth_schemas import EmailVerificationRequest
from app.schemas.auth_schemas import RefreshTokenRequest, LogoutRequest

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        # Initialize auth service
        auth_service = AuthService(db)
        
        # Register user
        user_response = await auth_service.register_user(request)

        logger.info(f"User registered successfully: {user_response.email}")
        return user_response
    
    except ValueError as e:
        # Validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        # Initialize auth service
        auth_service = AuthService(db)

        # Login user
        login_response = await auth_service.login_user(request)

        logger.info(f"User logged in successfully: {request.email}")
        return login_response
    
    except ValueError as e:
        # Invalid credentials
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    request: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        # Initialize auth service
        auth_service = AuthService(db)

        # Verify email
        await auth_service.verify_email(request.token)

        logger.info(f"Email verified successfully")
        return MessageResponse(message="Email verified successfully")
    
    except Exception as e:
        logger.error(f"Email verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        # Initialize auth service
        auth_service = AuthService(db)
        
        # Forgot password
        await auth_service.forgot_password(request.email)

        logger.info(f"Password reset email sent to {request.email}")
        return MessageResponse(message="Password reset email sent")
    
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        # Initialize auth service
        auth_service = AuthService(db)
        
        # Reset password
        await auth_service.reset_password(request.token, request.new_password)

        logger.info(f"Password reset successfully")
        return MessageResponse(message="Password reset successfully")
    
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.post("/refresh-token", response_model=LoginResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        # Initialize auth service
        auth_service = AuthService(db)
        
        # Refresh token
        refresh_response = await auth_service.refresh_access_token(request.refresh_token)

        logger.info(f"Token refreshed successfully")
        return refresh_response
    
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
    
@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    request: LogoutRequest,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        # Initialize auth service
        auth_service = AuthService(db)
        
        # Logout user
        await auth_service.logout_user(request.refresh_token)

        logger.info(f"User logged out successfully")
        return MessageResponse(message="User logged out successfully")
    
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )