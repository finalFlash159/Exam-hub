# Upload API Documentation

Complete documentation for the Exam Hub file upload system with database integration and security features.

## 🎯 Overview

The Upload API provides secure, user-scoped file management with comprehensive validation, duplicate detection, and database integration. All endpoints require authentication and implement proper authorization controls.

### Key Features
- **Database Integration** - File metadata stored in PostgreSQL/SQLite
- **Security Hardened** - Path traversal protection, file validation, ownership checks
- **Duplicate Detection** - SHA-256 hash-based deduplication
- **User Scoped** - Files are owned by users with proper access control
- **Admin Features** - System-wide file management and statistics
- **Type Safe** - Pydantic schemas for all responses

## 🔐 Authentication

All endpoints (except health check) require JWT authentication:

```http
Authorization: Bearer <jwt_token>
```

### User Roles
- **USER** - Can manage own files only
- **ADMIN** - Can access all files and system statistics

## 📋 API Endpoints

### File Operations

#### Upload File
```http
POST /upload/
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**Request:**
```
file: <binary_file_data>
```

**Response:**
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
- Filename sanitization (path traversal protection)
- Duplicate detection via SHA-256 hash
- Database metadata storage
- User ownership tracking

**Error Responses:**
- `400` - Invalid file type, size, or empty file
- `401` - Authentication required
- `500` - Server error during upload

---

#### List User Files
```http
GET /upload/?skip=0&limit=100
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, optional) - Number of files to skip (default: 0)
- `limit` (int, optional) - Max files per page (default: 100, max: 1000)

**Response:**
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "file_id": "uuid-string",
        "stored_filename": "user123_abc123_document.pdf",
        "original_filename": "document.pdf",
        "size": 1024000,
        "size_mb": 1.02,
        "content_type": "application/pdf",
        "upload_status": "completed",
        "is_public": false,
        "is_image": false,
        "is_pdf": true,
        "uploaded_at": "2025-09-12T10:30:00Z",
        "filesystem_exists": true,
        "user_owned": true
      }
    ],
    "pagination": {
      "count": 1,
      "total_count": 1,
      "skip": 0,
      "limit": 100,
      "has_more": false
    },
    "user_id": "user-uuid",
    "user_scoped": true
  }
}
```

---

#### Get File Information
```http
GET /upload/{file_id}/info
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "file_id": "uuid-string",
    "stored_filename": "user123_abc123_document.pdf",
    "original_filename": "document.pdf",
    "size": 1024000,
    "size_mb": 1.02,
    "content_type": "application/pdf",
    "file_hash": "sha256-hash",
    "upload_status": "completed",
    "is_public": false,
    "is_image": false,
    "is_pdf": true,
    "uploaded_at": "2025-09-12T10:30:00Z",
    "updated_at": "2025-09-12T10:30:00Z",
    "owner_id": "user-uuid",
    "filesystem_exists": true,
    "database_integrated": true,
    "access_validated": true
  }
}
```

**Error Responses:**
- `404` - File not found
- `403` - Access denied (not file owner)

---

#### Download File
```http
GET /upload/{file_id}/download
Authorization: Bearer <token>
```

**Response:**
- **Success:** File content with proper headers
  ```
  Content-Type: application/pdf
  Content-Disposition: attachment; filename="document.pdf"
  X-File-ID: uuid-string
  X-File-Size: 1024000
  ```

**Error Responses:**
- `404` - File not found or missing from filesystem
- `403` - Access denied (not file owner)

---

#### Delete File
```http
DELETE /upload/{file_id}
Authorization: Bearer <token>
```

**Response:**
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

**Features:**
- Soft delete in database (marked as DELETED)
- Physical file removal from filesystem
- Ownership validation before deletion

---

### Admin Operations

#### List All Files (Admin)
```http
GET /upload/admin/files?skip=0&limit=100
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "file_id": "uuid-string",
        "stored_filename": "user123_abc123_document.pdf",
        "original_filename": "document.pdf",
        "size": 1024000,
        "size_mb": 1.02,
        "content_type": "application/pdf",
        "upload_status": "completed",
        "is_public": false,
        "owner_id": "user-uuid",
        "uploaded_at": "2025-09-12T10:30:00Z",
        "filesystem_exists": true,
        "admin_visible": true
      }
    ],
    "pagination": {
      "count": 1,
      "total_count": 1,
      "skip": 0,
      "limit": 100,
      "has_more": false
    },
    "admin_access": true,
    "requested_by": "admin@example.com"
  }
}
```

---

#### Upload Statistics (Admin)
```http
GET /upload/admin/stats
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_files": 150,
    "total_size_bytes": 157286400,
    "total_size_mb": 150.0,
    "active_users": 25,
    "file_types": {
      "application/pdf": 80,
      "image/jpeg": 45,
      "image/png": 20,
      "text/plain": 5
    },
    "average_file_size_mb": 1.0,
    "admin_access": true,
    "generated_by": "admin@example.com"
  }
}
```

---

### System Operations

#### Health Check
```http
GET /upload/health
```

**Response:**
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

## 🛡️ Security Features

### File Validation
- **File Type Checking** - Only allowed extensions (configurable)
- **Size Limits** - Maximum file size enforcement
- **Content Validation** - Magic number detection for common file types
- **Empty File Protection** - Zero-byte files rejected

### Path Security
- **Filename Sanitization** - Removes dangerous characters
- **Path Traversal Protection** - Prevents `../` attacks
- **Unique Storage Names** - UUID-based file naming

### Access Control
- **User Ownership** - Files scoped to uploading user
- **JWT Authentication** - All endpoints protected
- **Role-Based Access** - Admin vs user permissions
- **Audit Logging** - All operations logged

### Data Integrity
- **SHA-256 Hashing** - File content verification
- **Duplicate Detection** - Prevents redundant storage
- **Database Consistency** - Metadata synchronized with filesystem
- **Transaction Safety** - Atomic operations with rollback

## 📊 Database Schema

### uploaded_files Table
```sql
CREATE TABLE uploaded_files (
    id VARCHAR(36) PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) UNIQUE NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    size INTEGER NOT NULL,
    content_type VARCHAR(100),
    file_hash VARCHAR(64), -- SHA-256
    owner_id VARCHAR(36) NOT NULL, -- FK to users.id
    is_public BOOLEAN DEFAULT FALSE,
    storage_type VARCHAR(10) DEFAULT 'LOCAL',
    storage_metadata JSON,
    upload_status VARCHAR(20) DEFAULT 'COMPLETED',
    processed BOOLEAN DEFAULT FALSE,
    processing_result JSON,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_uploaded_files_owner_id ON uploaded_files(owner_id);
