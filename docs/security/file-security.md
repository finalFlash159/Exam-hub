# File Upload Security

Comprehensive security implementation for the Exam Hub file upload system, covering validation, access control, and threat mitigation.

## 🛡️ Security Overview

The upload system implements multiple layers of security to protect against common file upload vulnerabilities:

- **Input Validation** - File type, size, and content validation
- **Path Traversal Protection** - Filename sanitization and secure storage
- **Access Control** - User-scoped ownership and JWT authentication
- **Data Integrity** - SHA-256 hashing and duplicate detection
- **Audit Logging** - Comprehensive operation tracking

## 🔐 Authentication & Authorization

### JWT Authentication
All upload endpoints (except health check) require valid JWT tokens:

```http
Authorization: Bearer <jwt_token>
```

**Token Validation:**
- Token signature verification
- Expiration time checking
- User account status validation
- Role-based access control

### User Scoping
Files are strictly scoped to their owners:

```python
# Example ownership validation
if file_record.owner_id != current_user.id:
    raise PermissionError("Access denied")
```

**Access Rules:**
- **Users** can only access their own files
- **Admins** can access all files and system statistics
- **File operations** require both authentication and ownership validation

## 📁 File Validation

### File Type Restrictions
Only specific file types are allowed:

```python
ALLOWED_EXTENSIONS = {
    "txt", "pdf", "png", "jpg", "jpeg", "gif", 
    "doc", "docx", "xls", "xlsx", "ppt", "pptx"
}
```

**Validation Process:**
1. **Extension Check** - Filename extension validation
2. **MIME Type Check** - Content-Type header validation
3. **Magic Number Detection** - File content signature verification

```python
# Example content validation
if content.startswith(b'\x89PNG'):
    actual_type = "image/png"
elif content.startswith(b'%PDF'):
    actual_type = "application/pdf"
```

### File Size Limits
Maximum file size enforcement:

```python
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
```

**Size Validation:**
- Content length checking during upload
- File size verification after storage
- Size mismatch detection and cleanup

### Content Validation
Additional content security measures:

```python
# Empty file protection
if file_size == 0:
    raise ValueError("Empty file not allowed")

# Content integrity verification
saved_size = os.path.getsize(file_path)
if saved_size != file_size:
    raise Exception("File save verification failed")
```

## 🚫 Path Traversal Protection

### Filename Sanitization
Comprehensive filename cleaning to prevent path traversal attacks:

```python
def sanitize_filename(self, filename: str) -> str:
    if not filename:
        return "unnamed_file"
    
    # Extract extension
    name, ext = os.path.splitext(filename)
    
    # Remove dangerous characters
    safe_name = re.sub(r'[^\w\-_.]', '_', name)
    safe_ext = re.sub(r'[^\w.]', '', ext)
    
    # Remove leading/trailing dangerous chars
    safe_name = safe_name.strip('._')
    
    # Ensure name is not empty
    if not safe_name:
        safe_name = "file"
    
    # Limit length
    if len(safe_name) > 100:
        safe_name = safe_name[:100]
    
    return safe_name + safe_ext
```

**Sanitization Examples:**
```
Input: "../../../etc/passwd"     → Output: "etc_passwd"
Input: "file with spaces.pdf"    → Output: "file_with_spaces.pdf"
Input: "file@#$%^&*().jpg"       → Output: "file.jpg"
Input: ""                        → Output: "unnamed_file"
```

### Secure Storage
Files are stored with secure naming conventions:

```python
# Unique filename generation
file_uuid = uuid.uuid4().hex
stored_filename = f"{user_id[:8]}_{file_uuid}_{safe_filename}"
file_path = os.path.join(upload_folder, stored_filename)
```

**Storage Security:**
- **UUID-based naming** prevents filename collisions
- **User prefix** enables quick ownership identification
- **Absolute paths** prevent directory traversal
- **Isolated storage** outside web-accessible directories

## 🔍 Data Integrity

### SHA-256 Hashing
All files are hashed for integrity verification:

```python
def calculate_file_hash(self, content: bytes) -> str:
    # Memory-optimized hashing for large files
    if len(content) > 50 * 1024 * 1024:  # 50MB threshold
        hasher = hashlib.sha256()
        chunk_size = 8192
        for i in range(0, len(content), chunk_size):
            hasher.update(content[i:i+chunk_size])
        return hasher.hexdigest()
    else:
        return hashlib.sha256(content).hexdigest()
```

### Duplicate Detection
Hash-based deduplication prevents redundant storage:

```python
# Check for existing files with same hash
existing_file = await self.file_repo.get_by_hash(file_hash)
if existing_file and existing_file.owner_id == user_id:
    return existing_duplicate_response
```

**Benefits:**
- **Storage optimization** - Prevents duplicate files
- **Integrity verification** - Detects file corruption
- **Change detection** - Identifies modified files

## 🔒 Database Security

### Secure Schema Design
```sql
CREATE TABLE uploaded_files (
    id VARCHAR(36) PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) UNIQUE NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    owner_id VARCHAR(36) NOT NULL, -- FK constraint
    file_hash VARCHAR(64), -- SHA-256
    upload_status VARCHAR(20) DEFAULT 'COMPLETED',
    -- ... other fields
    
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- Security indexes
CREATE INDEX idx_uploaded_files_owner_id ON uploaded_files(owner_id);
CREATE INDEX idx_uploaded_files_file_hash ON uploaded_files(file_hash);
```

