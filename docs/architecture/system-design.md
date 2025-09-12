# System Architecture Documentation

## 🏗️ SYSTEM OVERVIEW

**Exam Hub** là một hệ thống tạo đề thi thông minh sử dụng AI, được thiết kế theo **Clean Architecture** với **Domain-Driven Design**.

### **Core Purpose**
- **File Upload System** - Secure document upload with validation & database integration
- **AI-Powered Generation** - Question generation từ uploaded files using Google Gemini
- **User Authentication** - JWT-based auth with role-based access control
- **Exam Management** - Complete exam lifecycle with user-scoped access
- **Security-First Design** - Comprehensive security measures across all layers

### **Architecture Pattern**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   React.js      │◄──►│   FastAPI       │◄──►│   Services      │
│   Material-UI   │    │   Clean Arch    │    │   Gemini AI     │
└─────────────────┘    └─────────────────┘    │   Brevo Email   │
                                              └─────────────────┘
```

### **Technology Stack**

**Backend:**
- **Framework:** FastAPI 0.104.1 + Uvicorn
- **Architecture:** Clean Architecture (Layered)
- **Database:** SQLAlchemy 2.0 + SQLite/PostgreSQL
- **Authentication:** JWT + Argon2 password hashing
- **File Upload:** Secure upload with SHA-256 hashing & validation
- **AI Integration:** LangChain + Google Gemini API
- **Email:** Brevo API integration
- **Document Processing:** PyMuPDF + python-docx
- **Security:** Comprehensive validation, sanitization & access control

**Frontend:**
- **Framework:** React.js + Material-UI
- **State Management:** Context API
- **Build Tool:** Create React App
- **Deployment:** Vercel

---

## 🏛️ BACKEND ARCHITECTURE

### **Layer Structure**
```
app/
├── api/           # 🌐 Presentation Layer (FastAPI endpoints)
├── services/      # 💼 Application Layer (Business logic)
├── repositories/  # ��️ Infrastructure Layer (Data access)
├── models/        # 📊 Domain Layer (Database models)
├── schemas/       # 📋 Data Transfer Objects (Pydantic)
├── utils/         # 🛠️ Utilities & helpers
└── core/          # ⚙️ Configuration & settings
```

### **Dependency Flow**
```
API Layer → Service Layer → Repository Layer → Database
    ↓           ↓              ↓
  Schemas   Business Logic   Data Models
```

### **Key Design Principles**
- ✅ **Separation of Concerns:** Mỗi layer có responsibility riêng
- ✅ **Dependency Injection:** Services inject repositories
- ✅ **Single Responsibility:** Mỗi class có 1 mục đích
- ✅ **Interface Segregation:** Clean abstractions
- ✅ **Async/Await:** Non-blocking I/O operations

---

## 🔄 BUSINESS WORKFLOWS

### **1. Document to Exam Workflow**
```
1. File Upload
   ├── Validate file type (PDF, DOCX, TXT)
   ├── Check file size (<16MB)
   ├── Generate unique file ID
   └── Store in uploads/ directory

2. Content Extraction (TODO)
   ├── PDF: PyMuPDF text extraction
   ├── DOCX: python-docx parsing
   └── TXT: Direct content reading

3. Question Generation
   ├── AI prompt engineering
   ├── Google Gemini API call
   ├── Response parsing & validation
   └── Mock generation (development)

4. Exam Creation
   ├── User review & editing
   ├── Metadata input (title, duration)
   ├── Database persistence
   └── Question relationship setup
```

### **2. User Authentication Workflow**
```
Registration → Email Verification → Login → Protected Access
     ↓              ↓                ↓           ↓
  Hash Password  Send Email      Generate JWT  Validate Token
  Store User     Token Check     Refresh Flow  Check Permissions
```

### **3. Exam Taking Workflow (Frontend)**
```
Browse Exams → Start Exam → Answer Questions → Submit → Results
     ↓             ↓              ↓             ↓        ↓
  List API    Timer Start    Track Progress  Calculate  Display
  Get Details  Load Qs       Save Answers    Score     Analytics
```

---

## 🚀 DEVELOPMENT STATUS

### **✅ COMPLETED MODULES**

**Core Infrastructure:**
- ✅ FastAPI application with lifespan management
- ✅ Database connection & migration setup
- ✅ Clean architecture implementation
- ✅ Async/await patterns throughout
- ✅ Comprehensive error handling

**Authentication System:**
- ✅ Complete user registration flow
- ✅ JWT token generation & refresh
- ✅ Email verification system
- ✅ Password reset functionality
- ✅ Secure password hashing
- ✅ JWT authentication middleware
- ✅ Protected route dependencies
- ✅ Role-based access control (USER/ADMIN)
- ✅ Resource ownership validation

**Exam Management:**
- ✅ Question generation (mock implementation)
- ✅ Exam CRUD operations with user scoping
- ✅ Database relationship loading
- ✅ Proper data validation
- ✅ Creator-based access control
- ✅ User-scoped exam listing
- ✅ Admin exam management endpoints

**File Upload:**
- ✅ Multi-format file support
- ✅ File validation & storage
- ✅ File management endpoints
- ✅ Metadata tracking

**Security & Authorization:**
- ✅ Complete authentication middleware
- ✅ User-scoped data access
- ✅ Ownership validation for resources
- ✅ Admin role separation
- ✅ Protected API endpoints

### **⚠️ HIGH PRIORITY TODO**

**Integration Features:**
- ⚠️ Apply authentication to upload module
- ⚠️ Document content extraction
- ⚠️ File-to-exam generation flow
- ⚠️ Real AI integration (replace mocks)

**Production Readiness:**
- ⚠️ Comprehensive testing suite
- ⚠️ Performance monitoring
- ⚠️ Production database setup
- ⚠️ Deployment configuration

---

## 🚀 CURRENT IMPLEMENTATION STATUS

### **✅ Phase 1 - COMPLETED (2025-09-12)**
**Core Authentication & Security:**
- JWT authentication with refresh tokens
- Role-based access control (USER/ADMIN)
- Password hashing with Argon2
- Email verification system

**File Upload System:**
- Secure file upload with comprehensive validation
- SHA-256 hash-based duplicate detection
- User-scoped file ownership & access control
- Database integration with metadata tracking
- Admin file management & system statistics
- Path traversal protection & filename sanitization

**API & Documentation:**
- RESTful API with Pydantic schemas
- Auto-generated OpenAPI documentation
- Comprehensive error handling
- Health monitoring endpoints

**Database Architecture:**
- Complete schema with all relationships
- Migration system with Alembic
- Performance indexes
- Transaction safety with rollback

### **🔄 Phase 2 - NEXT (AI Integration)**
- Document content extraction (PDF, DOCX, TXT)
- AI-powered question generation with Google Gemini
- Question validation & quality scoring
- Exam generation from uploaded files

### **📈 FUTURE ENHANCEMENTS**

#### **Phase 3 Features**
- Advanced question types (True/False, Fill-in-blank)
- Exam analytics & reporting
- Bulk exam management
- Advanced AI prompt engineering

#### **Phase 4 Features**
- Multi-language support
- Advanced user roles (Teacher/Student)
- Exam sharing & collaboration
- Mobile application

### **Performance Optimizations**
- Database query optimization
- Caching layer implementation
- File processing optimization
- API response compression

---

*Last updated: $(date)*
