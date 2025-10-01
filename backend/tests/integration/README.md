# 🔗 Integration Tests Guide

Integration tests verify that **multiple components work together correctly** with real infrastructure (database, cache) but without external APIs.

---

## 📋 What are Integration Tests?

**Characteristics:**
- ✅ Test multiple components working together
- ✅ Use real database (test database or in-memory)
- ✅ Use real cache (Redis) if needed
- ✅ Mock external APIs (OpenAI, Gemini, email services)
- ✅ Test complete request-to-response flow
- ✅ Verify data persistence and retrieval

**What to Use (Real):**
- Database connections
- ORM queries (SQLAlchemy)
- Database transactions
- Cache operations (Redis)
- File system operations

**What to Mock:**
- External API calls (OpenAI, Gemini)
- Email services (Brevo/SendGrid)
- Payment gateways
- Third-party services

---

## 📁 Structure

```
tests/integration/
├── api/                   # API endpoint integration tests
│   ├── test_auth_endpoints.py
│   ├── test_exam_endpoints.py
│   └── test_upload_endpoints.py
├── services/              # Service layer integration tests
│   ├── test_auth_service_integration.py
│   ├── test_exam_service_integration.py
│   └── test_upload_service_integration.py
└── genai/                 # GenAI integration tests
    ├── test_genai_service.py
    └── test_document_processor.py
```

---

## 🎯 When to Write Integration Tests

Write integration tests for:
- ✅ **API endpoints** - Complete HTTP request/response flow
- ✅ **Database transactions** - Data persistence across layers
- ✅ **Service interactions** - Multiple services working together
- ✅ **Authentication flow** - Login, token refresh, logout
- ✅ **File upload/processing** - File storage and retrieval
- ✅ **Complex workflows** - Multi-step business processes

**Don't write integration tests for:**
- ❌ Simple CRUD operations (use unit tests)
- ❌ Individual functions (use unit tests)
- ❌ External API behavior (use E2E tests or manual testing)

---

## 🔧 Writing Integration Tests

### Example 1: Testing API Endpoints

```python
"""Integration test for authentication endpoints"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.models.base import Base
from app.database.connection import get_db_session


@pytest.fixture
async def test_db_engine():
    """Create test database"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """Create database session"""
    async_session = async_sessionmaker(test_db_engine, expire_on_commit=False)

    async with async_session() as session:
        yield session


@pytest.fixture
async def client(test_db_session):
    """Create test client with database override"""
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_user_registration_flow(client):
    """Test complete user registration flow"""
    # Register user
    response = await client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "id" in data
```

### Example 2: Testing Service Integration

```python
"""Integration test for exam service with real database"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.services.exam_service import ExamService
from app.repositories.exam_repository import ExamRepository
from app.repositories.user_repository import UserRepository
from app.models.base import Base


@pytest.fixture
async def db_session():
    """Create test database session"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def test_user(db_session):
    """Create test user"""
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user_with_verification(
        email="examuser@example.com",
        hashed_password="hashed",
        full_name="Exam User",
        verification_token="token"
    )
    await user_repo.verify_email("token")
    return user


@pytest.mark.asyncio
async def test_create_and_retrieve_exam(db_session, test_user):
    """Test creating exam and retrieving it"""
    exam_service = ExamService(db_session)

    # Create exam
    exam_data = {
        "title": "Python Basics",
        "subject": "Programming",
        "difficulty": "beginner",
        "questions": [...]
    }

    exam = await exam_service.create_exam(test_user.id, exam_data)

    # Retrieve exam
    retrieved_exam = await exam_service.get_exam(exam.id, test_user.id)

    assert retrieved_exam.id == exam.id
    assert retrieved_exam.title == "Python Basics"
    assert retrieved_exam.user_id == test_user.id
```

### Example 3: Testing Complete Flow

```python
"""Integration test for file upload and processing"""
import pytest
from io import BytesIO
from fastapi import UploadFile

from app.services.upload_service import UploadService
from app.services.document_service import DocumentService


@pytest.mark.asyncio
async def test_upload_and_process_document(db_session, test_user):
    """Test complete file upload and processing flow"""
    upload_service = UploadService(db_session)
    document_service = DocumentService()

    # Create test file
    file_content = b"This is test document content for processing."
    file = UploadFile(
        filename="test_document.txt",
        file=BytesIO(file_content)
    )

    # Upload file
    upload_result = await upload_service.save_uploaded_file(file, test_user.id)
    assert upload_result["file_id"] is not None

    file_id = upload_result["file_id"]

    # Process file
    process_result = await document_service.process_file(file_id, test_user.id)

    assert process_result["status"] == "completed"
    assert "extracted_text" in process_result
    assert len(process_result["extracted_text"]) > 0
```

---

## 🎭 Mocking External Services

### Pattern 1: Mock AI Client

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch('app.genai.clients.factory.AIClientFactory.create_client')
async def test_exam_generation_with_mock_ai(mock_factory, db_session, test_user):
    """Test exam generation with mocked AI client"""
    # Setup mock
    mock_client = AsyncMock()
    mock_client.generate_exam.return_value = {
        "questions": [
            {"question": "What is Python?", "answer": "A programming language"}
        ]
    }
    mock_factory.return_value = mock_client

    # Execute
    exam_service = ExamService(db_session)
    result = await exam_service.generate_exam_from_content("Python content", test_user.id)

    # Verify
    assert len(result["questions"]) > 0
    mock_client.generate_exam.assert_called_once()