CREATE INDEX idx_uploaded_files_file_hash ON uploaded_files(file_hash);
CREATE INDEX idx_uploaded_files_stored_filename ON uploaded_files(stored_filename);
```

## 🔧 Configuration

### Settings
```python
# File upload settings
UPLOAD_FOLDER = "uploads/"
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "doc", "docx"}

# Storage settings
STORAGE_TYPE = "local"  # local, s3, gcs (future)
```

### Environment Variables
```env
# Upload configuration
UPLOAD_FOLDER=./uploads
MAX_UPLOAD_SIZE=52428800
ALLOWED_EXTENSIONS=txt,pdf,png,jpg,jpeg,gif,doc,docx
```

## 🧪 Testing

### Example cURL Commands

**Upload File:**
```bash
curl -X POST "http://localhost:8000/upload/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "file=@document.pdf"
```

**List Files:**
```bash
curl -X GET "http://localhost:8000/upload/?limit=10" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Download File:**
```bash
curl -X GET "http://localhost:8000/upload/{file_id}/download" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -o downloaded_file.pdf
```

## 📈 Performance

### Optimizations
- **Hash-based Deduplication** - Saves storage space
- **Pagination** - Efficient large dataset handling
- **Database Indexes** - Fast queries on owner_id, file_hash
- **Streaming Hash** - Memory-efficient large file processing

### Limits
- **File Size:** 50MB per file (configurable)
- **Request Rate:** Managed by FastAPI rate limiting
- **Storage:** Limited by available disk space
- **Concurrent Uploads:** Handled by async processing

## 🚨 Error Handling

### Common Error Codes
- `400 Bad Request` - Invalid file, size, or type
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Access denied (wrong owner)
- `404 Not Found` - File doesn't exist
- `413 Payload Too Large` - File exceeds size limit
- `500 Internal Server Error` - Server-side issues

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "details": "Detailed error description (debug mode only)",
  "error_code": "UPLOAD_001"
}
```

---

*Documentation generated from implementation completed on 2025-09-12*
