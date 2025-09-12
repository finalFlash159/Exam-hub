# 🤖 AI Integration API Documentation

## 📋 **OVERVIEW**

API endpoints for AI-powered exam generation with multi-provider support (OpenAI, Gemini, Mock).

**Base URL:** `http://localhost:8000`  
**Authentication:** Required (JWT Bearer token)

---

## 🔍 **AI CLIENT DISCOVERY**

### **GET /ai/clients**

Get available AI service providers and their capabilities.

**Authentication:** Required  
**Method:** GET  
**Path:** `/ai/clients`

#### **Response:**
```json
{
  "available_clients": [
    {
      "type": "openai",
      "name": "OpenAI",
      "model": "gpt-4o-mini",
      "max_tokens": 2000,
      "supports": ["multiple_choice", "true_false", "short_answer", "essay"],
      "languages": ["en", "vi", "fr", "es", "de"],
      "is_healthy": true,
      "status": "available",
      "cost_per_1k_tokens": 0.0005
    },
    {
      "type": "gemini",
      "name": "Google Gemini",
      "model": "gemini-2.0-flash-exp",
      "max_tokens": 8000,
      "supports": ["multiple_choice", "true_false", "essay", "coding"],
      "languages": ["en", "vi", "ja", "ko", "zh"],
      "is_healthy": true,
      "status": "available",
      "cost_per_1k_tokens": 0.0003
    },
    {
      "type": "mock",
      "name": "Mock Client",
      "model": "mock-v1",
      "max_tokens": 4000,
      "supports": ["multiple_choice", "true_false"],
      "languages": ["en"],
      "is_healthy": true,
      "status": "available",
      "cost_per_1k_tokens": 0
    }
  ],
  "default_client": "gemini",
  "total_clients": 3
}
```

#### **Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Authentication required
- `500 Internal Server Error` - Server error

#### **cURL Example:**
```bash
curl -X GET "http://localhost:8000/ai/clients" \
  -H "Authorization: Bearer your-jwt-token"
```

---

## 🎯 **EXAM GENERATION FROM FILE**

### **POST /upload/{file_id}/generate-exam**

Generate exam questions from uploaded document using AI.

**Authentication:** Required  
**Method:** POST  
**Path:** `/upload/{file_id}/generate-exam`

#### **Path Parameters:**
- `file_id` (string, required) - ID of uploaded file to process

#### **Request Body:**
```json
{
  "exam_title": "Python Programming Basics",
  "question_count": 15,
  "difficulty": "medium",
  "ai_client": "openai",
  "question_types": ["multiple_choice", "true_false"],
  "language": "en",
  "subject_hint": "Programming fundamentals"
}
```

#### **Request Schema:**
```json
{
  "exam_title": {
    "type": "string",
    "required": true,
    "min_length": 1,
    "max_length": 200,
    "description": "Title for the generated exam"
  },
  "question_count": {
    "type": "integer",
    "default": 10,
    "minimum": 1,
    "maximum": 50,
    "description": "Number of questions to generate"
  },
  "difficulty": {
    "type": "string",
    "enum": ["easy", "medium", "hard"],
    "default": "medium",
    "description": "Difficulty level of questions"
  },
  "ai_client": {
    "type": "string",
    "enum": ["openai", "gemini", "mock"],
    "default": "gemini",
    "description": "AI provider to use for generation"
  },
  "question_types": {
    "type": "array",
    "items": {
      "type": "string",
      "enum": ["multiple_choice", "true_false", "short_answer", "essay"]
    },
    "default": ["multiple_choice"],
    "description": "Types of questions to generate"
  },
  "language": {
    "type": "string",
    "default": "en",
    "description": "Language code for generated questions"
  },
  "subject_hint": {
    "type": "string",
    "required": false,
    "description": "Optional subject area hint for better context"
  }
}
```

