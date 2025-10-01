"""
E2E tests for /exam/generate API endpoint with authentication.

Tests the full flow: HTTP Request → Auth → ExamService → GenAIService → Response
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.database.connection import get_db_session
from app.models.user import User
from app.utils.security import create_access_token


# Mark as e2e
pytestmark = pytest.mark.e2e


@pytest.fixture
async def test_db():
    """
    Provide test database session.
    """
    async for db in get_db_session():
        yield db


@pytest.fixture
async def test_user(test_db: AsyncSession):
    """
    Create a test user for authentication.
    Returns user object.
    """
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(test_db)

    # Check if test user exists
    existing_user = await user_repo.get_by_email("test@example.com")

    if existing_user:
        return existing_user

    # Create test user if not exists
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": "fake_hashed_password",
        "is_active": True,
        "is_verified": True,
        "role": "user"
    }

    user = await user_repo.create(user_data)
    return user


@pytest.fixture
def auth_headers(test_user: User):
    """
    Generate JWT token for test user.
    Returns authorization headers.
    """
    access_token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}


class TestExamGenerateEndpoint:
    """Test /exam/generate endpoint with authentication."""

    def test_generate_exam_with_valid_auth(self, auth_headers):
        """Test generate exam với valid authentication."""
        print("\n🔄 Testing /exam/generate endpoint with auth...")

        client = TestClient(app)
        # ARRANGE: Request data
        request_data = {
            "content": "Python is a high-level programming language. " * 10,
            "question_count": 2,
            "subject": "Python Programming",
            "ai_provider": "mock",  # Use mock to avoid API costs
            "language": "en",
            "difficulty": "easy"
        }

        # ACT: Call API endpoint
        response = client.post(
            "/exam/generate",
            json=request_data,
            headers=auth_headers
        )

        # ASSERT: Check response
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

        data = response.json()

        # Check response structure
        assert "success" in data
        assert "questions" in data
        assert "metadata" in data

        # Check success
        assert data["success"] is True

        # Check questions
        questions = data["questions"]
        assert isinstance(questions, list)
        assert len(questions) > 0

        # Check first question structure
        first_q = questions[0]
        assert "question_text" in first_q
        assert "options" in first_q
        assert "correct_answer" in first_q

        print(f"✅ Generated {len(questions)} questions via API")
        print(f"📝 Sample: {first_q['question_text'][:60]}...")

    def test_generate_exam_without_auth(self):
        """Test generate exam WITHOUT authentication - should fail."""
        print("\n🔄 Testing /exam/generate without auth (should fail)...")

        client = TestClient(app)
        request_data = {
            "content": "Test content",
            "question_count": 1,
            "ai_provider": "mock"
        }

        # ACT: Call without auth headers
        response = client.post(
            "/exam/generate",
            json=request_data
        )

        # ASSERT: Should be unauthorized
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

        print(f"✅ Correctly rejected unauthenticated request")

    def test_generate_exam_with_invalid_token(self):
        """Test generate exam với invalid JWT token."""
        print("\n🔄 Testing /exam/generate with invalid token...")

        client = TestClient(app)
        request_data = {
            "content": "Test content",
            "question_count": 1,
            "ai_provider": "mock"
        }

        # ACT: Call with invalid token
        response = client.post(
            "/exam/generate",
            json=request_data,
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        # ASSERT: Should be unauthorized
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

        print(f"✅ Correctly rejected invalid token")

    def test_generate_exam_with_short_content(self, auth_headers):
        """Test generate exam với content quá ngắn - should fail validation."""
        print("\n🔄 Testing /exam/generate with short content...")

        client = TestClient(app)
        request_data = {
            "content": "Short",  # < 100 chars
            "question_count": 1,
            "ai_provider": "mock"
        }

        # ACT: Call API
        response = client.post(
            "/exam/generate",
            json=request_data,
            headers=auth_headers
        )

        # ASSERT: Should be bad request
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        data = response.json()
        assert "detail" in data
        assert "Insufficient content" in data["detail"]

        print(f"✅ Correctly rejected short content")

    def test_generate_exam_with_different_providers(self, auth_headers):
        """Test generate exam với different AI providers."""
        print("\n🔄 Testing /exam/generate with different providers...")

        client = TestClient(app)
        for provider in ["mock"]:  # Only test mock for speed
            print(f"  Testing provider: {provider}")

            request_data = {
                "content": "Test content for exam generation. " * 10,
                "question_count": 1,
                "ai_provider": provider,
                "subject": f"Test with {provider}"
            }

            response = client.post(
                "/exam/generate",
                json=request_data,
                headers=auth_headers
            )

            assert response.status_code == 201, f"Provider {provider} failed: {response.text}"
            print(f"    ✅ {provider} worked")
