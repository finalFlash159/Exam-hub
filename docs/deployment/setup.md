# Development Setup Guide

## 🚀 QUICK START

### **Prerequisites**
- **Python:** 3.11+ (recommended: 3.12)
- **Node.js:** 18+ (for frontend)
- **Git:** Latest version
- **Google Gemini API Key:** [Get here](https://makersuite.google.com/app/apikey)

---

## 🛠️ BACKEND SETUP

### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/Exam-hub.git
cd Exam-hub
```

### **2. Backend Environment**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Environment Configuration**
```bash
# Copy environment template
cp ../deployment.env.example .env

# Edit .env file with your settings
nano .env
```

**Required Environment Variables:**
```env
# Core Settings
ENV=development
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite+aiosqlite:///./exam_hub.db

# AI Service
GEMINI_API_KEY=your_google_gemini_api_key_here

# Email Service (Brevo)
BREVO_API_KEY=your_brevo_api_key
FROM_EMAIL=noreply@yourapp.com
FROM_NAME=Your App Name
FRONTEND_URL=http://localhost:3000

# Optional Settings
PORT=5001
DEBUG=true
```

### **4. Database Setup**
```bash
# Initialize database
alembic upgrade head

# Verify database creation
ls -la exam_hub.db
```

### **5. Start Backend Server**
```bash
# Development server with auto-reload
python -m app.main

# Alternative: Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload
```

**Verify Backend:**
- API: http://localhost:5001
- Health: http://localhost:5001/health
- Docs: http://localhost:5001/docs

---

## 🎨 FRONTEND SETUP

### **1. Frontend Environment**
```bash
cd ../exam-app

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_BACKEND_URL=http://localhost:5001" > .env.local
```

### **2. Start Frontend Server**
```bash
# Development server
npm start
```

**Verify Frontend:**
- App: http://localhost:3000
- Auto-opens in browser

---

## 🧪 VERIFICATION TESTS

### **1. Backend Health Check**
```bash
curl http://localhost:5001/health | jq
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "database": "connected",
  "components": {
    "api": "ok",
    "database": "ok"
  }
}
```

### **2. Test Authentication Flow**
```bash
# Register user
curl -X POST "http://localhost:5001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123", 
    "full_name": "Test User"
  }' | jq

# Expected: User created, verification email sent
```

### **3. Test Exam Generation**
```bash
# Generate questions
curl -X POST "http://localhost:5001/exam/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "file_content": "Machine learning is a branch of artificial intelligence that focuses on algorithms and statistical models.",
    "num_questions": 2,
    "subject": "Machine Learning"
  }' | jq

# Expected: Mock questions generated
```

### **4. Test File Upload**
```bash
# Create test file
echo "Test content for upload" > test.txt

# Upload file
curl -X POST "http://localhost:5001/upload/upload" \
  -F "file=@test.txt" | jq

# Expected: File uploaded successfully
```

---

## 🗂️ PROJECT STRUCTURE

```
Exam-hub/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── repositories/   # Data access
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── utils/          # Utilities
│   │   └── core/           # Configuration
│   ├── tests/              # Backend tests
│   ├── uploads/            # Uploaded files
│   ├── requirements.txt    # Python dependencies
│   └── alembic/            # Database migrations
├── exam-app/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # State management
│   │   ├── hooks/          # Custom hooks
│   │   └── data/           # Static data
│   └── package.json        # Node dependencies
├── docs/                   # Documentation
└── docker-compose.yml      # Container setup
```

---

## 🐳 DOCKER DEVELOPMENT

### **Option 1: Docker Compose (Full Stack)**
```bash
# Copy environment
cp deployment.env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Option 2: Backend Only**
```bash
cd backend

# Build image
docker build -t exam-hub-backend .

# Run container
docker run -p 5001:5001 \
  -e GEMINI_API_KEY=your_key \
  -e DATABASE_URL=sqlite+aiosqlite:///./exam_hub.db \
  exam-hub-backend
```

---

## 🧪 RUNNING TESTS

### **Backend Tests**
```bash
cd backend

# Install test dependencies (included in requirements.txt)
pip install pytest pytest-cov pytest-mock

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app tests/

# Run specific test file
python -m pytest tests/test_auth_service.py -v
```

### **Frontend Tests**
```bash
cd exam-app

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage --watchAll=false
```

---

## 🔧 DEVELOPMENT TOOLS

### **Code Quality**
```bash
# Backend formatting
pip install black isort flake8
black app/
isort app/
flake8 app/

# Frontend formatting  
cd exam-app
npm run format  # If configured
```

### **Database Management**
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### **Useful Development Commands**
```bash
# Backend hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 5001

# Frontend with custom port
cd exam-app && PORT=3001 npm start

# View database
sqlite3 backend/exam_hub.db
.tables
.schema users
```

---

## 🚨 TROUBLESHOOTING

### **Common Issues**

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.11+

# Check virtual environment
which python  # Should point to venv

# Check dependencies
pip list | grep fastapi

# Check environment variables
echo $GEMINI_API_KEY
```

**Database errors:**
```bash
# Reset database
rm backend/exam_hub.db
cd backend && alembic upgrade head

# Check migrations
alembic current
alembic history
```

**Frontend connection issues:**
```bash
# Check backend is running
curl http://localhost:5001/health

# Check CORS settings
# Backend should allow frontend origin

# Check environment variables
cat exam-app/.env.local
```

**File upload fails:**
```bash
# Check uploads directory exists
mkdir -p backend/uploads

# Check file permissions
ls -la backend/uploads/

# Check file size limits (16MB default)
```

### **Port Conflicts**
```bash
# Find process using port
lsof -i :5001
lsof -i :3000

# Kill process
kill -9 PID

# Use different ports
PORT=5002 python -m app.main
PORT=3001 npm start
```

### **API Key Issues**
```bash
# Test Gemini API key
curl -H "x-goog-api-key: YOUR_API_KEY" \
  "https://generativelanguage.googleapis.com/v1/models"

# Check environment loading
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
```

---

## 📈 PERFORMANCE TIPS

### **Backend Optimization**
- Use SQLite for development (faster than PostgreSQL setup)
- Enable database echo only when debugging: `DATABASE_ECHO=false`
- Use `--reload` only in development
- Monitor memory usage with large file uploads

### **Frontend Optimization**
- Use `npm start` for development (hot reload)
- Clear browser cache if seeing old versions
- Use React DevTools for debugging
- Monitor network requests in browser DevTools

---

## �� NEXT STEPS

After successful setup:

1. **Explore API:** Visit http://localhost:5001/docs
2. **Test Frontend:** Create an exam end-to-end
3. **Read Documentation:** Check `docs/` folder
4. **Review Code:** Understand the clean architecture
5. **Run Tests:** Ensure everything works
6. **Start Development:** Pick a feature to implement

---

*Setup guide for Exam Hub development environment*
