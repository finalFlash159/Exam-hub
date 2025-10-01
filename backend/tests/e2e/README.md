# 🌐 End-to-End (E2E) Tests Guide

E2E tests verify **complete user flows** with **all real components** including external APIs.

---

## 📋 What are E2E Tests?

**Characteristics:**
- ✅ Test complete user scenarios from start to finish
- ✅ Use all real infrastructure (database, cache, external APIs)
- ✅ Test real API interactions (OpenAI, Gemini, email services)
- ✅ Verify entire system working together
- ✅ Slowest tests but highest confidence

**What to Use (All Real):**
- Database connections
- External API calls (OpenAI, Gemini)
- Email services
- File storage
- Cache (Redis)
- Complete HTTP request/response flow

**What NOT to Mock:**
- Nothing! (or as little as possible)

---

## 📁 Structure

```
tests/e2e/
└── genai/                    # GenAI E2E tests
    ├── test_api_endpoint.py  # Full API flow with real AI
    └── test_real_api.py      # Direct AI client tests
```

---

## 🎯 When to Write E2E Tests

Write E2E tests for:
- ✅ **Critical user flows** - Registration → Login → Create Exam
- ✅ **External API integration** - OpenAI/Gemini exam generation
- ✅ **Payment flows** - (if applicable)
- ✅ **Complex workflows** - Multi-step processes with external services
- ✅ **Smoke tests** - Basic functionality checks before deployment

**Don't write E2E tests for:**
- ❌ Every single feature (too slow and expensive)
- ❌ Edge cases (use unit/integration tests)
- ❌ Internal implementation details
- ❌ Already covered by integration tests

---

## 🔧 Writing E2E Tests

### Example 1: Testing AI Exam Generation Flow

```python
"""E2E test for exam generation with real OpenAI API"""
import pytest
import os
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.config import settings


pytestmark = pytest.mark.e2e  # Mark all tests in this file as E2E


@pytest.fixture
async def client():
    """Create test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def skip_if_no_api_key():
    """Skip test if API key not configured"""
    if not settings.openai_api_key or settings.openai_api_key.startswith("sk-fake"):
        pytest.skip("OpenAI API key not configured")


@pytest.mark.asyncio
async def test_complete_exam_generation_flow(client, skip_if_no_api_key):
    """Test complete exam generation flow with real OpenAI API"""
    # 1. Register user
    register_response = await client.post(
        "/auth/register",
        json={
            "email": "e2euser@example.com",
            "password": "SecurePass123!",
            "full_name": "E2E Test User"
        }
    )
    assert register_response.status_code == 201

    # 2. Login
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "e2euser@example.com",
            "password": "SecurePass123!",
            "remember_me": False
        }
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # 3. Generate exam with real AI
    headers = {"Authorization": f"Bearer {access_token}"}
    exam_response = await client.post(
        "/exam/generate",
        json={
            "content": "Python is a high-level programming language. Key features: dynamic typing, garbage collection, interpreted.",
            "subject": "Programming",
            "difficulty": "beginner",
            "question_count": 5
        },
        headers=headers
    )

    assert exam_response.status_code == 200
    exam_data = exam_response.json()
    assert len(exam_data["questions"]) == 5
    assert all("question" in q for q in exam_data["questions"])
    assert all("answer" in q for q in exam_data["questions"])

    # 4. Save exam
    save_response = await client.post(
        "/exam/save",
        json={
            "title": "Python Basics E2E Test",
            "exam_data": exam_data
        },
        headers=headers
    )

    assert save_response.status_code == 201
    saved_exam = save_response.json()
    assert saved_exam["id"] is not None

    # 5. Retrieve exam
    exam_id = saved_exam["id"]
    get_response = await client.get(
        f"/exam/{exam_id}",
        headers=headers
    )

    assert get_response.status_code == 200
    retrieved_exam = get_response.json()
    assert retrieved_exam["title"] == "Python Basics E2E Test"
```

### Example 2: Testing Document Upload and AI Processing

```python
"""E2E test for file upload and AI content extraction"""
import pytest
from io import BytesIO


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_upload_and_ai_process_document(client, skip_if_no_api_key):
    """Test uploading document and processing with real AI"""
    # 1. Login as user
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "fileuser@example.com",
            "password": "password",
            "remember_me": False
        }
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Upload file
    file_content = b"Machine learning is a subset of AI. It uses algorithms to learn from data."
    files = {
        "file": ("document.txt", BytesIO(file_content), "text/plain")
    }

    upload_response = await client.post(
        "/upload/",
        files=files,
        headers=headers
    )

    assert upload_response.status_code == 201
    file_id = upload_response.json()["file_id"]

    # 3. Process with AI
    process_response = await client.post(
        f"/upload/{file_id}/process",
        headers=headers
    )

    assert process_response.status_code == 200
    result = process_response.json()
    assert "extracted_content" in result
    assert "summary" in result
    assert len(result["extracted_content"]) > 0
```

### Example 3: Testing Real AI Client Directly