```

### Pattern 2: Mock Email Service

```python
@pytest.mark.asyncio
@patch('app.services.email_service.EmailService.send_email')
async def test_registration_with_mock_email(mock_send_email, client):
    """Test registration with mocked email sending"""
    mock_send_email.return_value = True

    response = await client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
    )

    assert response.status_code == 201
    mock_send_email.assert_called_once()
```

---

## ▶️ Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/api/test_auth_endpoints.py -v

# Run specific test class
pytest tests/integration/api/test_auth_endpoints.py::TestUserLogin -v

# Run with markers
pytest -m integration -v

# Run with coverage
pytest tests/integration/ --cov=app --cov-report=html

# Run in parallel (be careful with database)
pytest tests/integration/ -n 2
```

---

## 🗄️ Database Setup Patterns

### Pattern 1: In-Memory SQLite (Fast)

```python
@pytest.fixture
async def db_session():
    """Fast in-memory database"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()
```

### Pattern 2: Test Database File (Persistent)

```python
@pytest.fixture
async def db_session():
    """Persistent test database"""
    test_db_path = "test_exam_hub.db"

    engine = create_async_engine(f"sqlite+aiosqlite:///{test_db_path}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()

    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
```

### Pattern 3: PostgreSQL Test Database (Production-like)

```python
@pytest.fixture(scope="session")
async def test_db_url():
    """Create test PostgreSQL database"""
    return "postgresql+asyncpg://user:pass@localhost/test_db"


@pytest.fixture
async def db_session(test_db_url):
    """PostgreSQL test database session"""
    engine = create_async_engine(test_db_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
```

---

## ✅ Integration Test Checklist

- [ ] Test uses real database (in-memory or test DB)
- [ ] External APIs are mocked
- [ ] Test covers complete flow (multiple layers)
- [ ] Test verifies data persistence
- [ ] Test has proper setup and teardown
- [ ] Test is independent of other tests
- [ ] Test uses fixtures for common setup
- [ ] Test cleans up after itself
- [ ] Test name describes the flow being tested
- [ ] Test assertions verify both behavior and state

---

## 🔄 Test Data Management

### Pattern 1: Fixtures for Common Data

```python
@pytest.fixture
async def verified_user(db_session):
    """Create verified user for tests"""
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user_with_verification(
        email="verified@example.com",
        hashed_password=get_password_hash("password"),
        full_name="Verified User",
        verification_token="token"
    )
    await user_repo.verify_email("token")
    return user


@pytest.fixture
async def admin_user(db_session):
    """Create admin user for tests"""
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user_with_verification(
        email="admin@example.com",
        hashed_password=get_password_hash("password"),
        full_name="Admin User",
        verification_token="token"
    )
    await user_repo.verify_email("token")
    user.role = UserRole.ADMIN
    await db_session.commit()
    return user
```

### Pattern 2: Factory Functions

```python
async def create_test_exam(db_session, user_id, **kwargs):
    """Factory function for creating test exams"""
    defaults = {
        "title": "Test Exam",
        "subject": "Test Subject",
        "difficulty": "medium",
        "questions": []
    }
    defaults.update(kwargs)

    exam_repo = ExamRepository(db_session)
    return await exam_repo.create(user_id=user_id, **defaults)
```

---

## 🐛 Common Pitfalls

### ❌ Don't: Depend on test execution order
```python
# Bad - tests depend on each other
async def test_create_user():
    global user_id
    user_id = await create_user()

async def test_update_user():  # Fails if test_create_user doesn't run first
    await update_user(user_id)
```

### ✅ Do: Make tests independent
```python
# Good - each test is self-contained
async def test_update_user(verified_user):
    await update_user(verified_user.id)
```

### ❌ Don't: Leave test data in database
```python
# Bad - pollutes database
async def test_something():
    user = await create_user()
    # Test code...
    # No cleanup!
```

### ✅ Do: Clean up test data
```python
# Good - cleans up
async def test_something(db_session):
    user = await create_user()
    try:
        # Test code...
    finally:
        await db_session.delete(user)
        await db_session.commit()
```

---

## 📚 Best Practices

1. **Use transactions** - Rollback after each test for clean state
2. **Mock external services** - Don't make real API calls
3. **Test realistic scenarios** - Use real data flows
4. **Keep tests focused** - One flow per test
5. **Use fixtures for setup** - Reuse common test data
6. **Clean up resources** - Delete files, close connections
7. **Test error paths** - Verify error handling across layers
8. **Use meaningful assertions** - Check both data and state

---

## 🔗 Related

- [Unit Tests Guide](../unit/README.md) - Testing isolated components
- [E2E Tests Guide](../e2e/README.md) - Testing complete user flows with real APIs
- [Main Testing Guide](../README.md) - Overview and quick start

---

**Remember:** Integration tests verify **components work together** with **real infrastructure** but **mocked external services** 🔗