#### **Success Response (200):**
```json
{
  "success": true,
  "exam_data": {
    "title": "Python Programming Basics",
    "questions": [
      {
        "question_id": "q1",
        "question_text": "What is the correct way to define a function in Python?",
        "question_type": "multiple_choice",
        "options": [
          {
            "option_id": "A",
            "text": "def function_name():",
            "is_correct": true
          },
          {
            "option_id": "B",
            "text": "function function_name():",
            "is_correct": false
          },
          {
            "option_id": "C",
            "text": "define function_name():",
            "is_correct": false
          },
          {
            "option_id": "D",
            "text": "func function_name():",
            "is_correct": false
          }
        ],
        "correct_answer": "A",
        "explanation": "In Python, functions are defined using the 'def' keyword followed by the function name and parentheses.",
        "difficulty": "medium",
        "points": 1
      },
      {
        "question_id": "q2",
        "question_text": "Python is a dynamically typed language.",
        "question_type": "true_false",
        "correct_answer": "true",
        "explanation": "Python is indeed dynamically typed, meaning variable types are determined at runtime.",
        "difficulty": "easy",
        "points": 1
      }
    ],
    "total_questions": 2,
    "difficulty": "medium",
    "estimated_duration": 15
  },
  "file_id": "abc123-def456-ghi789",
  "client_used": "openai",
  "content_length": 1250,
  "generation_time": 12.5,
  "created_at": "2025-09-12T10:30:00Z"
}
```

#### **Error Responses:**

**File Not Found (404):**
```json
{
  "success": false,
  "error": "File not found or access denied",
  "file_id": "abc123-def456-ghi789"
}
```

**File Not Processed (400):**
```json
{
  "success": false,
  "error": "File content not available. Please process the file first using POST /upload/{file_id}/process",
  "file_id": "abc123-def456-ghi789"
}
```

**AI Client Error (400):**
```json
{
  "success": false,
  "error": "Client openai is not properly configured",
  "file_id": "abc123-def456-ghi789"
}
```

**Insufficient Content (400):**
```json
{
  "success": false,
  "error": "Insufficient content for exam generation (minimum 100 characters)",
  "file_id": "abc123-def456-ghi789",
  "content_length": 45
}
```

**AI Generation Error (500):**
```json
{
  "success": false,
  "error": "OpenAI API error: Rate limit exceeded",
  "file_id": "abc123-def456-ghi789",
  "client_used": "openai"
}
```

#### **Status Codes:**
- `200 OK` - Exam generated successfully
- `400 Bad Request` - Invalid request or insufficient content
- `401 Unauthorized` - Authentication required
- `404 Not Found` - File not found or access denied
- `500 Internal Server Error` - AI service error

#### **cURL Example:**
```bash
curl -X POST "http://localhost:8000/upload/abc123-def456-ghi789/generate-exam" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_title": "Python Programming Basics",
    "question_count": 10,
    "difficulty": "medium",
    "ai_client": "openai",
    "question_types": ["multiple_choice"],
    "language": "en"
  }'
```

---

## 🔧 **AI CLIENT HEALTH CHECK**

### **GET /ai/clients/{client_type}/health**

Check health status of specific AI client.

**Authentication:** Required (Admin only)  
**Method:** GET  
**Path:** `/ai/clients/{client_type}/health`

#### **Path Parameters:**
- `client_type` (string, required) - AI client type: `openai`, `gemini`, or `mock`

#### **Response:**
```json
{
  "client_type": "openai",
  "is_configured": true,
  "is_healthy": true,
  "client_info": {
    "name": "OpenAI",
    "model": "gpt-4o-mini",
    "max_tokens": 2000,
    "supports": ["multiple_choice", "true_false", "short_answer", "essay"],
    "languages": ["en", "vi", "fr", "es", "de"]
  },
  "response_time": 150,
  "last_checked": "2025-09-12T10:30:00Z"
}
```

#### **Error Response:**
```json
{
  "client_type": "openai",
  "is_configured": false,
  "is_healthy": false,
  "error": "OpenAI API key not configured"
}
```

---

## 📊 **LEGACY EXAM GENERATION**

### **POST /exam/generate**

Legacy endpoint for exam generation from text content (backward compatibility).

**Authentication:** Required  
**Method:** POST  
**Path:** `/exam/generate`

