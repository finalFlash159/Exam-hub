"""
Unit tests for AuthService

These tests mock repository dependencies to test business logic in isolation.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

from app.services.auth_service import AuthService
from app.schemas.auth_schemas import UserRegisterRequest, UserLoginRequest
from app.models.user import User, UserRole
from app.models.auth import RefreshToken


@pytest.fixture
def mock_user_repository():
    """Mock UserRepository"""
    return AsyncMock()


@pytest.fixture
def mock_token_repository():
    """Mock RefreshTokenRepository"""
    return AsyncMock()


@pytest.fixture
def mock_email_service():
    """Mock EmailService"""
    return AsyncMock()


@pytest.fixture
def mock_session():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_session):
    """Create AuthService with mocked dependencies"""
    service = AuthService(mock_session)
    return service


class TestUserRegistration:
    """Test user registration flow"""

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, mock_user_repository, mock_email_service):
        """Test successful user registration"""
        # Setup mocks
        auth_service.user_repository = mock_user_repository
        auth_service.email_service = mock_email_service

        mock_user_repository.get_by_email.return_value = None  # Email not taken

        # Create mock user object (not actual User model)
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "newuser@example.com"
        mock_user.full_name = "New User"
        mock_user.email_verified = False
        mock_user.role = UserRole.USER

        mock_user_repository.create_user_with_verification.return_value = mock_user
        mock_email_service.send_verification_email.return_value = True

        # Execute
        register_request = UserRegisterRequest(
            email="newuser@example.com",
            password="SecurePass123!",
            full_name="New User"
        )

        result = await auth_service.register_user(register_request)

        # Assertions
        assert result["email"] == "newuser@example.com"
        assert result["full_name"] == "New User"
        mock_user_repository.get_by_email.assert_called_once_with("newuser@example.com")
        mock_user_repository.create_user_with_verification.assert_called_once()
        mock_email_service.send_verification_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_email_already_exists(self, auth_service, mock_user_repository):
        """Test registration with existing email"""
        auth_service.user_repository = mock_user_repository

        existing_user = MagicMock()
        existing_user.id = 1
        existing_user.email = "existing@example.com"
        mock_user_repository.get_by_email.return_value = existing_user

        register_request = UserRegisterRequest(
            email="existing@example.com",
            password="password123",
            full_name="Test User"
        )

        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register_user(register_request)

    @pytest.mark.asyncio
    async def test_register_user_weak_password(self, auth_service):
        """Test registration with weak password"""
        register_request = UserRegisterRequest(
            email="test@example.com",
            password="weak",  # Too short
            full_name="Test User"
        )

        with pytest.raises(Exception):  # Pydantic ValidationError
            await auth_service.register_user(register_request)


class TestUserLogin:
    """Test user login flow"""

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, mock_user_repository, mock_token_repository):
        """Test successful login"""
        auth_service.user_repository = mock_user_repository
        auth_service.token_repository = mock_token_repository

        # Mock verified user with correct password
        with patch('app.core.security.verify_password', return_value=True):
            with patch('app.core.security.get_password_hash', return_value="hashed"):
                mock_user = MagicMock()
                mock_user.id = 1
                mock_user.email = "user@example.com"
                mock_user.hashed_password = "hashed"
                mock_user.email_verified = True
                mock_user.role = UserRole.USER
                mock_user_repository.get_by_email.return_value = mock_user

                mock_refresh_token = RefreshToken(
                    id=1,
                    user_id=1,
                    token="refresh_token_123",
                    expires_at=datetime.now(timezone.utc) + timedelta(days=7)
                )
                mock_token_repository.create_refresh_token.return_value = mock_refresh_token

                # Execute
                login_request = UserLoginRequest(
                    email="user@example.com",
                    password="correct_password",
                    remember_me=False
                )

                with patch('app.core.security.create_access_token', return_value="access_token_123"):
                    result = await auth_service.login_user(login_request)

                # Assertions
                assert "access_token" in result
                assert "refresh_token" in result
                assert result["token_type"] == "bearer"
                assert result["user"]["email"] == "user@example.com"

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_service, mock_user_repository):
        """Test login with non-existent email"""
        auth_service.user_repository = mock_user_repository
        mock_user_repository.get_by_email.return_value = None

        login_request = UserLoginRequest(
            email="notfound@example.com",
            password="password123",
            remember_me=False
        )

        with pytest.raises(ValueError, match="User not found"):
            await auth_service.login_user(login_request)

    @pytest.mark.asyncio
    async def test_login_unverified_email(self, auth_service, mock_user_repository):
        """Test login with unverified email"""
        auth_service.user_repository = mock_user_repository

        unverified_user = MagicMock()
        unverified_user.id = 1
        unverified_user.email = "unverified@example.com"
        unverified_user.email_verified = False

        mock_user_repository.get_by_email.return_value = unverified_user

        login_request = UserLoginRequest(
            email="unverified@example.com",
            password="password123",
            remember_me=False
        )

        with pytest.raises(ValueError, match="Email not verified"):
            await auth_service.login_user(login_request)

    @pytest.mark.asyncio
    async def test_login_incorrect_password(self, auth_service, mock_user_repository):
        """Test login with incorrect password"""
        auth_service.user_repository = mock_user_repository

        with patch('app.core.security.verify_password', return_value=False):
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.email = "user@example.com"
            mock_user.hashed_password = "hashed"
            mock_user.email_verified = True

            mock_user_repository.get_by_email.return_value = mock_user

            login_request = UserLoginRequest(
                email="user@example.com",
                password="wrong_password",
                remember_me=False
            )

            with pytest.raises(ValueError, match="Incorrect password"):
                await auth_service.login_user(login_request)


class TestEmailVerification:
    """Test email verification flow"""

    @pytest.mark.asyncio
    async def test_verify_email_success(self, auth_service, mock_user_repository):
        """Test successful email verification"""
        auth_service.user_repository = mock_user_repository

        verified_user = MagicMock()
        verified_user.id = 1
        verified_user.email = "verify@example.com"
        verified_user.email_verified = True

        mock_user_repository.verify_email.return_value = verified_user

        result = await auth_service.verify_email("valid_token")

        assert result is True
        mock_user_repository.verify_email.assert_called_once_with("valid_token")

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, auth_service, mock_user_repository):
        """Test email verification with invalid token"""
        auth_service.user_repository = mock_user_repository
        mock_user_repository.verify_email.return_value = None

        result = await auth_service.verify_email("invalid_token")

        assert result is False


class TestPasswordReset:
    """Test password reset flow"""

    @pytest.mark.asyncio
    async def test_forgot_password_success(self, auth_service, mock_user_repository, mock_email_service):
        """Test forgot password request"""
        auth_service.user_repository = mock_user_repository
        auth_service.email_service = mock_email_service

        mock_user = User(id=1, email="forgot@example.com")
        mock_user_repository.get_by_email.return_value = mock_user
        mock_user_repository.set_password_reset_token.return_value = True
        mock_email_service.send_password_reset_email.return_value = True

        result = await auth_service.forgot_password("forgot@example.com")

        assert result is True
        mock_user_repository.set_password_reset_token.assert_called_once()
        mock_email_service.send_password_reset_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_forgot_password_user_not_found(self, auth_service, mock_user_repository):
        """Test forgot password with non-existent email"""
        auth_service.user_repository = mock_user_repository
        mock_user_repository.get_by_email.return_value = None

        with pytest.raises(ValueError, match="User not found"):
            await auth_service.forgot_password("notfound@example.com")

    @pytest.mark.asyncio
    async def test_reset_password_success(self, auth_service, mock_user_repository):
        """Test successful password reset"""
        auth_service.user_repository = mock_user_repository
        mock_reset_user = MagicMock()
        mock_reset_user.email = "reset@example.com"
        mock_user_repository.reset_password.return_value = mock_reset_user

        result = await auth_service.reset_password("valid_token", "NewSecurePass123!")

        assert result is True
        mock_user_repository.reset_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, auth_service, mock_user_repository):
        """Test password reset with invalid token"""
        auth_service.user_repository = mock_user_repository
        mock_user_repository.reset_password.return_value = None

        with pytest.raises(ValueError, match="Invalid or expired password reset token"):
            await auth_service.reset_password("invalid_token", "NewPass123!")


class TestTokenRefresh:
    """Test token refresh flow"""

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, auth_service, mock_token_repository, mock_user_repository):
        """Test successful access token refresh"""
        auth_service.token_repository = mock_token_repository
        auth_service.user_repository = mock_user_repository

        mock_refresh_token = RefreshToken(
            id=1,
            user_id=1,
            token="refresh_123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        mock_token_repository.get_valid_token = AsyncMock(return_value=mock_refresh_token)

        mock_user = User(id=1, email="user@example.com", role=UserRole.USER)
        mock_user_repository.get_by_id.return_value = mock_user

        with patch('app.core.security.create_access_token', return_value="new_access_token"):
            result = await auth_service.refresh_access_token("refresh_123")

        assert result["access_token"] == "new_access_token"
        assert result["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid(self, auth_service, mock_token_repository):
        """Test refresh with invalid token"""
        auth_service.token_repository = mock_token_repository
        mock_token_repository.get_valid_token = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await auth_service.refresh_access_token("invalid_token")


class TestLogout:
    """Test logout flow"""

    @pytest.mark.asyncio
    async def test_logout_success(self, auth_service, mock_token_repository):
        """Test successful logout"""
        auth_service.token_repository = mock_token_repository
        mock_token_repository.revoke_token = AsyncMock(return_value=True)

        result = await auth_service.logout_user("refresh_token_123")

        assert result is True
        mock_token_repository.revoke_token.assert_called_once_with("refresh_token_123")

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self, auth_service, mock_token_repository):
        """Test logout with invalid token"""
        auth_service.token_repository = mock_token_repository
        mock_token_repository.revoke_token = AsyncMock(return_value=False)

        result = await auth_service.logout_user("invalid_token")

        assert result is False
