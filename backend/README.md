# 📚 Exam Hub Backend

**AI-Powered Exam Generation System - Backend API**

FastAPI + SQLAlchemy + Multi-Provider AI Integration (OpenAI GPT, Google Gemini)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Redis 7+ (for rate limiting)
- SQLite (dev) or PostgreSQL (production)

### Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Start Redis (via Docker)
docker-compose up redis -d

# 5. Initialize database
alembic upgrade head
python tests/create_superuser.py

# 6. Run server
uvicorn app.main:app --reload

# 7. Access API docs
# http://localhost:8000/docs
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                      # API endpoints (FastAPI routers)
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── exam.py              # Exam management endpoints
│   │   └── upload.py            # File upload endpoints
│   │
│   ├── services/                 # Business logic layer
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── exam_service.py      # Exam generation logic
│   │   ├── upload_service.py    # File upload logic
│   │   └── document_service.py  # Document processing
│   │
│   ├── repositories/             # Data access layer
│   │   ├── base_repository.py   # Generic CRUD operations
│   │   ├── user_repository.py   # User data access
│   │   ├── exam_repository.py   # Exam data access
│   │   └── file_repository.py   # File data access
│   │
│   ├── models/                   # Database models (SQLAlchemy)
│   │   ├── user.py              # User model
│   │   ├── exam.py              # Exam model
│   │   └── file.py              # File model
│   │
│   ├── schemas/                  # Pydantic schemas (validation)
│   │   ├── auth_schemas.py      # Auth request/response schemas
│   │   ├── exam_schemas.py      # Exam schemas
│   │   └── file_schemas.py      # File schemas
│   │
│   ├── genai/                    # AI integration module
│   │   ├── clients/             # AI client implementations
│   │   │   ├── factory.py       # Client factory (OpenAI/Gemini/Mock)
│   │   │   ├── openai_client.py # OpenAI GPT integration
│   │   │   ├── gemini_client.py # Google Gemini integration
│   │   │   └── mock_client.py   # Mock client (testing)
│   │   ├── prompts/             # YAML prompt templates
│   │   │   ├── loader.py        # Jinja2 template loader
│   │   │   └── templates/       # Prompt YAML files
│   │   └── utils/               # AI utilities
│   │       └── retry.py         # Exponential backoff retry
│   │
│   ├── auth/                     # Authentication & authorization
│   │   ├── middleware.py        # JWT authentication middleware
│   │   └── dependencies.py      # Auth dependencies
│   │
│   ├── core/                     # Core configuration
│   │   ├── config.py            # Application settings
│   │   ├── security.py          # Security utilities (JWT, Argon2)
│   │   └── rate_limit.py        # Rate limiting decorators
│   │
│   ├── database/                 # Database infrastructure
│   │   ├── connection.py        # Async database session
│   │   └── redis.py             # Redis connection manager
│   │
│   └── main.py                   # FastAPI application entry point
│
├── alembic/                      # Database migrations
│   ├── versions/                # Migration files
│   └── env.py                   # Alembic configuration
│
├── tests/                        # Test suite
│   ├── genai/                   # GenAI module tests
│   ├── conftest.py              # Pytest fixtures
│   └── README.md                # Testing documentation
│
├── requirements.txt              # Python dependencies
├── .env                         # Environment variables (DO NOT COMMIT)
└── pytest.ini                   # Pytest configuration
```

---

## 🏗️ Architecture

### Layered Architecture Pattern

```
┌─────────────────────────────────────────┐
│       API Layer (FastAPI Routers)       │
│   /auth  /exam  /upload  /health        │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Service Layer                    │
│   Auth  Exam  Upload  Document  GenAI   │
│   (Business Logic)                       │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Repository Layer                    │
│   User  Exam  File  (Generic CRUD)      │
│   (Data Access)                          │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│    Database (SQLAlchemy Async ORM)      │
│   SQLite (dev) / PostgreSQL (prod)      │
└──────────────────────────────────────────┘
```

### Design Patterns

- **Repository Pattern**: Generic base repository with CRUD operations
- **Factory Pattern**: AI client factory (OpenAI/Gemini/Mock)
- **Strategy Pattern**: Document processors (PDF/DOCX/TXT)
- **Dependency Injection**: FastAPI's dependency system
- **Middleware Pattern**: JWT authentication middleware

---

## 🔑 Key Features

### ✅ Authentication & Authorization
- JWT-based auth (access + refresh tokens)
- Argon2 password hashing
- Email verification flow
- Password reset flow
- Role-based access control (USER, ADMIN)

### ✅ Rate Limiting
- Redis-based rate limiting
- Configurable per endpoint type
- Auth endpoints: 3-5 requests/min
- Exam generation: 10 requests/min
- General API: 100-200 requests/min

### ✅ AI Integration (GenAI Module)
- Multi-provider support (OpenAI GPT, Google Gemini, Mock)
- Factory pattern with client caching
- YAML-based prompt templates (Jinja2)
- Automatic retry with exponential backoff
- Response normalization

### ✅ File Upload & Processing
- Secure upload with validation
- Filename sanitization (prevent path traversal)
- Duplicate detection (SHA-256 hashing)
- Content extraction (PDF, DOCX, TXT)
- User-scoped file management

### ✅ Security
- Input validation (Pydantic)
- CORS configuration (specific origins only)
- File sanitization
- Ownership validation
- Rate limiting

---

## 🛠️ Development

### Running the Server

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000

# With custom settings
uvicorn app.main:app --reload --log-level debug
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_service.py -v

# Run with output
pytest -v -s
```

