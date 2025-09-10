# Database Design Documentation

## 📊 DATABASE ARCHITECTURE

### **Database Technology**
- **Development:** SQLite (file-based, easy setup)
- **Production:** PostgreSQL (scalable, ACID compliance)
- **ORM:** SQLAlchemy 2.0 with async support
- **Migrations:** Alembic for schema versioning

---

## 🗃️ ENTITY RELATIONSHIP DIAGRAM

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Users       │     │     Exams       │     │   Questions     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ email (UQ)      │     │ title           │◄────┤ exam_id (FK)    │
│ hashed_password │     │ description     │     │ question_text   │
│ full_name       │     │ duration_min    │     │ options (JSON)  │
│ email_verified  │     │ total_questions │     │ correct_answer  │
│ role            │     │ passing_score   │     │ explanation     │
│ is_active       │     │ status          │     │ difficulty      │
│ created_at      │     │ is_public       │     │ order_index     │
│ updated_at      │     │ created_at      │     │ points          │
└─────────────────┘     │ updated_at      │     │ created_at      │
         │               └─────────────────┘     │ updated_at      │
         │                        │              └─────────────────┘
         │                        │                       │
         │               ┌─────────────────┐              │
         │               │ ExamAttempts    │              │
         └───────────────┤ id (PK)         │──────────────┘
                         │ user_id (FK)    │
                         │ exam_id (FK)    │
                         │ start_time      │
                         │ end_time        │
                         │ score           │
                         │ answers (JSON)  │
                         │ created_at      │
                         └─────────────────┘

┌─────────────────┐     ┌─────────────────────────────┐
│ RefreshTokens   │     │ EmailVerificationTokens     │
├─────────────────┤     ├─────────────────────────────┤
│ id (PK)         │     │ id (PK)                     │
│ user_id (FK)    │─────┤ user_id (FK)                │
│ token (UQ)      │     │ token (UQ)                  │
│ expires_at      │     │ expires_at                  │
│ created_at      │     │ created_at                  │
└─────────────────┘     └─────────────────────────────┘
```

---

## 🏗️ TABLE SPECIFICATIONS

### **Users Table**
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
```

**Purpose:** User authentication, profile management, role-based access
**Key Features:**
- Email-based authentication with verification
- Secure password storage (Argon2 hashing)
- Role system (USER/ADMIN)
- Password reset functionality
- Account status tracking

### **Exams Table**
```sql
CREATE TABLE exams (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INTEGER,
    total_questions INTEGER DEFAULT 0,
    passing_score INTEGER,
    status VARCHAR(20) DEFAULT 'draft',
    is_public BOOLEAN DEFAULT FALSE,
    source_file_id VARCHAR(255),
    source_file_name VARCHAR(255),
    generation_method VARCHAR(50),
    legacy_id INTEGER,
    legacy_file_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_exams_title ON exams(title);
CREATE INDEX idx_exams_status ON exams(status);
CREATE INDEX idx_exams_public ON exams(is_public);
CREATE INDEX idx_exams_created ON exams(created_at);
```

**Purpose:** Exam metadata and configuration
**Key Features:**
- Exam content organization
- Status workflow (DRAFT → PUBLISHED → ARCHIVED)
- Public/private visibility control
- Source file tracking
- Legacy migration support

### **Questions Table**
```sql
CREATE TABLE questions (
    id VARCHAR(36) PRIMARY KEY,
    exam_id VARCHAR(36) REFERENCES exams(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) DEFAULT 'multiple_choice',
    options JSON NOT NULL,
    correct_answer VARCHAR(10) NOT NULL,
    explanation TEXT,
    difficulty VARCHAR(10) DEFAULT 'medium',
    order_index INTEGER DEFAULT 0,
    points INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_questions_exam_id ON questions(exam_id);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_order ON questions(exam_id, order_index);
```

**Purpose:** Question content and metadata
**Key Features:**
- Multiple choice questions with 4 options
- Flexible options storage (JSON)
- Difficulty levels (EASY/MEDIUM/HARD)
- Question ordering within exams
- Detailed explanations for learning

### **ExamAttempts Table**
```sql
CREATE TABLE exam_attempts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    exam_id VARCHAR(36) REFERENCES exams(id),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    score INTEGER,
    answers JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_attempts_user_id ON exam_attempts(user_id);
CREATE INDEX idx_attempts_exam_id ON exam_attempts(exam_id);
CREATE INDEX idx_attempts_score ON exam_attempts(score);
CREATE INDEX idx_attempts_created ON exam_attempts(created_at);
```

**Purpose:** User exam results and analytics
**Key Features:**
- Exam session tracking
- Score calculation and storage
- Answer history (JSON)
- Performance analytics support

### **RefreshTokens Table**
```sql
CREATE TABLE refresh_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
```

**Purpose:** JWT refresh token management
**Key Features:**
- Secure session management
- Token expiration tracking
- User session cleanup
- Multiple device support

---

## 🔧 DATABASE OPERATIONS

### **Migration Strategy**
```bash
# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### **Connection Configuration**
```python
# Development (SQLite)
DATABASE_URL = "sqlite+aiosqlite:///./exam_hub.db"

# Production (PostgreSQL)
DATABASE_URL = "postgresql+asyncpg://user:pass@host:port/dbname"
```

### **Performance Considerations**

**Indexes:**
- Primary keys (automatic)
- Foreign keys for relationships
- Search fields (email, title)
- Frequently filtered columns (status, role)

**Query Optimization:**
- Relationship loading with `selectinload()`
- Pagination for large result sets
- Connection pooling for concurrent access
- Query result caching (future)

---

## 📊 DATA RELATIONSHIPS

### **One-to-Many Relationships**
- **User → RefreshTokens:** One user can have multiple active sessions
- **Exam → Questions:** One exam contains multiple questions
- **User → ExamAttempts:** One user can attempt multiple exams
- **Exam → ExamAttempts:** One exam can be attempted by multiple users

### **Many-to-Many Relationships**
- **User ↔ Exam (via ExamAttempts):** Users can take multiple exams, exams can be taken by multiple users

### **Cascade Behaviors**
- **Exam deleted → Questions deleted:** CASCADE
- **User deleted → RefreshTokens deleted:** CASCADE
- **User deleted → ExamAttempts preserved:** SET NULL (for analytics)

---

## 🔒 DATA SECURITY

### **Sensitive Data Protection**
- **Passwords:** Argon2 hashing, never stored in plaintext
- **Tokens:** Secure random generation, expiration tracking
- **Personal Data:** Email validation, GDPR compliance ready

### **Data Integrity**
- **Foreign Key Constraints:** Maintain referential integrity
- **Check Constraints:** Validate enum values
- **Unique Constraints:** Prevent duplicates
- **Not Null Constraints:** Ensure required data

### **Backup Strategy**
- **Development:** SQLite file backup
- **Production:** PostgreSQL automated backups
- **Migration Safety:** Test migrations on staging first

---

## 📈 SCALING CONSIDERATIONS

### **Current Capacity**
- **Users:** 10K+ (with proper indexing)
- **Exams:** 1K+ per user
- **Questions:** 50+ per exam
- **Concurrent Users:** 100+ (with connection pooling)

### **Optimization Opportunities**
- **Read Replicas:** For analytics and reporting
- **Partitioning:** Large tables by date/user
- **Caching:** Redis for frequently accessed data
- **Search:** Elasticsearch for full-text search

---

*Database design based on current implementation and scalability requirements*