#### **Request Body:**
```json
{
  "file_content": "Python is a high-level programming language...",
  "num_questions": 10,
  "subject": "Python Programming"
}
```

#### **Response:**
```json
{
  "questions": [
    {
      "question_text": "What is Python?",
      "options": ["A programming language", "A snake", "A framework", "A database"],
      "correct_answer": "A programming language",
      "explanation": "Python is a high-level programming language."
    }
  ],
  "subject": "Python Programming",
  "total_questions": 1
}
```

**Note:** This endpoint uses the default AI client (Gemini) and is maintained for backward compatibility.

---

## 🔐 **AUTHENTICATION**

All AI endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer your-jwt-token-here
```

### **Getting Access Token:**

1. **Register:** `POST /auth/register`
2. **Login:** `POST /auth/login`
3. **Use token:** Include in Authorization header

---

## 📈 **RATE LIMITS & QUOTAS**

### **Rate Limits:**
- **AI Generation:** 10 requests per minute per user
- **Client Discovery:** 60 requests per minute per user
- **Health Checks:** 5 requests per minute per user (Admin only)

### **Content Limits:**
- **Minimum content:** 100 characters
- **Maximum content:** 50,000 characters
- **Maximum questions:** 50 per exam
- **Supported file types:** PDF, DOCX, TXT

### **AI Provider Limits:**
- **OpenAI:** Subject to OpenAI rate limits
- **Gemini:** Subject to Google rate limits
- **Mock:** No limits (development only)

---

## 🚨 **ERROR HANDLING**

### **Common Error Patterns:**

#### **Authentication Errors:**
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

#### **Validation Errors:**
```json
{
  "detail": [
    {
      "loc": ["body", "question_count"],
      "msg": "ensure this value is less than or equal to 50",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 50}
    }
  ],
  "status_code": 422
}
```

#### **AI Service Errors:**
```json
{
  "success": false,
  "error": "AI service temporarily unavailable",
  "error_code": "AI_SERVICE_DOWN",
  "retry_after": 300
}
```

### **Error Codes:**
- `AI_CLIENT_NOT_CONFIGURED` - AI client missing API key
- `AI_CLIENT_UNHEALTHY` - AI client connectivity issues
- `CONTENT_TOO_SHORT` - Insufficient content for generation
- `CONTENT_TOO_LONG` - Content exceeds processing limits
- `AI_SERVICE_DOWN` - AI provider temporarily unavailable
- `GENERATION_FAILED` - AI generation process failed
- `RATE_LIMIT_EXCEEDED` - Too many requests

---

## 🧪 **TESTING**

### **Mock Client:**
For development and testing, use the mock client:

```json
{
  "ai_client": "mock"
}
```

The mock client:
- ✅ Always available and healthy
- ✅ Generates realistic test questions
- ✅ No API key required
- ✅ Instant responses
- ✅ No cost

### **Example Test Request:**
```bash
curl -X POST "http://localhost:8000/upload/test-file-id/generate-exam" \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_title": "Test Exam",
    "question_count": 5,
    "ai_client": "mock"
  }'
```

---

## 📚 **EXAMPLES**

### **Complete Workflow Example:**

```bash
# 1. Login to get token
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  | jq -r '.access_token')

# 2. Upload file
FILE_ID=$(curl -X POST "http://localhost:8000/upload/file" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf" \
  | jq -r '.file_id')

# 3. Process file content
curl -X POST "http://localhost:8000/upload/$FILE_ID/process" \
  -H "Authorization: Bearer $TOKEN"

# 4. Check available AI clients
curl -X GET "http://localhost:8000/ai/clients" \
  -H "Authorization: Bearer $TOKEN"

# 5. Generate exam
curl -X POST "http://localhost:8000/upload/$FILE_ID/generate-exam" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_title": "Document Analysis Exam",
    "question_count": 15,
    "difficulty": "medium",
    "ai_client": "openai",
    "question_types": ["multiple_choice", "true_false"]
  }'
```

---

*Last updated: 2025-09-12*
*API Version: 3.0*
