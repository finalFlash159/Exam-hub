# API Endpoints Documentation

## 🌐 API OVERVIEW

**Base URL:** `http://localhost:5001` (development) / `https://your-domain.com` (production)
**API Version:** 3.0.0
**Documentation:** `/docs` (Swagger UI) | `/redoc` (ReDoc)

---

## 🔐 AUTHENTICATION ENDPOINTS

### **POST /auth/register**
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": "user-uuid",
  "email": "user@example.com", 
  "full_name": "John Doe",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Errors:**
- `400`: Email already registered, validation errors
- `500`: Registration failed

---

### **POST /auth/login**
Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "remember_me": false
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user"
  }
}
```

**Errors:**
- `400`: Invalid credentials
- `401`: Email not verified
- `500`: Login failed

---

### **POST /auth/verify-email**
Verify user email address.

**Request Body:**
```json
{
  "token": "email-verification-token"
}
```

**Response (200):**
```json
{
  "message": "Email verified successfully"
}
```

---

### **POST /auth/forgot-password**
Request password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "Password reset email sent"
}
```

---

### **POST /auth/reset-password**
Reset password using reset token.

**Request Body:**
```json
{
  "token": "password-reset-token",
  "new_password": "newsecurepassword123"
}
```

**Response (200):**
```json
{
  "message": "Password reset successfully"
}
```

---

