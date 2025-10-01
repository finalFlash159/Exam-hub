# 🧪 Unit Tests Guide

Unit tests verify individual components in **complete isolation** with all dependencies mocked.

---

## 📋 What are Unit Tests?

**Characteristics:**
- ✅ Test single function/method/class in isolation
- ✅ Mock all external dependencies (database, APIs, services)
- ✅ Fast execution (no I/O, network, or database)
- ✅ Deterministic (same input = same output, always)
- ✅ No side effects

**What to Mock:**
- Database connections and queries
- External API calls
- File system operations
- Email services
- Other services/repositories

---

## 📁 Structure

```
tests/unit/
├── repositories/          # Repository layer tests
│   ├── test_user_repository.py
│   ├── test_refresh_token_repository.py
│   └── test_exam_repository.py
├── services/             # Service layer tests
│   ├── test_auth_service.py
│   ├── test_exam_service.py
│   └── test_upload_service.py
├── utils/                # Utility function tests
│   ├── test_security.py
│   └── test_validators.py
└── genai/                # GenAI module tests
    ├── test_factory.py
    ├── test_mock_client.py
    ├── test_retry.py
    └── test_response_parser.py
```

---

## 🎯 When to Write Unit Tests

Write unit tests for:
- ✅ **Business logic** - Complex calculations, validations, transformations
- ✅ **Utility functions** - Pure functions with no side effects
- ✅ **Service methods** - Business logic with mocked dependencies
- ✅ **Repository methods** - Data access patterns (with in-memory DB)
- ✅ **Edge cases** - Boundary conditions, error handling

**Don't write unit tests for:**
- ❌ Simple getters/setters
- ❌ Database schema (use integration tests)
- ❌ Third-party libraries
- ❌ Configuration files

---

## 🔧 Writing Unit Tests

### Example 1: Testing Repository with In-Memory Database

```python
"""Test UserRepository methods"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.repositories.user_repository import UserRepository


@pytest.fixture
async def db_session():
    """Create in-memory database"""
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


@pytest.fixture
def user_repository(db_session):
    return UserRepository(db_session)


@pytest.mark.asyncio
async def test_create_user(user_repository):
    """Test creating a user"""
    user = await user_repository.create_user_with_verification(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        verification_token="token123"
    )

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_verified is False
```

### Example 2: Testing Service with Mocked Dependencies

```python
"""Test AuthService with mocked repositories"""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.auth_service import AuthService
from app.models.user import User


@pytest.fixture
def mock_user_repository():
    return AsyncMock()


@pytest.fixture
def mock_email_service():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_session):
    return AuthService(mock_session)


@pytest.mark.asyncio
async def test_register_user_success(auth_service, mock_user_repository, mock_email_service):
    """Test successful user registration"""
    # Setup mocks
    auth_service.user_repository = mock_user_repository
    auth_service.email_service = mock_email_service

    mock_user_repository.get_by_email.return_value = None
    mock_user = User(id=1, email="new@example.com", full_name="New User")
    mock_user_repository.create_user_with_verification.return_value = mock_user
    mock_email_service.send_verification_email.return_value = True

    # Execute
    result = await auth_service.register_user(register_request)

    # Assertions
    assert result["email"] == "new@example.com"
    mock_user_repository.create_user_with_verification.assert_called_once()
    mock_email_service.send_verification_email.assert_called_once()
```

### Example 3: Testing Utility Functions

```python
"""Test security utilities"""
import pytest
from app.core.security import validate_password, get_password_hash, verify_password


def test_validate_password_success():
    """Test password validation with valid password"""
    valid, message = validate_password("SecurePass123!")
    assert valid is True


def test_validate_password_too_short():
    """Test password validation with short password"""
    valid, message = validate_password("short")
    assert valid is False
    assert "at least 8 characters" in message


def test_password_hashing():
    """Test password hashing and verification"""
    password = "MySecurePassword123!"
    hashed = get_password_hash(password)

    # Hash should not be the same as password
    assert hashed != password

    # Verify correct password
    assert verify_password(password, hashed) is True

    # Verify incorrect password
    assert verify_password("WrongPassword", hashed) is False
```

---

## 🎭 Mocking Patterns

### Pattern 1: Mock AsyncMock for Async Functions

