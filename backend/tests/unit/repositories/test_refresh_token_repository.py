"""
Unit tests for RefreshTokenRepository

Tests refresh token CRUD operations in isolation with in-memory database.
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.user import User, UserRole
from app.models.auth import RefreshToken
from app.models.base import Base
from app.repositories.user_repository import RefreshTokenRepository, UserRepository


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
async def test_user(db_session):
    """Create a test user"""
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user_with_verification(
        email="tokentest@example.com",
        hashed_password="hashed_pwd",
        full_name="Token Test User",
        verification_token="token"
    )
    return user


@pytest.fixture
def token_repository(db_session):
    """Create RefreshTokenRepository instance"""
    return RefreshTokenRepository(db_session)


class TestRefreshTokenCreate:
    """Test refresh token creation"""

    @pytest.mark.asyncio
    async def test_create_refresh_token(self, token_repository, test_user):
        """Test creating refresh token"""
        token = "test_refresh_token_123"
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        refresh_token = await token_repository.create_refresh_token(
            user_id=test_user.id,
            token=token,
            expires_at=expires_at,
            device_info="iPhone 15",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )

        assert refresh_token.id is not None
        assert refresh_token.user_id == test_user.id
        assert refresh_token.token == token
        # Compare timestamps without microseconds
        assert refresh_token.expires_at.replace(microsecond=0, tzinfo=timezone.utc) == expires_at.replace(microsecond=0)
        assert refresh_token.device_info == "iPhone 15"
        assert refresh_token.ip_address == "192.168.1.1"
        assert refresh_token.is_revoked is False

    @pytest.mark.asyncio
    async def test_create_multiple_tokens_same_user(self, token_repository, test_user):
        """Test creating multiple tokens for same user"""
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        token1 = await token_repository.create_refresh_token(
            test_user.id, "token1", expires_at, "Device 1"
        )
        token2 = await token_repository.create_refresh_token(
            test_user.id, "token2", expires_at, "Device 2"
        )

        assert token1.id != token2.id
        assert token1.token != token2.token
        assert token1.user_id == token2.user_id


class TestRefreshTokenRead:
    """Test refresh token retrieval"""

    @pytest.mark.asyncio
    async def test_get_valid_token(self, token_repository, test_user):
        """Test getting valid (not expired, not revoked) token"""
        token_str = "valid_token"
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        await token_repository.create_refresh_token(
            test_user.id, token_str, expires_at
        )

        found_token = await token_repository.get_valid_token(token_str)

        assert found_token is not None
        assert found_token.token == token_str
        assert found_token.is_revoked is False

    @pytest.mark.asyncio
    async def test_get_expired_token(self, token_repository, test_user):
        """Test getting expired token returns None"""
        token_str = "expired_token"
        expires_at = datetime.now(timezone.utc) - timedelta(days=1)  # Expired

        await token_repository.create_refresh_token(
            test_user.id, token_str, expires_at
        )

        found_token = await token_repository.get_valid_token(token_str)

        assert found_token is None

    @pytest.mark.asyncio
    async def test_get_revoked_token(self, token_repository, test_user):
        """Test getting revoked token returns None"""
        token_str = "revoked_token"
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        await token_repository.create_refresh_token(
            test_user.id, token_str, expires_at
        )

        # Revoke it
        await token_repository.revoke_token(token_str)

        # Try to get it
        found_token = await token_repository.get_valid_token(token_str)

        assert found_token is None

    @pytest.mark.asyncio
    async def test_get_nonexistent_token(self, token_repository):
        """Test getting non-existent token returns None"""
        found_token = await token_repository.get_valid_token("nonexistent")
        assert found_token is None


class TestRefreshTokenUpdate:
    """Test refresh token updates"""

    @pytest.mark.asyncio
    async def test_revoke_token(self, token_repository, test_user):
        """Test revoking a token"""
        token_str = "token_to_revoke"
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        await token_repository.create_refresh_token(
            test_user.id, token_str, expires_at
        )

        success = await token_repository.revoke_token(token_str)

        assert success is True

        # Verify token is revoked
        found_token = await token_repository.get_valid_token(token_str)
        assert found_token is None

    @pytest.mark.asyncio
    async def test_revoke_nonexistent_token(self, token_repository):
        """Test revoking non-existent token"""
        success = await token_repository.revoke_token("nonexistent")
        assert success is False

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens(self, token_repository, test_user):
        """Test revoking all tokens for a user"""
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        # Create 3 tokens
        await token_repository.create_refresh_token(test_user.id, "token1", expires_at)
        await token_repository.create_refresh_token(test_user.id, "token2", expires_at)
        await token_repository.create_refresh_token(test_user.id, "token3", expires_at)

        # Revoke all
        count = await token_repository.revoke_all_user_tokens(test_user.id)

        assert count == 3

        # Verify all are revoked
        assert await token_repository.get_valid_token("token1") is None
        assert await token_repository.get_valid_token("token2") is None
        assert await token_repository.get_valid_token("token3") is None

    @pytest.mark.asyncio
    async def test_revoke_all_tokens_no_tokens(self, token_repository, test_user):
        """Test revoking all tokens when user has none"""
        count = await token_repository.revoke_all_user_tokens(test_user.id)
        assert count == 0


class TestRefreshTokenCleanup:
    """Test cleanup operations"""

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens(self, token_repository, test_user):
        """Test cleaning up expired tokens"""
        now = datetime.now(timezone.utc)

        # Create expired and valid tokens
        await token_repository.create_refresh_token(
            test_user.id, "expired1", now - timedelta(days=1)
        )
        await token_repository.create_refresh_token(
            test_user.id, "expired2", now - timedelta(days=2)
        )
        await token_repository.create_refresh_token(
            test_user.id, "valid", now + timedelta(days=7)
        )

        # Note: Cleanup method needs to be implemented in repository
        # This is a test for future implementation
        # count = await token_repository.cleanup_expired_tokens()
        # assert count == 2
