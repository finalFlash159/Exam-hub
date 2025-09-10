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

**⚠️ TODO: Requires Authentication**

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

**⚠️ TODO: Requires Authentication + Authorization**

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
- `401`: Authentication required (TODO)
- `403`: Access denied (TODO)
- `404`: Exam not found
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

## 🔒 AUTHENTICATION HEADERS

### **Protected Endpoints (TODO)**
For endpoints requiring authentication, include JWT token:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Current Status**
- ⚠️ **All endpoints currently PUBLIC**
- ⚠️ **No authentication middleware implemented**
- ⚠️ **Authorization not enforced**

**Priority Fix:** Implement JWT middleware and protect sensitive endpoints.

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