```python
"""Direct E2E test for AI clients"""
import pytest
from app.genai.clients.openai_client import OpenAIClient
from app.genai.clients.gemini_client import GeminiClient
from app.core.config import settings


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_openai_client_real_api():
    """Test OpenAI client with real API"""
    if not settings.openai_api_key:
        pytest.skip("OpenAI API key not configured")

    client = OpenAIClient(api_key=settings.openai_api_key)

    response = await client.generate_completion(
        prompt="What is 2 + 2? Answer in one word.",
        max_tokens=10
    )

    assert response is not None
    assert len(response) > 0
    assert "4" in response or "four" in response.lower()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_gemini_client_real_api():
    """Test Gemini client with real API"""
    if not settings.gemini_api_key:
        pytest.skip("Gemini API key not configured")

    client = GeminiClient(api_key=settings.gemini_api_key)

    response = await client.generate_exam(
        content="Python programming language",
        subject="Programming",
        difficulty="beginner",
        question_count=3
    )

    assert response is not None
    assert "questions" in response
    assert len(response["questions"]) == 3
```

---

## ⚙️ Configuration

### pytest Markers

Mark E2E tests so they can be run separately:

```python
# Mark single test
@pytest.mark.e2e
async def test_something():
    ...

# Mark entire file
pytestmark = pytest.mark.e2e
```

### Skipping Tests Without API Keys

```python
@pytest.fixture
def skip_if_no_openai_key():
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OpenAI API key not configured")


@pytest.fixture
def skip_if_no_gemini_key():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("Gemini API key not configured")
```

---

## ▶️ Running E2E Tests

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run with E2E marker
pytest -m e2e -v

# Skip E2E tests (run only unit + integration)
pytest -m "not e2e" -v

# Run specific E2E test
pytest tests/e2e/genai/test_real_api.py::test_openai_client_real_api -v

# Run with verbose output
pytest tests/e2e/ -v -s

# Run with rate limiting (to avoid API rate limits)
pytest tests/e2e/ -v --maxfail=1  # Stop after first failure
```

---

## 💰 Cost Management

E2E tests that call external APIs incur costs. Follow these practices:

### 1. Use Test Mode When Available
```python
# OpenAI doesn't have test mode, but you can use cheaper models
client = OpenAIClient(api_key=key, model="gpt-3.5-turbo")  # Cheaper than gpt-4
```

### 2. Limit Test Data Size
```python
# Bad - expensive
content = "..." * 10000  # Very long content

# Good - minimal but realistic
content = "Python is a programming language."
```

### 3. Cache Responses (for development)
```python
@pytest.fixture
def cached_ai_response():
    """Use cached response for development"""
    if os.getenv("CI"):  # Only use real API in CI
        return None
    return {
        "questions": [
            {"question": "What is Python?", "answer": "A programming language"}
        ]
    }
```

### 4. Run E2E Tests Less Frequently
- Run in CI only on main branch
- Run manually before releases
- Don't run on every commit

---

## 🚦 CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e-tests:
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

      - name: Run E2E tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          pytest -m e2e -v --maxfail=3
```

---

## ✅ E2E Test Checklist

- [ ] Test covers complete user flow
- [ ] Test uses real external APIs
- [ ] Test is marked with `@pytest.mark.e2e`
- [ ] Test skips gracefully if API keys missing
- [ ] Test uses minimal data to reduce costs
- [ ] Test has clear failure messages
- [ ] Test cleans up created data
- [ ] Test is idempotent (can run multiple times)
- [ ] Test doesn't depend on other tests
- [ ] Test has reasonable timeout

---

## 🐛 Common Pitfalls

### ❌ Don't: Make too many E2E tests
```python
# Bad - testing every edge case in E2E (expensive and slow)
@pytest.mark.e2e
async def test_exam_generation_with_1_question():
    ...

@pytest.mark.e2e
async def test_exam_generation_with_5_questions():
    ...

@pytest.mark.e2e
async def test_exam_generation_with_10_questions():
    ...
```

### ✅ Do: Test critical paths only
```python
# Good - one comprehensive E2E test
@pytest.mark.e2e
async def test_exam_generation_flow():
    # Test with realistic question count
    ...
```

### ❌ Don't: Ignore API rate limits
```python
# Bad - may hit rate limits
for i in range(100):
    await client.generate_exam(...)
```

### ✅ Do: Respect rate limits
```python
# Good - add delays if needed
import asyncio

for i in range(10):
    await client.generate_exam(...)
    await asyncio.sleep(1)  # Respect rate limits
```

---

## 📊 Monitoring E2E Tests

### Track Metrics
- **Success rate** - % of passing tests
- **API costs** - Cost per test run
- **Execution time** - How long tests take
- **Flakiness** - Tests that fail intermittently

### Log API Calls
```python
import logging

logger = logging.getLogger(__name__)

@pytest.mark.e2e
async def test_something():
    logger.info("Starting E2E test: exam generation")
    logger.info(f"Using model: {settings.ai_model}")

    start_time = time.time()
    result = await generate_exam()
    duration = time.time() - start_time

    logger.info(f"Test completed in {duration:.2f}s")
```

---

## 📚 Best Practices

1. **Keep E2E tests minimal** - Only test critical flows
2. **Use realistic data** - But keep it small to save costs
3. **Handle flakiness** - Retry on transient failures
4. **Clean up data** - Delete created resources
5. **Monitor costs** - Track API usage
6. **Run selectively** - Not on every commit
7. **Use test accounts** - Separate from production
8. **Document dependencies** - API keys, services required

---

## 🔗 Related

- [Unit Tests Guide](../unit/README.md) - Testing isolated components
- [Integration Tests Guide](../integration/README.md) - Testing with real database
- [Main Testing Guide](../README.md) - Overview and quick start

---

**Remember:** E2E tests provide **highest confidence** but are **slowest and most expensive** - use them wisely! 💎