**See [tests/README.md](tests/README.md) for comprehensive testing guide.**

---

## 🔐 Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./exam_hub.db

# Security
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
# REDIS_PASSWORD=your-redis-password  # Production only

# Rate Limiting
RATE_LIMIT_ENABLED=true

# AI Providers
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...
DEFAULT_AI_PROVIDER=gemini

# Email (Brevo/Sendinblue)
BREVO_API_KEY=xkeysib-...
FROM_EMAIL=noreply@examhub.com
FROM_NAME=Exam Hub

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

### Security Notes:
- **Never commit `.env` to git**
- Use strong `SECRET_KEY` (generate with `openssl rand -base64 32`)
- Use Redis password in production
- Restrict CORS origins in production

---

## 📊 API Endpoints

### Authentication (`/auth`)
- `POST /register` - User registration
- `POST /login` - User login
- `POST /verify-email` - Email verification
- `POST /forgot-password` - Password reset request
- `POST /reset-password` - Password reset
- `POST /refresh-token` - Refresh access token
- `POST /logout` - User logout

### Exam Management (`/exam`)
- `POST /generate` - Generate exam from content (AI)
- `POST /save` - Save exam to database
- `GET /{exam_id}` - Get exam by ID
- `GET /` - List user's exams
- `GET /admin/all` - Admin: list all exams

### File Upload (`/upload`)
- `POST /` - Upload file
- `GET /` - List user's files
- `GET /{file_id}` - Get file info
- `DELETE /{file_id}` - Delete file
- `POST /{file_id}/process` - Process file
- `GET /{file_id}/content` - Get extracted content

### Health (`/health`)
- `GET /health` - System health (DB, Redis, API)

**Full API documentation: http://localhost:8000/docs**

---

## 🧪 Testing

### Quick Test Commands

```bash
# All tests
pytest

# Specific module
pytest tests/genai/ -v
pytest tests/test_auth_service.py -v

# With coverage
pytest --cov=app --cov-report=term-missing

# Parallel execution
pytest -n auto
```

### Test Structure

```
tests/
├── genai/                         # GenAI module tests
│   ├── test_gemini_client_integration.py
│   ├── test_openai_client_integration.py
│   ├── test_prompts_loader.py
│   └── test_factory.py
├── test_auth_service.py           # Authentication tests
├── test_upload_service.py         # File upload tests
├── test_document_service.py       # Document processing tests
└── conftest.py                    # Shared fixtures
```

**See [tests/README.md](tests/README.md) for complete testing guide.**

---

## 📚 Documentation

- **Main Docs**: [../docs/README.md](../docs/README.md)
- **API Reference**: [../docs/api/endpoints.md](../docs/api/endpoints.md)
- **Architecture**: [../docs/architecture/system-design.md](../docs/architecture/system-design.md)
- **Security**: [../docs/security/](../docs/security/)
- **Testing**: [tests/README.md](tests/README.md)

---

## 🐛 Common Issues

### Issue: "event loop closed" in tests
**Solution**: Ensure `pytest.ini` has `asyncio_mode = auto`

### Issue: Redis connection failed
**Solution**: Start Redis with `docker-compose up redis -d`

### Issue: Database migration conflicts
**Solution**: Reset migrations or manually resolve conflicts in `alembic/versions/`

### Issue: Rate limiting not working
**Solution**: Check `RATE_LIMIT_ENABLED=true` in `.env` and Redis is running

---

## 🤝 Contributing

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Add tests for new features

### Git Workflow
1. Create feature branch from `main`
2. Make changes and add tests
3. Run tests: `pytest`
4. Commit with descriptive message
5. Create pull request

### Commit Message Format
```
<type>: <subject>

<body>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

---

## 📞 Resources

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Pytest Docs**: https://docs.pytest.org/

---

**Built with ❤️ using FastAPI & Modern Python**