### **POST /auth/refresh-token**
Get new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user"
  }
}
```

---

### **POST /auth/logout**
Logout user and revoke refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

## 📝 EXAM ENDPOINTS

### **POST /exam/generate**
Generate exam questions from text content.
🔒 **REQUIRES AUTHENTICATION**

**Request Body:**
```json
{
  "file_content": "Machine learning is a branch of artificial intelligence...",
  "num_questions": 5,
  "subject": "Machine Learning"
}
```

**Response (201):**
```json
{
  "questions": [
    {
      "question_text": "What is machine learning?",
      "options": [
        "A branch of AI",
        "A programming language", 
        "A database system",
        "A web framework"
      ],
      "correct_answer": "A",
      "explanation": "Machine learning is indeed a branch of artificial intelligence..."
    }
  ],
  "subject": "Machine Learning",
  "total_questions": 5
}
```

**Errors:**
- `400`: Invalid input, text too short
- `500`: Generation failed

---

### **POST /exam/save**
Save generated exam to database.
🔒 **REQUIRES AUTHENTICATION - User-scoped**

**Request Body:**
```json
{
  "title": "Machine Learning Basics",
  "description": "Introduction to ML concepts",
  "duration_minutes": 30,
  "questions": [
    {
      "question_text": "What is machine learning?",
      "options": ["A branch of AI", "A programming language", "A database system", "A web framework"],
      "correct_answer": "A",
      "explanation": "Machine learning is indeed a branch of artificial intelligence..."
    }
  ]
}
```

**Response (201):**
```json
{
  "id": "exam-uuid",
  "title": "Machine Learning Basics",
  "message": "Exam 'Machine Learning Basics' saved successfully"
}
```

**Errors:**
- `400`: Validation errors
- `401`: Authentication required (TODO)
- `500`: Save failed

---

### **GET /exam/{exam_id}**
Get exam details with questions.
🔒 **REQUIRES AUTHENTICATION + OWNERSHIP CHECK**

**Response (200):**
```json
{
  "id": "exam-uuid",
  "title": "Machine Learning Basics",
  "description": "Introduction to ML concepts",
  "duration_minutes": 30,
  "questions": [
    {
      "id": "question-uuid",
      "question_text": "What is machine learning?",
      "options": ["A branch of AI", "A programming language", "A database system", "A web framework"],
      "correct_answer": "A",
      "explanation": "Machine learning is indeed a branch of artificial intelligence...",
      "difficulty": "medium",
      "points": 1,
      "order_index": 1
    }
  ],
  "created_at": "2025-01-15T10:30:00Z",
  "is_public": false
}
```

**Errors:**
- `401`: Authentication required
- `403`: Access denied - not exam owner or not public
- `404`: Exam not found
- `500`: Retrieval failed

---

### **GET /exam/**
List current user's exams.
🔒 **REQUIRES AUTHENTICATION - User-scoped**

**Response (200):**
```json
{
  "exams": [
    {
      "id": "exam-uuid",
      "title": "My Exam",
      "description": "Description",
      "duration_minutes": 30,
      "total_questions": 5,
      "is_public": false,
      "status": "draft",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ],
  "count": 1,
  "user_id": "user-uuid"
}
```

**Errors:**
- `401`: Authentication required
- `500`: Retrieval failed

---

### **GET /exam/admin/all**
List ALL exams (Admin only).
🔒 **REQUIRES ADMIN ROLE**

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

**Response (200):**
```json
{
  "exams": [
    {
      "id": "exam-uuid",
      "title": "Any User's Exam",
      "description": "Description",
      "creator_id": "user-uuid",
      "duration_minutes": 30,
      "total_questions": 5,
      "is_public": true,
      "status": "published",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ],
  "count": 1,
  "total_available": 1,
  "admin_access": true
}
```

**Errors:**
- `401`: Authentication required
- `403`: Admin role required
- `500`: Retrieval failed

---

## 📁 UPLOAD ENDPOINTS

### **POST /upload/upload**
Upload document file.

**⚠️ TODO: Requires Authentication**

**Request:** `multipart/form-data`
- `file`: Document file (PDF, DOCX, TXT)

**Response (201):**
```json
{
  "message": "File uploaded successfully",
  "file_id": "unique-file-id",
  "original_filename": "document.pdf",
  "size": 1024000,
  "content_type": "application/pdf",
  "metadata": {
    "upload_folder": "uploads",
    "save_path": "uploads/unique-file-id_document.pdf",
    "extension": ".pdf",
    "validation_passed": true
  }
}
```

**Errors:**
- `400`: File type not allowed, file too large
- `401`: Authentication required (TODO)
- `500`: Upload failed

---

### **GET /upload/**
List uploaded files.

**⚠️ TODO: Requires Authentication**

**Response (200):**
```json
{
  "files": [
    {
      "file_id": "unique-file-id",
      "filename": "document.pdf"
    }
  ],
  "count": 1
}
```

---

### **GET /upload/{file_id}**
Get file information.

**⚠️ TODO: Requires Authentication + Ownership Check**

**Response (200):**
```json
{
  "file_id": "unique-file-id",
  "file_path": "uploads/unique-file-id_document.pdf",
  "size": 1024000,
  "created_at": 1705320600.123,
  "modified_at": 1705320600.123,
  "exists": true
}
```

---

### **DELETE /upload/{file_id}**
Delete uploaded file.

**⚠️ TODO: Requires Authentication + Ownership Check**

**Response (200):**
```json
{
  "message": "File deleted successfully",
  "file_id": "unique-file-id",
  "deleted": true
}
```

---

## 🏥 SYSTEM ENDPOINTS

### **GET /**
API information and status.

**Response (200):**
```json
{
  "message": "Exam Hub API v3.0 - Refactored Architecture",
  "description": "Clean architecture with services, repositories, and database integration",
  "docs": "/docs",
  "redoc": "/redoc",
  "version": "3.0.0",
  "architecture": "layered",
  "status": "running"
}
```

---

### **GET /health**
Health check with database status.

**Response (200):**
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

**Response (503) - Unhealthy:**
```json
{
  "status": "unhealthy",
  "version": "3.0.0",
  "database": "disconnected",
  "error": "Database connection failed"
}
```

---

## 📁 UPLOAD ENDPOINTS

### **POST /upload/**
🔒 **REQUIRES AUTHENTICATION** - Upload file for current user

**Request:**
```http
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

file: <binary_file_data>
```

**Response (201):**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "file_id": "uuid-string",
    "original_filename": "document.pdf",
    "stored_filename": "user123_abc123_document.pdf",
    "size": 1024000,
    "size_mb": 1.02,
    "content_type": "application/pdf",
    "file_hash": "sha256-hash",
    "uploaded_at": "2025-09-12T10:30:00Z",
    "is_duplicate": false,
    "metadata": {
      "is_image": false,
      "is_pdf": true,
      "user_scoped": true,
      "database_integrated": true
    }
  }
}
```

**Features:**
- File validation (type, size, content)
- Filename sanitization & path traversal protection
- SHA-256 hash-based duplicate detection
- Database metadata storage
- User ownership tracking

**Errors:**
- `400`: Invalid file type, size, or empty file
- `401`: Authentication required
- `500`: Server error during upload

---

### **GET /upload/**
🔒 **REQUIRES AUTHENTICATION** - List current user's files

**Query Parameters:**
- `skip` (int, optional) - Number of files to skip (default: 0)
- `limit` (int, optional) - Max files per page (default: 100, max: 1000)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "file_id": "uuid-string",
        "original_filename": "document.pdf",
        "size": 1024000,
        "size_mb": 1.02,
        "content_type": "application/pdf",
        "upload_status": "completed",
        "uploaded_at": "2025-09-12T10:30:00Z",
        "filesystem_exists": true
      }
    ],
    "pagination": {
      "count": 1,
      "total_count": 1,
      "skip": 0,
      "limit": 100,
      "has_more": false
    }
  }
}
```

---

### **GET /upload/{file_id}/info**
🔒 **REQUIRES AUTHENTICATION + OWNERSHIP** - Get file information

**Response (200):**
```json
{
  "success": true,
  "data": {
    "file_id": "uuid-string",
    "original_filename": "document.pdf",
    "size": 1024000,
    "content_type": "application/pdf",
    "upload_status": "completed",
    "filesystem_exists": true,
    "uploaded_at": "2025-09-12T10:30:00Z"
  }
}
```

**Errors:**
- `404`: File not found
- `403`: Access denied (not file owner)

---

### **GET /upload/{file_id}/download**
🔒 **REQUIRES AUTHENTICATION + OWNERSHIP** - Download file

**Response (200):**
- File content with proper headers
- `Content-Type`: File MIME type
- `Content-Disposition`: attachment; filename="..."
- `X-File-ID`: File identifier
- `X-File-Size`: File size in bytes

**Errors:**
- `404`: File not found or missing from filesystem
- `403`: Access denied (not file owner)

---

### **DELETE /upload/{file_id}**
🔒 **REQUIRES AUTHENTICATION + OWNERSHIP** - Delete file

**Response (200):**
```json
{
  "success": true,
  "message": "File deleted successfully",
  "data": {
    "file_id": "uuid-string",
    "original_filename": "document.pdf",
    "filesystem_deleted": true,
    "database_updated": true
  }
}
```

---

### **GET /upload/admin/files**
🔒 **REQUIRES ADMIN ROLE** - List all files (Admin only)

**Query Parameters:**
- `skip` (int, optional) - Number of files to skip
- `limit` (int, optional) - Max files per page

**Response (200):**
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "file_id": "uuid-string",
        "original_filename": "document.pdf",
        "owner_id": "user-uuid",
        "size": 1024000,
        "uploaded_at": "2025-09-12T10:30:00Z"
      }
    ],
    "admin_access": true,
    "requested_by": "admin@example.com"
  }
}
```

