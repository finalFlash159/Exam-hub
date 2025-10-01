import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.schemas.auth_schemas import (
    UserRegisterRequest, UserLoginRequest,
    UserResponse, LoginResponse, MessageResponse
)
from app.repositories.user_repository import UserRepository, RefreshTokenRepository
from app.services.email_service import EmailService
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token,
    validate_password,
)
from app.models.user import User

logger = logging.getLogger(__name__)

class AuthService:
    """
    Authentication service for handling user auth workflows
    Manages registration, login, email verification, password reset,
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.user_repository = UserRepository(db_session)
        self.refresh_token_repository = RefreshTokenRepository(db_session)
        self.email_service = EmailService()
        logger.info("AuthService initialized")

    async def register_user(self, request: UserRegisterRequest) -> UserResponse:
        """
        Register new user with email verification

        Args:
            request (UserRegisterRequest): User registration data

        Returns:
            UserResponse: User information with verification status
        Raises:
            HTTPException: If email or user ID already exists
        """
        try:
            # Check if email already exists
            existing_user = await self.user_repository.get_by_email(request.email)
            if existing_user:
                raise ValueError("Email already registered")
             
            # hash password
            hashed_password = get_password_hash(request.password)
            
            # generate verification token
            verification_token = secrets.token_hex(32)
            
            # create user
            user = await self.user_repository.create_user_with_verification(
                email=request.email,
                hashed_password=hashed_password,
                full_name=request.full_name,
                verification_token=verification_token,
            )
            
            # send verification email
            await self.email_service.send_verification_email(request.email, verification_token)

            return UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value,
                is_active=user.is_active,
                is_verified=user.email_verified,
                created_at=user.created_at,
            )
        except ValueError as e:
            # Re-raise validation errors as-is  
            raise e
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise Exception("Failed to register user")
        
    
    async def login_user(self, request: UserLoginRequest) -> LoginResponse:
        """
        Authenticate user and generate tokens
        Agrs:
            request (UserLoginRequest): User login data 
        Returns:
            LoginResponse: Login response with access and refresh tokens
        Raises:
            HTTPException: If user not found or credentials are invalid
        """
        try:
            # check if user exists
            user = await self.user_repository.get_by_email(request.email)
            if not user:
                raise ValueError("User not found")
            
            # check if user is active
            if not user.is_active:
                raise ValueError("User is not active")
            
            # check if user is verified
            if not user.email_verified:
                raise ValueError("Please verify your email first")
            
            # verify password
            if not verify_password(request.password, user.hashed_password):
                raise ValueError("Invalid credentials")

            # generate tokens
            token_data = {"sub": user.id, "email": user.email}
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data, request.remember_me)

            # update last login timestamp
            await self.user_repository.update(user.id, last_login=datetime.now(timezone.utc))

            # set token expiration
            expires_days = 30 if request.remember_me else 7
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

            # save refresh token
            await self.refresh_token_repository.create_refresh_token(
                user_id=user.id,
                token=refresh_token,
                expires_at=expires_at,
            )

            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=UserResponse(
                    id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    role=user.role.value,
                    is_active=user.is_active,
                    is_verified=user.email_verified,
                    created_at=user.created_at,
                )
            )
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise Exception("Login failed")


    async def verify_email(self, token: str) -> bool:
        """
        Verify user email using token from email link
        Called when user clicks verification link
        """
        try:
            user = await self.user_repository.verify_email(token)

            if not user:
                raise ValueError("Invalid or expired verification token")
            
            logger.info(f"User {user.email} verified successfully")
            return True
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            raise Exception("Email verification failed")
    
    async def forgot_password(self, email: str) -> bool:
        """
        Send password reset email to user

        Args:
            email (str): User email
        Returns:
            bool: True if password reset email sent successfully, False otherwise
        Raises:
            ValueError: If user not found or email is invalid
        """
        try:
            # Get user by email
            user = await self.user_repository.get_by_email(email)
            if not user:
                raise ValueError("User not found")
            
            # Check if email is verified
            if not user.email_verified:
                raise ValueError("Please verify your email first")
            
            # Generate reset token
            reset_token = secrets.token_hex(32)
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

            # Save token to user
            await self.user_repository.set_password_reset_token(user, reset_token, expires_at)
            
            # Send reset email
            email_sent = await self.email_service.send_password_reset_email(
                email, reset_token, user.full_name
            )

            if email_sent:
                logger.info(f"Password reset email sent to {email}" )
                return True
            else:
                raise ValueError("Failed to send password reset email")
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            raise Exception("Failed to send password reset email")
        
    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset user password using reset token
        Args:
            token: Password reset token from email
            new_password: New password
        Returns:
            bool: True if password reset successfully, False otherwise
        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            # Validate new password
            is_valid, error_msg = validate_password(new_password)
            
            if not is_valid:
                raise ValueError(f"Invalid password: {error_msg}")
            
            # Reset password 
            user = await self.user_repository.reset_password(
                token, 
                get_password_hash(new_password)
            )
            
            if not user:
                raise ValueError(f"Invalid or expired password reset token")
            
            logger.info(f"Password reset successfully for user {user.email}")
            return True
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            raise Exception("Failed to reset password")
    
    async def refresh_access_token(self, refresh_token: str) -> LoginResponse:
        """
        Generate new access token using refresh token
        Args:
            refresh_token: Refresh token
        Returns:
            LoginResponse: Login response with new access token
        Raises:
            ValueError: If refresh token is invalid or expired
        """

        try:
            # Get valid refresh token from db
            db_token = await self.refresh_token_repository.get_valid_token(refresh_token)
            if not db_token:
                raise ValueError("Invalid or expired refresh token")
            
            # Get user
            user = await self.user_repository.get_by_id(db_token.user_id)
            if not user:
                raise ValueError("User not found")
            
            # Check if user is active
            if not user.is_active:
                raise ValueError("User is not active")

            # Generate new access token
            token_data = {"sub": user.id, "email": user.email}
            access_token = create_access_token(token_data)

            # Return new access token
            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=UserResponse(
                    id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    role=user.role.value,
                    is_active=user.is_active,
                    is_verified=user.email_verified,
                    created_at=user.created_at,
                )
            )
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error resetting access token: {e}")
            raise Exception("Failed to reset access token")
        

    
    async def logout_user(self, refresh_token: str) -> bool:
        """
        Logout user by revoking refresh token
        Args:
            refresh_token: Refresh token
        Returns:
            bool: True if logout successfully, False otherwise
        Raises:
            ValueError: If refresh token is invalid or expired
        """
        try:
            # Get valid refresh token from db 
            db_token = await self.refresh_token_repository.get_valid_token(refresh_token)
            if not db_token:
                raise ValueError("Invalid or expired refresh token")
            
            # Revoke refresh token
            success = await self.refresh_token_repository.revoke_token(refresh_token)
            if not success:
                raise ValueError("Failed to revoke refresh token")
            
            logger.info(f"User logged out successfully")
            return True
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            raise Exception("Failed to logout user")
        
