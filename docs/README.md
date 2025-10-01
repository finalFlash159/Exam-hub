# 📚 Exam Hub - Documentation

**AI-Powered Exam Generation System**

Built with FastAPI, SQLAlchemy, and Multi-Provider AI Integration (OpenAI GPT, Google Gemini)

---

## 🚀 Quick Start

### For Developers
1. **Setup:** [deployment/setup.md](deployment/setup.md) - Environment setup & installation
2. **Architecture:** [architecture/system-design.md](architecture/system-design.md) - System design & structure
3. **API Reference:** [api/endpoints.md](api/endpoints.md) - Complete API documentation
4. **Testing:** [../backend/tests/README.md](../backend/tests/README.md) - Testing guide

### For Operators
- **CLI Commands:** [cli-commands.md](cli-commands.md) - All commands reference
- **Deployment:** [deployment/setup.md](deployment/setup.md) - Production setup

---

## 📖 Documentation Structure

```
docs/
├── README.md                      # 👈 You are here
├── cli-commands.md                # CLI commands guide
│
├── api/                           # API documentation
│   ├── endpoints.md              # All API endpoints
│   ├── upload-api.md             # File upload API
│   └── ai-endpoints.md           # AI/Exam generation API
│
├── architecture/                  # Architecture details
│   ├── system-design.md          # High-level system design
│   ├── database-design.md        # Database schema
│   └── genai-architecture.md     # AI module design
│
├── security/                      # Security documentation
│   ├── authentication.md         # Auth & JWT
│   ├── authorization.md          # RBAC & permissions
│   └── file-security.md          # File upload security
│
└── deployment/                    # Deployment guides
    └── setup.md                   # Setup & configuration
```

---

## 🏗️ System Overview

### Architecture Pattern
**Layered Architecture** (Clean Architecture principles)

```
┌─────────────────────────────────────────┐
│          API Layer (FastAPI)            │
│   /auth  /exam  /upload  /health        │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Service Layer                    │
│   Auth  Exam  Upload  Document  GenAI   │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Repository Layer (Data Access)      │
│   User  Exam  File  (BaseRepository)    │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│    Database (SQLAlchemy Async ORM)      │
│   SQLite (dev) / PostgreSQL (prod)      │
└──────────────────────────────────────────┘
```

### Key Features

✅ **Authentication & Authorization**
- JWT-based auth (access + refresh tokens)
- Argon2 password hashing
- Email verification
- Password reset flow
- Role-based access control (USER, ADMIN)

✅ **Rate Limiting**
- Redis-based rate limiting
- Configurable per endpoint type
- Auth endpoints: 3-5 requests/min
- Exam generation: 10 requests/min
- General API: 100-200 requests/min

✅ **AI Integration (GenAI Module)**
- Multi-provider support (OpenAI GPT, Google Gemini, Mock)
- Factory pattern with client caching
- YAML-based prompt templates (Jinja2)
- Automatic retry with exponential backoff
- Response normalization

✅ **File Upload & Processing**
- Secure upload with validation
- Filename sanitization (prevent path traversal)
- Duplicate detection (SHA-256 hashing)
- Content extraction (PDF, DOCX, TXT)
- User-scoped file management

✅ **Security**
- Input validation (Pydantic)
- CORS configuration (specific origins only)
- File sanitization
- Ownership validation
- Rate limiting

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.104.1 |
| **Database** | SQLAlchemy 2.0 (Async) |
| **Auth** | JWT + Argon2 |
| **AI/LLM** | LangChain + OpenAI + Gemini |
| **Caching** | Redis 7+ |
| **Email** | Brevo (Sendinblue) |
| **Testing** | pytest + pytest-asyncio |
| **Docs** | OpenAPI (Swagger) |

---

## 📊 Project Status

### ✅ Completed Features
- ✅ Authentication system (JWT, email verification, password reset)
- ✅ File upload & processing pipeline
- ✅ AI-powered exam generation (multi-provider)
- ✅ Rate limiting with Redis
- ✅ Database schema with relationships
- ✅ API documentation (auto-generated)
- ✅ Security hardening (CORS, sanitization, rate limits)
- ✅ Admin tools (CLI)

### 🔄 Current Version
**v3.0** - Production-Ready with Rate Limiting

### 🎯 API Endpoints

**Authentication** (`/auth`)
- `POST /register` - User registration
- `POST /login` - User login
- `POST /verify-email` - Email verification
- `POST /forgot-password` - Password reset request
- `POST /reset-password` - Password reset
- `POST /refresh-token` - Refresh access token
- `POST /logout` - User logout

**Exam Management** (`/exam`)
- `POST /generate` - Generate exam from content (AI)
- `POST /save` - Save exam to database
- `GET /{exam_id}` - Get exam by ID
- `GET /` - List user's exams
- `GET /admin/all` - Admin: list all exams

**File Upload** (`/upload`)
- `POST /` - Upload file
- `GET /` - List user's files
- `GET /{file_id}` - Get file info
- `DELETE /{file_id}` - Delete file
- `POST /{file_id}/process` - Process file
- `GET /{file_id}/content` - Get extracted content

**Health** (`/health`)
- `GET /health` - System health (DB, Redis, API)

---

## 🔐 Environment Variables

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./exam_hub.db

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis (Rate Limiting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
RATE_LIMIT_ENABLED=true

# AI Providers
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...
DEFAULT_AI_PROVIDER=gemini

# Email (Brevo)
BREVO_API_KEY=xkeysib-...
FROM_EMAIL=noreply@examhub.com
FRONTEND_URL=http://localhost:3000
```

---

## 📝 Development Workflow

### 1. Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Database
```bash
alembic upgrade head
python tests/create_superuser.py
```

### 3. Redis
```bash
docker-compose up redis -d
```

### 4. Run
```bash
uvicorn app.main:app --reload
```

### 5. Test
```bash
pytest tests/ -v
```

---

## 📞 Resources

- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **Health Check:** http://localhost:8000/health
- **Backend Code:** `/backend/app/`
- **Database:** SQLite (`exam_hub.db`) or PostgreSQL

---

## 🤝 Support

For detailed information:
- **Architecture:** [architecture/system-design.md](architecture/system-design.md)
- **API Reference:** [api/endpoints.md](api/endpoints.md)
- **Setup Guide:** [deployment/setup.md](deployment/setup.md)
- **Security:** [security/](security/)
- **Testing:** [../backend/tests/README.md](../backend/tests/README.md)

---

**Built with ❤️ using FastAPI & Modern Python**