### Transaction Safety
Atomic operations with proper rollback:

```python
try:
    # Create database record
    file_record = await self.file_repo.create_file_record(...)
    
    # Save to filesystem
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Update status
    await self.file_repo.update_status(file_record.id, FileStatus.COMPLETED)
    
except Exception as e:
    # Cleanup on failure
    await self.file_repo.delete_file_record(file_record.id, user_id)
    if os.path.exists(file_path):
        os.remove(file_path)
    raise
```

### Soft Delete
Files are marked as deleted rather than permanently removed:

```python
# Soft delete implementation
file_record.upload_status = FileStatus.DELETED
await self.session.commit()
```

**Advantages:**
- **Data recovery** - Accidentally deleted files can be restored
- **Audit trail** - Deletion history is maintained
- **Compliance** - Meets data retention requirements

## 📊 Audit Logging

### Comprehensive Logging
All file operations are logged with security context:

```python
# Upload logging
logger.info(f"User {current_user.email} uploading file: {file.filename}")
logger.info(f"File upload completed successfully: {file_record.id}")

# Access logging
logger.info(f"User {current_user.email} downloading file: {file_id}")
logger.warning(f"Unauthorized access attempt: user {user_id} tried to access file {file_id}")

# Security events
logger.warning(f"Upload validation failed for user {current_user.email}: {error}")
logger.warning(f"File type not allowed: {filename}")
```

### Log Categories
- **INFO** - Normal operations (upload, download, delete)
- **WARNING** - Security events (unauthorized access, validation failures)
- **ERROR** - System errors (filesystem issues, database problems)
- **DEBUG** - Detailed operation tracking (development only)

### Security Monitoring
Key events to monitor:

```python
# Failed authentication attempts
logger.warning(f"Authentication failed for upload request")

# Unauthorized access attempts
logger.warning(f"User {user_id} denied access to file {file_id} owned by {owner_id}")

# Validation failures
logger.warning(f"File type not allowed: {filename}")
logger.warning(f"File too large: {file_size} > {max_size}")

# Suspicious activity
logger.warning(f"Path traversal attempt detected: {filename}")
logger.warning(f"Multiple failed uploads from user: {user_id}")
```

## ⚠️ Threat Mitigation

### Common Upload Vulnerabilities

#### 1. Malicious File Upload
**Threat:** Uploading executable files or scripts
**Mitigation:**
- Strict file type allowlist
- Content-type validation
- Magic number verification
- No execution permissions on upload directory

#### 2. Path Traversal
**Threat:** `../../../etc/passwd` filename attacks
**Mitigation:**
- Comprehensive filename sanitization
- UUID-based storage names
- Absolute path validation
- Isolated storage directories

#### 3. File Bomb/DoS
**Threat:** Large files exhausting storage/memory
**Mitigation:**
- File size limits (50MB default)
- Memory-optimized processing
- Streaming hash calculation
- Storage quota monitoring

#### 4. Content Injection
**Threat:** Malicious content in files
**Mitigation:**
- Content-type validation
- File signature verification
- Virus scanning (future enhancement)
- Isolated file serving

#### 5. Information Disclosure
**Threat:** Unauthorized file access
**Mitigation:**
- User-scoped access control
- JWT authentication required
- Ownership validation
- Admin-only system access

## 🔧 Security Configuration

### Environment Variables
```env
# Upload security settings
MAX_UPLOAD_SIZE=52428800  # 50MB
ALLOWED_EXTENSIONS=txt,pdf,png,jpg,jpeg,gif,doc,docx
UPLOAD_FOLDER=./uploads

# Security settings
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Security Headers
```python
# File download security headers
headers = {
    "Content-Disposition": f"attachment; filename=\"{safe_filename}\"",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-File-ID": file_id,
    "X-File-Size": str(file_size)
}
```

## 🧪 Security Testing

### Test Cases
```python
# 1. Path traversal protection
test_filename = "../../../etc/passwd"
expected_safe = "etc_passwd"

# 2. File type validation
test_malicious_file = "malware.exe"
expected_error = "File type not allowed"

# 3. Size limit enforcement
test_large_file = b"A" * (60 * 1024 * 1024)  # 60MB
expected_error = "File too large"

# 4. Unauthorized access
test_access_other_user_file()
expected_error = "Access denied"

# 5. Empty file protection
test_empty_file = b""
expected_error = "Empty file not allowed"
```

### Security Checklist
- [ ] File type validation working
- [ ] Size limits enforced
- [ ] Path traversal protection active
- [ ] Authentication required for all endpoints
- [ ] User scoping enforced
- [ ] Admin role validation working
- [ ] Audit logging comprehensive
- [ ] Error messages don't leak information
- [ ] File storage isolated and secure
- [ ] Database constraints properly enforced

## 🚀 Future Enhancements

### Planned Security Features
1. **Virus Scanning** - Integrate with ClamAV or similar
2. **Content Analysis** - Deep content inspection
3. **Rate Limiting** - Per-user upload rate limits
4. **IP Whitelisting** - Restrict uploads by IP
5. **File Quarantine** - Suspicious file isolation
6. **Advanced Monitoring** - ML-based anomaly detection

### Compliance Considerations
- **GDPR** - User data protection and deletion rights
- **HIPAA** - Healthcare data security (if applicable)
- **SOC 2** - Security controls and monitoring
- **ISO 27001** - Information security management

---

*Security documentation updated with implementation completed on 2025-09-12*

