# 📋 BACKEND ARCHITECTURE MIGRATION PLAN

## 🎯 **TỔNG QUAN**

### **Mục tiêu:**
- Chuyển từ **flat structure** sang **layered architecture**
- Tách biệt **business logic** khỏi API endpoints  
- Chuẩn bị cho **database integration** và **authentication**
- Tạo **scalable foundation** cho tương lai

### **Nguyên tắc Migration:**
- ✅ **Zero Downtime** - Luôn có version working
- ✅ **Incremental** - Từng bước nhỏ, test sau mỗi step
- ✅ **Backward Compatible** - Không break existing APIs
- ✅ **Rollback Ready** - Có thể quay lại nếu cần

---

## 📊 **PHÂN TÍCH HIỆN TRẠNG**

### **Cấu trúc hiện tại:**
```
backend/
├── app.py                    # Main app (OK)
├── document_processor.py     # ❌ ROOT - cần move
├── llm_generator.py          # ❌ ROOT - cần move
├── api/                      # ✅ GOOD structure
│   ├── exam.py              # ❌ Contains business logic
│   ├── upload.py            # ❌ Contains business logic  
│   └── health.py            # ✅ Simple endpoint
├── core/                     # ✅ GOOD structure
│   ├── config.py            # ❌ Có hardcoded paths
│   └── logging_config.py    # ✅ OK
├── models/                   # ✅ GOOD but limited
│   └── exam_models.py       # ✅ OK (Pydantic schemas)
└── tests/                    # ✅ GOOD structure
```

### **Dependency Issues:**
```
❌ api/exam.py → document_processor (ROOT LEVEL)
❌ api/exam.py → llm_generator (ROOT LEVEL)  
❌ api/upload.py → document_processor (ROOT LEVEL)
❌ core/config.py → hardcoded frontend paths
❌ Direct file system operations in API
```

### **Missing Layers:**
```
❌ Services Layer (business logic)
❌ Repository Layer (data access) 
❌ Database Models (SQLAlchemy)
❌ Utilities Package (helpers)
❌ Exception Handling (custom exceptions)
```

---

## 🎯 **CẤU TRÚC MỤC TIÊU**

### **Target Architecture:**
```
backend/
├── app/                      # Main application package
│   ├── main.py              # FastAPI app factory
│   ├── api/                 # API layer (routes only)
│   │   ├── endpoints/       # Endpoint definitions
│   │   │   ├── auth.py      # Authentication
│   │   │   ├── exams.py     # Exam management
│   │   │   ├── upload.py    # File upload
│   │   │   └── health.py    # Health checks
│   │   └── dependencies.py  # API dependencies
│   ├── core/                # Core functionality
│   │   ├── config.py        # Settings management
│   │   ├── security.py      # Auth & security
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── logging.py       # Logging setup
│   ├── services/            # Business logic layer
│   │   ├── exam_service.py  # Exam business logic
│   │   ├── upload_service.py # Upload business logic
│   │   ├── ai_service.py    # AI/LLM integration
│   │   └── document_service.py # Document processing
│   ├── repositories/        # Data access layer
│   │   ├── base.py          # Base repository
│   │   ├── exam_repository.py # Exam data access
│   │   └── file_repository.py # File operations
│   ├── models/              # Database models
│   │   ├── base.py          # SQLAlchemy base
│   │   ├── exam.py          # Exam model
│   │   └── user.py          # User model
│   ├── schemas/             # Pydantic schemas
│   │   ├── exam.py          # Exam schemas
│   │   └── user.py          # User schemas
│   └── utils/               # Utility functions
│       ├── document_processor.py # Document utilities
│       ├── ai_generator.py       # AI utilities
│       └── helpers.py            # General helpers
├── tests/                   # Test suite
├── alembic/                 # Database migrations
└── scripts/                 # Utility scripts
```

---

## 🚀 **MIGRATION PHASES**

## **PHASE 1: FOUNDATION SETUP**
**Timeline:** 1-2 days  
**Risk:** 🟢 Low

### **Step 1.1: Create Directory Structure**
```bash
mkdir -p app/{api/endpoints,core,services,repositories,models,schemas,utils}
mkdir -p scripts alembic
```

### **Step 1.2: Create Base Files**
```bash
# Create __init__.py files
find app -type d -exec touch {}/__init__.py \;

# Create main.py (new app entry point)
touch app/main.py
```

### **Step 1.3: Backup Current State**
```bash
git add .
git commit -m "✅ Phase 1.1: Directory structure created"
```

### **Success Criteria:**
- [ ] All directories created
- [ ] __init__.py files in place
- [ ] Git commit successful
- [ ] Original files still in place and working

---

## **PHASE 2: MOVE UTILITIES** 
**Timeline:** 1-2 days  
**Risk:** 🟡 Medium

### **Step 2.1: Move document_processor.py**
```bash
# Move file
mv document_processor.py app/utils/document_processor.py

# Create compatibility import (temporary)
echo "from app.utils.document_processor import DocumentProcessor" > document_processor.py
```

### **Step 2.2: Move llm_generator.py**
```bash
# Move file  
mv llm_generator.py app/utils/ai_generator.py

# Create compatibility import (temporary)
echo "from app.utils.ai_generator import ExamGenerator" > llm_generator.py
```

### **Step 2.3: Test Compatibility**
```bash
# Test imports still work
python -c "from document_processor import DocumentProcessor; print('✅ Document processor OK')"
python -c "from llm_generator import ExamGenerator; print('✅ LLM generator OK')"

# Test API endpoints
python -m pytest tests/ -v
```

### **Step 2.4: Update Internal Imports**
```python
# In app/utils/ai_generator.py
# Update: from core.config import create_gemini_instance
# To: from app.core.config import create_gemini_instance
```

