import logging
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.models.user import User, UserRole
from app.models.auth import RefreshToken, EmailVerificationToken
from .base import BaseRepository

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            stmt = select(User).where(User.email == email)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    async def create_user_with_verification(
        self, 
        email: str, 
        hashed_password: str, 
        full_name: str,
        verification_token: str
    ) -> User:
        """Create user with email verification token"""
        try:
            # Tạo User object
            user = User(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                email_verified=False,  # ← Chưa verify
                email_verification_token=verification_token,  # ← Token for verification
                is_active=True,  # ← Active nhưng chưa verified
                role=UserRole.USER  # ← Default role
            )
            
            # Add to database
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)  # ← Get generated ID
            
            logger.info(f"User created with email: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            await self.session.rollback()
            raise
    
    async def verify_email(self, token: str) -> Optional[User]:
        """Verify email and activate user"""
        try:
            # Tìm user bằng verification token
            stmt = select(User).where(
                and_(
                    User.email_verification_token == token,
                    User.email_verified == False  # ← Chỉ verify user chưa verified
                )
            )
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"Invalid verification token: {token}")
                return None
            
            # Update user - verify email
            user.email_verified = True
            user.email_verification_token = None  # ← Clear token
            
            await self.session.commit()
            logger.info(f"Email verified for user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            await self.session.rollback()
            return None
    
    async def set_password_reset_token(
        self, 
        user: User, 
        reset_token: str, 
        expires_at: datetime
    ) -> bool:
        """Set password reset token for user"""
        try:
            # Update user với reset token info
            user.password_reset_token = reset_token
            user.password_reset_expires = expires_at
            
            await self.session.commit()
            logger.info(f"Password reset token set for user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting password reset token: {e}")
            await self.session.rollback()
            return False
    
    async def reset_password(self, token: str, new_hashed_password: str) -> Optional[User]:
        """Reset password using token"""
        try:
            # Tìm user bằng reset token
            stmt = select(User).where(User.password_reset_token == token)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning(f"Invalid reset token: {token}")
                return None
            
            # Check token expiration
            now = datetime.now(timezone.utc)
            if user.password_reset_expires:
                expires = user.password_reset_expires
                
                # Ensure timezone is set
                if expires.tzinfo is None:
                    expires = expires.replace(tzinfo=timezone.utc)
                
                if expires < now:
                    logger.warning(f"Expired reset token for user: {user.email}")
                    return None
            
            # Update password và clear reset token
            user.hashed_password = new_hashed_password
            user.password_reset_token = None  # ← Clear token
            user.password_reset_expires = None  # ← Clear expiration
            
            await self.session.commit()
            logger.info(f"Password reset successful for user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            await self.session.rollback()
            return None

class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)
    
    async def create_refresh_token(
        self,
        user_id: str,
        token: str,
        expires_at: datetime,
        device_info: str = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> RefreshToken:
        """Create new refresh token"""
        try:
            refresh_token = RefreshToken(
                user_id=user_id,
                token=token,
                expires_at=expires_at,
                device_info=device_info,
                ip_address=ip_address,
                user_agent=user_agent,
                is_revoked=False  # ← Active token
            )
            
            self.session.add(refresh_token)
            await self.session.commit()
            await self.session.refresh(refresh_token)
            
            logger.info(f"Refresh token created for user: {user_id}")
            return refresh_token
            
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            await self.session.rollback()
            raise
    
    async def get_valid_token(self, token: str) -> Optional[RefreshToken]:
        """Get valid (non-revoked, non-expired) refresh token"""
        try:
            # Get token first, then check expiration manually
            stmt = select(RefreshToken).where(RefreshToken.token == token)
            result = await self.session.execute(stmt)
            refresh_token = result.scalar_one_or_none()
            
            if not refresh_token:
                return None
            
            # Check if revoked
            if refresh_token.is_revoked:
                return None
            
            # Check expiration with timezone handling
            now = datetime.now(timezone.utc)
            if refresh_token.expires_at:
                expires = refresh_token.expires_at
                # Fix timezone issue like password reset
                if expires.tzinfo is None:
                    expires = expires.replace(tzinfo=timezone.utc)
                
                if expires < now:
                    return None  # Expired
            
            return refresh_token
            
        except Exception as e:
            logger.error(f"Error getting valid token: {e}")
            return None
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke refresh token"""
        try:
            stmt = select(RefreshToken).where(RefreshToken.token == token)
            result = await self.session.execute(stmt)
            refresh_token = result.scalar_one_or_none()
            
            if not refresh_token:
                return False
            
            refresh_token.is_revoked = True
            await self.session.commit()
            
            logger.info(f"Refresh token revoked: {token[:10]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            await self.session.rollback()
            return False
    
    async def revoke_all_user_tokens(self, user_id: str) -> int:
        """Revoke all refresh tokens for user"""
        try:
            # Update all active tokens for user
            from sqlalchemy import update
            
            stmt = update(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.is_revoked == False
                )
            ).values(is_revoked=True)
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            revoked_count = result.rowcount
            logger.info(f"Revoked {revoked_count} tokens for user: {user_id}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"Error revoking all user tokens: {e}")
            await self.session.rollback()
            return 0