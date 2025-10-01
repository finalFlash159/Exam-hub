"""
Integration tests for Authentication API endpoints

These tests use TestClient with a real test database to verify
the complete authentication flow from HTTP request to database.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.base import Base
from app.database.connection import get_db_session
from app.models.user import User


@pytest.fixture
async def test_db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """Create test database session"""
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
async def client(test_db_session):
    """Create test client with database override"""
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db_session] = override_get_db

    # Mock FastAPILimiter to avoid Redis dependency in tests
    with patch('fastapi_limiter.FastAPILimiter.redis', new=AsyncMock()):
        with patch('fastapi_limiter.FastAPILimiter.identifier', new=AsyncMock()):
            with patch('fastapi_limiter.FastAPILimiter.http_callback', new=AsyncMock()):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as ac:
                    yield ac

    app.dependency_overrides.clear()


class TestUserRegistration:
    """Test /auth/register endpoint"""

    @pytest.mark.asyncio
    async def test_register_user_success(self, client):
        """Test successful user registration"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "full_name": "New User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # First registration
        await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "SecurePass123!",
                "full_name": "User 1"
            }
        )

        # Second registration with same email
        response = await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "AnotherPass123!",
                "full_name": "User 2"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "password": "SecurePass123!",
                "full_name": "Test User"
            }
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client):
        """Test registration with weak password"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak",
                "full_name": "Test User"
            }
        )

        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()


class TestUserLogin:
    """Test /auth/login endpoint"""

    @pytest.mark.asyncio
    async def test_login_success(self, client, test_db_session):
        """Test successful login"""
        # Register and verify user first
        from app.repositories.user_repository import UserRepository
        from app.core.security import get_password_hash

        user_repo = UserRepository(test_db_session)
        user = await user_repo.create_user_with_verification(
            email="login@example.com",
            hashed_password=get_password_hash("SecurePass123!"),
            full_name="Login User",
            verification_token="token123"
        )
        await user_repo.verify_email("token123")

        # Login
        response = await client.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "SecurePass123!",
                "remember_me": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "login@example.com"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_db_session):
        """Test login with wrong password"""
        from app.repositories.user_repository import UserRepository
        from app.core.security import get_password_hash

        user_repo = UserRepository(test_db_session)
        await user_repo.create_user_with_verification(
            email="wrongpwd@example.com",
            hashed_password=get_password_hash("CorrectPass123!"),
            full_name="Test User",
            verification_token="token"
        )
        await user_repo.verify_email("token")

        response = await client.post(
            "/auth/login",
            json={
                "email": "wrongpwd@example.com",
                "password": "WrongPass123!",
                "remember_me": False
            }
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_unverified_email(self, client, test_db_session):
        """Test login with unverified email"""
        from app.repositories.user_repository import UserRepository
        from app.core.security import get_password_hash

        user_repo = UserRepository(test_db_session)
        await user_repo.create_user_with_verification(
            email="unverified@example.com",
            hashed_password=get_password_hash("SecurePass123!"),
            full_name="Unverified User",
            verification_token="token"
        )
        # Don't verify email

        response = await client.post(
            "/auth/login",
            json={
                "email": "unverified@example.com",
                "password": "SecurePass123!",
                "remember_me": False
            }
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        response = await client.post(
            "/auth/login",
            json={
                "email": "notexist@example.com",
                "password": "SomePass123!",
                "remember_me": False
            }
        )

        assert response.status_code == 404


class TestEmailVerification:
    """Test /auth/verify-email endpoint"""

    @pytest.mark.asyncio
    async def test_verify_email_success(self, client, test_db_session):
        """Test successful email verification"""
        from app.repositories.user_repository import UserRepository
        from app.core.security import get_password_hash

        user_repo = UserRepository(test_db_session)
        await user_repo.create_user_with_verification(
            email="verify@example.com",
            hashed_password=get_password_hash("password"),
            full_name="Verify User",
            verification_token="valid_token"
        )

        response = await client.post(
            "/auth/verify-email",
            json={"token": "valid_token"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Email verified successfully"

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, client):
        """Test email verification with invalid token"""
        response = await client.post(
            "/auth/verify-email",
            json={"token": "invalid_token"}
        )

        assert response.status_code == 400


class TestPasswordReset:
    """Test password reset flow"""

    @pytest.mark.asyncio
    async def test_forgot_password_success(self, client, test_db_session):
        """Test forgot password request"""
        from app.repositories.user_repository import UserRepository
        from app.core.security import get_password_hash

        user_repo = UserRepository(test_db_session)
        await user_repo.create_user_with_verification(
            email="forgot@example.com",
            hashed_password=get_password_hash("password"),
            full_name="Forgot User",
            verification_token="token"
        )

        response = await client.post(
            "/auth/forgot-password",
            json={"email": "forgot@example.com"}
        )

        assert response.status_code == 200
        assert "reset email" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_reset_password_success(self, client, test_db_session):
        """Test successful password reset"""
        from app.repositories.user_repository import UserRepository
        from app.core.security import get_password_hash
        from datetime import datetime, timezone, timedelta

        user_repo = UserRepository(test_db_session)
        user = await user_repo.create_user_with_verification(
            email="reset@example.com",
            hashed_password=get_password_hash("OldPass123!"),
            full_name="Reset User",
            verification_token="token"
        )

        # Set reset token
        reset_token = "reset_token_123"
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        await user_repo.set_password_reset_token(user, reset_token, expires_at)

        response = await client.post(
            "/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewPass123!"
            }
        )

        assert response.status_code == 200


class TestTokenRefresh:
    """Test /auth/refresh-token endpoint"""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client, test_db_session):
        """Test successful token refresh"""
        from app.repositories.user_repository import UserRepository, RefreshTokenRepository
        from app.core.security import get_password_hash
        from datetime import datetime, timezone, timedelta

        # Create user
        user_repo = UserRepository(test_db_session)
        user = await user_repo.create_user_with_verification(
            email="refresh@example.com",
            hashed_password=get_password_hash("password"),
            full_name="Refresh User",
            verification_token="token"
        )
        await user_repo.verify_email("token")

        # Create refresh token
        token_repo = RefreshTokenRepository(test_db_session)
        refresh_token = await token_repo.create_refresh_token(
            user_id=user.id,
            token="refresh_token_123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        response = await client.post(
            "/auth/refresh-token",
            json={"refresh_token": "refresh_token_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


class TestLogout:
    """Test /auth/logout endpoint"""

    @pytest.mark.asyncio
    async def test_logout_success(self, client, test_db_session):
        """Test successful logout"""
        from app.repositories.user_repository import UserRepository, RefreshTokenRepository
        from app.core.security import get_password_hash
        from datetime import datetime, timezone, timedelta

        # Create user and refresh token
        user_repo = UserRepository(test_db_session)
        user = await user_repo.create_user_with_verification(
            email="logout@example.com",
            hashed_password=get_password_hash("password"),
            full_name="Logout User",
            verification_token="token"
        )

        token_repo = RefreshTokenRepository(test_db_session)
        await token_repo.create_refresh_token(
            user_id=user.id,
            token="logout_token",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        response = await client.post(
            "/auth/logout",
            json={"refresh_token": "logout_token"}
        )

        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

        # Verify token is revoked
        revoked_token = await token_repo.get_valid_token("logout_token")
        assert revoked_token is None
