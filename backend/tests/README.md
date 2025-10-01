# 🧪 Testing Guide - Exam Hub Backend

Comprehensive testing documentation for the Exam Hub backend application.

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Test Structure](#-test-structure)
3. [Test Types](#-test-types)
4. [Running Tests](#-running-tests)
5. [Writing Tests](#-writing-tests)
6. [Test Coverage](#-test-coverage)
7. [CI/CD Integration](#-cicd-integration)
8. [Best Practices](#-best-practices)

---

## 🚀 Quick Start

### Prerequisites
```bash
cd backend
pip install -r requirements.txt
```

### Run Tests
```bash
# All tests (excluding E2E)
pytest -m "not e2e"

# All tests including E2E
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test type
pytest tests/unit/ -v                # Unit tests only
pytest tests/integration/ -v         # Integration tests only
pytest tests/e2e/ -v                 # E2E tests only
```

---

## 📁 Test Structure

```
tests/
├── README.md                    # 👈 This file
├── conftest.py                  # Shared pytest fixtures
├── pytest.ini                   # Pytest configuration
│
├── unit/                        # 🔬 Unit Tests (isolated, mocked)
│   ├── README.md               # Unit testing guide
│   ├── repositories/           # Repository tests
│   │   ├── test_user_repository.py
│   │   ├── test_refresh_token_repository.py
│   │   └── test_exam_repository.py
│   ├── services/               # Service tests (mocked dependencies)
│   │   ├── test_auth_service.py
│   │   ├── test_exam_service.py
│   │   └── test_upload_service.py
│   ├── utils/                  # Utility tests
│   │   ├── test_security.py
│   │   └── test_validators.py
│   └── genai/                  # GenAI unit tests
│       ├── test_factory.py
│       ├── test_mock_client.py
│       ├── test_retry.py
│       └── test_response_parser.py
│
├── integration/                 # 🔗 Integration Tests (real DB, mocked APIs)
│   ├── README.md               # Integration testing guide
│   ├── api/                    # API endpoint tests
│   │   ├── test_auth_endpoints.py
│   │   ├── test_exam_endpoints.py
│   │   └── test_upload_endpoints.py
│   ├── services/               # Service integration tests
│   │   ├── test_auth_service_integration.py
│   │   └── test_exam_service_integration.py
│   └── genai/                  # GenAI integration tests
│       ├── test_genai_service.py
│       └── test_document_processor.py
│
├── e2e/                         # 🌐 End-to-End Tests (all real)
│   ├── README.md               # E2E testing guide
│   └── genai/                  # GenAI E2E tests
│       ├── test_api_endpoint.py
│       └── test_real_api.py
│
├── fixtures/                    # Shared test data
│   └── __init__.py
│
├── helpers/                     # Test helper utilities
│   └── __init__.py
│
└── scripts/                     # Manual test scripts
    ├── create_superuser.py
    ├── test_auth_service.py
    ├── test_upload_service.py
    └── test_user_repository.py
```

---

## 🎯 Test Types

### 🔬 Unit Tests (`tests/unit/`)

**Purpose:** Test individual components in isolation with mocked dependencies.

**Characteristics:**
- ✅ Fast execution (< 100ms per test)
- ✅ No external dependencies (DB, APIs, network)
- ✅ All dependencies mocked
- ✅ Test single function/method/class

**Example:**
```python
@pytest.mark.asyncio
async def test_validate_password():
    valid, msg = validate_password("SecurePass123!")
    assert valid is True
```

**[📖 Read Full Unit Testing Guide](unit/README.md)**

---

### 🔗 Integration Tests (`tests/integration/`)

**Purpose:** Test multiple components working together with real database but mocked external APIs.

**Characteristics:**
- ✅ Use real database (in-memory or test DB)
- ✅ Mock external APIs (OpenAI, Gemini, email)
- ✅ Test complete request-response flow
- ✅ Verify data persistence

**Example:**
```python
@pytest.mark.asyncio
async def test_user_registration_flow(client):
    response = await client.post("/auth/register", json={...})
    assert response.status_code == 201
```

**[📖 Read Full Integration Testing Guide](integration/README.md)**

---

### 🌐 E2E Tests (`tests/e2e/`)

**Purpose:** Test complete user flows with all real components including external APIs.

**Characteristics:**
- ✅ All real components (DB, cache, external APIs)
- ✅ Test critical user flows
- ✅ Slowest and most expensive tests
- ✅ Highest confidence

**Example:**
```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_exam_generation_with_real_ai(client):
    # Complete flow with real OpenAI/Gemini API
    ...
```

**[📖 Read Full E2E Testing Guide](e2e/README.md)**

---

## ▶️ Running Tests

### By Test Type

```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# E2E tests only
pytest tests/e2e/ -v
```

### By Marker

```bash
# Unit tests
pytest -m unit -v

# Integration tests
pytest -m integration -v

# E2E tests
pytest -m e2e -v

# Skip E2E tests (faster for local development)
pytest -m "not e2e" -v

# Skip slow tests
pytest -m "not slow" -v
```

### By Module

```bash
# Auth tests
pytest tests/unit/services/test_auth_service.py -v
pytest tests/integration/api/test_auth_endpoints.py -v

# GenAI tests
pytest tests/unit/genai/ -v
pytest tests/integration/genai/ -v
pytest tests/e2e/genai/ -v

# Repository tests
pytest tests/unit/repositories/ -v
```

### By Test Name

```bash
# Specific test function
pytest tests/unit/services/test_auth_service.py::test_register_user_success -v

# Test class
pytest tests/unit/services/test_auth_service.py::TestUserRegistration -v

# Pattern matching
pytest -k "register" -v  # Run all tests with "register" in name
pytest -k "not slow" -v  # Run all tests without "slow" in name
```

### With Options

```bash
# Verbose output
pytest -v

# Show print statements
pytest -v -s

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Parallel execution (faster)
pytest -n auto

# Show slowest 10 tests
pytest --durations=10

# Disable warnings
pytest --disable-warnings
```

---

## ✍️ Writing Tests

### Test Structure (AAA Pattern)

```python
@pytest.mark.asyncio
async def test_something():
    # ARRANGE - Setup test data
    user_data = {"email": "test@example.com"}
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = None

    # ACT - Execute function being tested
    result = await service.create_user(user_data)

    # ASSERT - Verify results
    assert result is not None
    assert result["email"] == "test@example.com"
    mock_repo.get_by_email.assert_called_once()
```

### Fixtures

```python
# In conftest.py
@pytest.fixture
async def db_session():
    """Provide database session for tests"""
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
    return await user_repo.create_user_with_verification(...)
```

### Mocking

```python
from unittest.mock import AsyncMock, patch

# Mock repository
mock_repo = AsyncMock()
mock_repo.get_by_id.return_value = User(id=1, email="test@example.com")

# Mock with patch
@patch('app.services.email_service.EmailService.send_email')
async def test_something(mock_send_email):
    mock_send_email.return_value = True
    ...
```

### Parametrize Tests

```python
@pytest.mark.parametrize("password,expected", [
    ("weak", False),
    ("SecurePass123!", True),
    ("12345678", False),
])
def test_password_validation(password, expected):
    valid, _ = validate_password(password)
    assert valid == expected
```

---

## 📊 Test Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=app --cov-report=term-missing

# HTML report (detailed)
pytest --cov=app --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=app --cov-report=xml

# Coverage for specific module
pytest tests/unit/services/ --cov=app.services
```

### Coverage Goals

- **Overall:** > 80%
- **Critical paths (auth, payment):** > 95%
- **Utility functions:** > 90%
- **API endpoints:** > 85%

### What to Cover

✅ **Do cover:**
- Business logic
- Edge cases and error handling
- Authentication/authorization
- Data validation
- API endpoints
- Database operations

❌ **Don't need to cover:**
- Configuration files
- Simple getters/setters
- Third-party library code
- Database migrations

---

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=app --cov-report=xml

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## ✅ Best Practices

### General

1. ✅ **Write tests first (TDD)** - Define behavior before implementation
2. ✅ **Keep tests simple** - Tests should be easier to read than production code
3. ✅ **Test behavior, not implementation** - Tests should survive refactoring
4. ✅ **One assertion concept per test** - Test one thing at a time
5. ✅ **Use descriptive names** - `test_login_with_invalid_credentials_returns_401`

### Unit Tests

1. ✅ **Mock all dependencies** - Database, APIs, external services
2. ✅ **Keep tests fast** - < 100ms per test
3. ✅ **Test edge cases** - Null values, empty lists, boundary conditions
4. ✅ **Test error handling** - Exceptions, validation errors

### Integration Tests

1. ✅ **Use test database** - In-memory SQLite or separate test DB
2. ✅ **Clean up after tests** - Reset database state
3. ✅ **Mock external APIs** - Don't make real API calls
4. ✅ **Test realistic flows** - Complete user scenarios

### E2E Tests

1. ✅ **Test critical paths only** - Don't test everything in E2E
2. ✅ **Use minimal data** - Keep API costs low
3. ✅ **Skip if no API keys** - Graceful degradation
4. ✅ **Run less frequently** - In CI on main branch only

---

## 🐛 Debugging Tests

### Run Single Test with Debug Output

```bash
pytest tests/unit/services/test_auth_service.py::test_register_user -v -s
```

### Use pytest debugger

```python
def test_something():
    result = function_under_test()
    import pdb; pdb.set_trace()  # Breakpoint
    assert result == expected
```

### Print debugging

```bash
# Show print statements
pytest -v -s

# Capture=no (show all output)
pytest -v --capture=no
```

---

## 📚 Additional Resources

### Guides
- **[Unit Testing Guide](unit/README.md)** - Detailed unit testing patterns
- **[Integration Testing Guide](integration/README.md)** - Integration testing best practices
- **[E2E Testing Guide](e2e/README.md)** - End-to-end testing strategies

### Official Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

### Testing Philosophy
- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Testing Best Practices](https://testingjavascript.com/) (principles apply to Python)

---

## 🎯 Quick Reference

```bash
# Fast local development (unit + integration, no E2E)
pytest -m "not e2e" -v

# Full test suite (all tests)
pytest -v

# With coverage
pytest --cov=app --cov-report=html -m "not e2e"

# Specific module
pytest tests/unit/services/test_auth_service.py -v

# Parallel execution
pytest -n auto -m "not e2e"

# Watch mode (requires pytest-watch)
ptw -- -v -m "not e2e"
```

---

**Happy Testing! 🧪✨**
