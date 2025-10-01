"""
Unit tests for UserRepository

These tests use in-memory SQLite database and test repository methods in isolation.
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.user import User, UserRole
from app.models.base import Base
from app.repositories.user_repository import UserRepository


@pytest.fixture
async def db_session():
    """Create in-memory database for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def user_repository(db_session):
    """Create UserRepository instance"""
    return UserRepository(db_session)


class TestUserRepositoryCreate:
    """Test user creation methods"""

    @pytest.mark.asyncio
    async def test_create_user_with_verification(self, user_repository):
        """Test creating user with verification token"""
        user = await user_repository.create_user_with_verification(
            email="test@example.com",
            hashed_password="hashed_pwd",
            full_name="Test User",
            verification_token="token123"
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_pwd"
        assert user.full_name == "Test User"
        assert user.email_verification_token == "token123"
        assert user.email_verified is False
        assert user.role == UserRole.USER

    @pytest.mark.asyncio
    async def test_create_duplicate_email(self, user_repository):
        """Test creating user with duplicate email raises error"""
        await user_repository.create_user_with_verification(
            email="duplicate@example.com",
            hashed_password="pwd",
            full_name="User 1",
            verification_token="token1"
        )

        with pytest.raises(Exception):
            await user_repository.create_user_with_verification(
                email="duplicate@example.com",
                hashed_password="pwd2",
                full_name="User 2",
                verification_token="token2"
            )


class TestUserRepositoryRead:
    """Test user retrieval methods"""

    @pytest.mark.asyncio
    async def test_get_by_email_existing(self, user_repository):
        """Test getting existing user by email"""
        await user_repository.create_user_with_verification(
            email="exists@example.com",
            hashed_password="pwd",
            full_name="Existing User",
            verification_token="token"
        )

        user = await user_repository.get_by_email("exists@example.com")

        assert user is not None
        assert user.email == "exists@example.com"
        assert user.full_name == "Existing User"

    @pytest.mark.asyncio
    async def test_get_by_email_not_existing(self, user_repository):
        """Test getting non-existing user returns None"""
        user = await user_repository.get_by_email("notexists@example.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_id(self, user_repository):
        """Test getting user by ID"""
        created_user = await user_repository.create_user_with_verification(
            email="byid@example.com",
            hashed_password="pwd",
            full_name="By ID User",
            verification_token="token"
        )

        user = await user_repository.get_by_id(created_user.id)

        assert user is not None
        assert user.id == created_user.id
        assert user.email == "byid@example.com"


class TestUserRepositoryUpdate:
    """Test user update methods"""

    @pytest.mark.asyncio
    async def test_verify_email(self, user_repository):
        """Test email verification"""
        user = await user_repository.create_user_with_verification(
            email="verify@example.com",
            hashed_password="pwd",
            full_name="Verify User",
            verification_token="verify_token"
        )

        assert user.email_verified is False

        verified_user = await user_repository.verify_email("verify_token")

        assert verified_user is not None
        assert verified_user.email_verified is True
        assert verified_user.email_verification_token is None
        assert verified_user.email_verified_at is not None

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, user_repository):
        """Test email verification with invalid token"""
        verified_user = await user_repository.verify_email("invalid_token")
        assert verified_user is None

    @pytest.mark.asyncio
    async def test_set_password_reset_token(self, user_repository):
        """Test setting password reset token"""
        user = await user_repository.create_user_with_verification(
            email="reset@example.com",
            hashed_password="pwd",
            full_name="Reset User",
            verification_token="token"
        )

        reset_token = "reset_token_123"
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        success = await user_repository.set_password_reset_token(
            user, reset_token, expires_at
        )

        assert success is True

        # Verify token was set
        updated_user = await user_repository.get_by_id(user.id)
        assert updated_user.password_reset_token == reset_token
        assert updated_user.password_reset_expires is not None

    @pytest.mark.asyncio
    async def test_reset_password(self, user_repository):
        """Test password reset"""
        user = await user_repository.create_user_with_verification(
            email="resetpwd@example.com",
            hashed_password="old_pwd",
            full_name="Reset Password User",
            verification_token="token"
        )

        # Set reset token
        reset_token = "reset_123"
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        await user_repository.set_password_reset_token(user, reset_token, expires_at)

        # Reset password
        new_hashed_password = "new_hashed_pwd"
        updated_user = await user_repository.reset_password(reset_token, new_hashed_password)

        assert updated_user is not None
        assert updated_user.hashed_password == new_hashed_password
        assert updated_user.password_reset_token is None
        assert updated_user.password_reset_expires is None

    @pytest.mark.asyncio
    async def test_reset_password_expired_token(self, user_repository):
        """Test password reset with expired token"""
        user = await user_repository.create_user_with_verification(
            email="expired@example.com",
            hashed_password="pwd",
            full_name="Expired User",
            verification_token="token"
        )

        # Set expired reset token
        reset_token = "expired_token"
        expires_at = datetime.now(timezone.utc) - timedelta(hours=1)  # Already expired
        await user_repository.set_password_reset_token(user, reset_token, expires_at)

        # Try to reset password
        result = await user_repository.reset_password(reset_token, "new_pwd")

        assert result is None


class TestUserRepositoryDelete:
    """Test user deletion methods"""

    @pytest.mark.asyncio
    async def test_delete_user(self, user_repository):
        """Test deleting user"""
        user = await user_repository.create_user_with_verification(
            email="delete@example.com",
            hashed_password="pwd",
            full_name="Delete User",
            verification_token="token"
        )

        user_id = user.id

        success = await user_repository.delete(user_id)
        assert success is True

        # Verify user no longer exists
        deleted_user = await user_repository.get_by_id(user_id)
        assert deleted_user is None