### **Success Criteria:**
- [ ] Files moved successfully
- [ ] Compatibility imports working
- [ ] All tests passing
- [ ] API endpoints still functional

---

## **PHASE 3: CREATE SERVICES LAYER**
**Timeline:** 2-3 days  
**Risk:** 🟡 Medium

### **Step 3.1: Create Exam Service**
```python
# app/services/exam_service.py
class ExamService:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.ai_generator = ExamGenerator()
    
    async def generate_exam_from_file(self, file_path, title, count):
        # Move business logic from api/exam.py here
        pass
    
    async def save_exam(self, exam_data):
        # Move save logic here
        pass
```

### **Step 3.2: Create Upload Service**
```python
# app/services/upload_service.py  
class UploadService:
    async def save_uploaded_file(self, file):
        # Move upload logic here
        pass
```

### **Step 3.3: Update API Endpoints**
```python
# api/endpoints/exams.py (new)
from app.services.exam_service import ExamService

@router.post("/generate-exam")
async def generate_exam(request):
    service = ExamService()
    return await service.generate_exam_from_file(...)
```

### **Success Criteria:**
- [ ] Services created with business logic
- [ ] API endpoints use services
- [ ] No business logic in API layer
- [ ] All functionality preserved

---

## **PHASE 4: DATABASE INTEGRATION**
**Timeline:** 3-4 days  
**Risk:** 🔴 High

### **Step 4.1: Add Database Dependencies**
```bash
# Update requirements.txt
pip install sqlalchemy alembic asyncpg
```

### **Step 4.2: Create Models**
```python
# app/models/exam.py
class Exam(Base):
    id = Column(Integer, primary_key=True)
    title = Column(String)
    questions = relationship("Question", back_populates="exam")
```

### **Step 4.3: Create Repositories**
```python
# app/repositories/exam_repository.py
class ExamRepository:
    async def create(self, exam_data):
        # Database operations
        pass
```

### **Step 4.4: Update Services to Use DB**
```python
# app/services/exam_service.py
class ExamService:
    def __init__(self):
        self.exam_repo = ExamRepository()
    
    async def save_exam(self, exam_data):
        return await self.exam_repo.create(exam_data)
```

### **Success Criteria:**
- [ ] Database models defined
- [ ] Repositories implemented
- [ ] Services use repositories
- [ ] Data persisted to database
- [ ] File system backup still working

---

## **PHASE 5: AUTHENTICATION & SECURITY**
**Timeline:** 2-3 days  
**Risk:** 🟡 Medium

### **Step 5.1: Add Auth Dependencies**
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

### **Step 5.2: Create User Models & Services**
```python
# app/models/user.py
# app/services/auth_service.py
# app/api/endpoints/auth.py
```

### **Step 5.3: Protect Endpoints**
```python
# Add JWT middleware
# Protect exam generation endpoints
```

---

## **PHASE 6: CLEANUP & OPTIMIZATION**
**Timeline:** 1-2 days  
**Risk:** 🟢 Low

### **Step 6.1: Remove Compatibility Imports**
```bash
rm document_processor.py
rm llm_generator.py  
```

### **Step 6.2: Update app.py**
```python
# Update imports to use app.main
from app.main import create_app
app = create_app()
```

### **Step 6.3: Final Testing**
```bash
# Full test suite
python -m pytest tests/ -v --cov=app
```

---

## 🧪 **TESTING STRATEGY**

### **After Each Phase:**
1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test component interactions  
3. **API Tests** - Test endpoint functionality
4. **Manual Testing** - Test UI workflow

### **Rollback Plan:**
```bash
# If anything breaks:
git reset --hard HEAD~1  # Go back one commit
# Or restore from backup
cp -r backend_backup/* backend/
```

---

## 📊 **SUCCESS METRICS**

### **Code Quality:**
- [ ] No business logic in API endpoints
- [ ] Clear separation of concerns
- [ ] All imports working correctly
- [ ] Test coverage > 80%

### **Functionality:**
- [ ] All existing APIs working
- [ ] File upload working
- [ ] Exam generation working
- [ ] Exam saving working

### **Architecture:**
- [ ] Services layer implemented
- [ ] Repository pattern implemented
- [ ] Database integration complete
- [ ] Authentication working

---

## ⚠️ **RISK MITIGATION**

### **High Risk Areas:**
1. **Import Changes** - Many files import moved modules
2. **Path Dependencies** - Frontend path references
3. **File Operations** - Existing file save logic
4. **Database Migration** - Data migration complexity

### **Mitigation Strategies:**
1. **Compatibility Imports** - Temporary imports during transition
2. **Feature Flags** - Toggle between old/new implementations
3. **Incremental Testing** - Test after each small change
4. **Backup Strategy** - Multiple backup points

---

## 📅 **TIMELINE ESTIMATE**

| Phase | Duration | Risk | Dependencies |
|-------|----------|------|--------------|
| 1. Foundation | 1-2 days | Low | None |
| 2. Move Utils | 1-2 days | Medium | Phase 1 |
| 3. Services | 2-3 days | Medium | Phase 2 |
| 4. Database | 3-4 days | High | Phase 3 |
| 5. Auth | 2-3 days | Medium | Phase 4 |
| 6. Cleanup | 1-2 days | Low | Phase 5 |

**Total: 10-16 days**

---

## 🎯 **NEXT IMMEDIATE STEPS**

1. **Review this plan** - Đảm bảo bạn hiểu và đồng ý
2. **Execute Phase 1.1** - Tạo directory structure
3. **Test current functionality** - Đảm bảo everything working
4. **Begin Phase 2** - Move utility files

---

*📝 Note: File này sẽ được update trong quá trình migration để track progress* 