---

### **GET /upload/admin/stats**
🔒 **REQUIRES ADMIN ROLE** - Get upload statistics

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_files": 150,
    "total_size_mb": 150.0,
    "active_users": 25,
    "file_types": {
      "application/pdf": 80,
      "image/jpeg": 45
    },
    "admin_access": true
  }
}
```

---

### **GET /upload/health**
**PUBLIC ENDPOINT** - Upload service health check

**Response (200):**
```json
{
  "success": true,
  "data": {
    "service": "upload",
    "status": "healthy",
    "checks": {
      "upload_folder_exists": true,
      "upload_folder_writable": true,
      "database_integration": true,
      "security_enabled": true
    }
  }
}
```

---

## 🔒 AUTHENTICATION HEADERS

### **Protected Endpoints (TODO)**
For endpoints requiring authentication, include JWT token:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Current Status**
- ✅ **Authentication middleware implemented**
- ✅ **Protected endpoints working**
- ✅ **User-scoped data access enforced**
- ✅ **Role-based authorization active**
- ✅ **Upload system fully integrated**
- ✅ **File security & validation implemented**

**Security Status:** All sensitive endpoints are protected with JWT authentication, user-scoped access control, and comprehensive file security measures.

---

## 📊 ERROR RESPONSE FORMAT

### **Standard Error Response**
```json
{
  "detail": "Error description",
  "status_code": 400,
  "type": "validation_error"
}
```

### **Validation Error Response**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {...}
    }
  ]
}
```

---

## 🧪 TESTING ENDPOINTS

### **Using cURL**
```bash
# Health check
curl -X GET "http://localhost:5001/health"

# Register user
curl -X POST "http://localhost:5001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123", "full_name": "Test User"}'

# Generate exam
curl -X POST "http://localhost:5001/exam/generate" \
  -H "Content-Type: application/json" \
  -d '{"file_content": "Long text content here...", "num_questions": 3, "subject": "Test Subject"}'

# Upload file
curl -X POST "http://localhost:5001/upload/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.txt"
```

### **Using Postman**
1. **Import OpenAPI spec:** `http://localhost:5001/openapi.json`
2. **Set base URL:** `http://localhost:5001`
3. **Add Authorization header** (when implemented): `Bearer {token}`

---

## 🚀 UPCOMING ENDPOINTS

### **Planned Additions**

**Exam Management:**
```
GET  /exam/                    # List user's exams
PUT  /exam/{exam_id}           # Update exam
DELETE /exam/{exam_id}         # Delete exam
POST /exam/{exam_id}/publish   # Publish exam
```

**Exam Taking:**
```
POST /exam/{exam_id}/attempt   # Start exam attempt
PUT  /attempt/{attempt_id}     # Submit answers
GET  /attempt/{attempt_id}     # Get attempt results
```

**User Management:**
```
GET  /user/profile             # Get user profile
PUT  /user/profile             # Update profile
GET  /user/exams               # User's exams
GET  /user/attempts            # User's exam attempts
```

**Admin Endpoints:**
```
GET  /admin/users              # List all users
GET  /admin/exams              # List all exams
GET  /admin/analytics          # System analytics
```

---

*API documentation based on current implementation. Authentication requirements marked as TODO items.*