```python
from unittest.mock import AsyncMock

mock_repo = AsyncMock()
mock_repo.get_by_id.return_value = User(id=1, email="test@example.com")

user = await mock_repo.get_by_id(1)
assert user.email == "test@example.com"
```

### Pattern 2: Mock with Side Effects

```python
mock_service = AsyncMock()
mock_service.process.side_effect = [
    {"status": "success"},
    ValueError("Processing failed")
]

result1 = await mock_service.process()  # Returns success
# result2 = await mock_service.process()  # Raises ValueError
```

### Pattern 3: Patch External Dependencies

```python
from unittest.mock import patch

@patch('app.services.email_service.EmailService.send_email')
async def test_send_notification(mock_send_email):
    mock_send_email.return_value = True

    result = await notification_service.notify_user("user@example.com")

    assert result is True
    mock_send_email.assert_called_once()
```

### Pattern 4: Mock Return Values

```python
mock_repository = AsyncMock()
mock_repository.find_by_criteria.return_value = [
    User(id=1, email="user1@example.com"),
    User(id=2, email="user2@example.com")
]

users = await mock_repository.find_by_criteria(...)
assert len(users) == 2
```

---

## ▶️ Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/services/test_auth_service.py -v

# Run specific test class
pytest tests/unit/services/test_auth_service.py::TestUserRegistration -v

# Run specific test method
pytest tests/unit/services/test_auth_service.py::TestUserRegistration::test_register_user_success -v

# Run with markers
pytest -m unit -v

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=term-missing

# Run in parallel
pytest tests/unit/ -n auto
```

---

## ✅ Unit Test Checklist

- [ ] Test is isolated (no external dependencies)
- [ ] All dependencies are mocked
- [ ] Test is fast (< 100ms per test)
- [ ] Test has clear name describing what it tests
- [ ] Test follows AAA pattern (Arrange, Act, Assert)
- [ ] Test covers happy path
- [ ] Test covers edge cases
- [ ] Test covers error cases
- [ ] Assertions are specific and meaningful
- [ ] No hardcoded values (use variables/fixtures)

---

## 🎯 AAA Pattern

**Arrange** - Setup test data and mocks
**Act** - Execute the function being tested
**Assert** - Verify the results

```python
@pytest.mark.asyncio
async def test_create_user():
    # ARRANGE - Setup
    user_repo = UserRepository(db_session)
    email = "test@example.com"
    password = "hashed_password"

    # ACT - Execute
    user = await user_repo.create_user_with_verification(
        email=email,
        hashed_password=password,
        full_name="Test User",
        verification_token="token"
    )

    # ASSERT - Verify
    assert user.email == email
    assert user.hashed_password == password
    assert user.is_verified is False
```

---

## 🐛 Common Pitfalls

### ❌ Don't: Test implementation details
```python
# Bad - testing internal method
def test_internal_calculation():
    result = service._calculate_internal_value(10)
    assert result == 20
```

### ✅ Do: Test public interface
```python
# Good - testing public method
async def test_process_order():
    result = await service.process_order(order_id=123)
    assert result["status"] == "completed"
```

### ❌ Don't: Share state between tests
```python
# Bad - shared state
user = None

async def test_create():
    global user
    user = await repo.create_user(...)

async def test_update():  # Depends on test_create
    user.full_name = "Updated"
```

### ✅ Do: Use fixtures for clean state
```python
# Good - independent tests
@pytest.fixture
async def test_user():
    return await repo.create_user(...)

async def test_update(test_user):
    test_user.full_name = "Updated"
    await repo.update(test_user)
```

---

## 📚 Best Practices

1. **One assertion concept per test** - Test one thing at a time
2. **Use descriptive test names** - `test_login_with_invalid_password_returns_error`
3. **Keep tests simple** - Tests should be easier to read than production code
4. **Don't test external libraries** - Trust that pytest, FastAPI, etc. work
5. **Use fixtures for common setup** - Avoid code duplication
6. **Mock at the boundary** - Mock external dependencies, not internal logic
7. **Test behavior, not implementation** - Tests should survive refactoring

---

## 🔗 Related

- [Integration Tests Guide](../integration/README.md) - Testing with real database
- [E2E Tests Guide](../e2e/README.md) - Testing complete user flows
- [Main Testing Guide](../README.md) - Overview and quick start

---

**Remember:** Unit tests should be **FAST**, **ISOLATED**, and **DETERMINISTIC** ⚡
