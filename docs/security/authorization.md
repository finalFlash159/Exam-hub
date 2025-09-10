# Authorization System Documentation

## 🛡️ AUTHORIZATION OVERVIEW

Authorization trong Exam Hub được thiết kế theo **Role-Based Access Control (RBAC)** với **Resource Ownership** validation.

### **Authorization Hierarchy**
```
System Admin (ADMIN)
    ├── Full system access
    ├── User management
    ├── All exams access
    └── System configuration

Regular User (USER)  
    ├── Own profile management
    ├── Own exams only
    ├── Public exam access
    └── Limited upload permissions
```

---

## 🎭 ROLE-BASED ACCESS CONTROL

### **User Roles**

**USER (Default Role):**
- ✅ Create and manage own exams
- ✅ Upload files for own use
- ✅ Take public exams
- ✅ View own exam results
- ❌ Cannot access other users' data
- ❌ Cannot perform admin functions

**ADMIN (Elevated Role):**
- ✅ All USER permissions
- ✅ View all users and exams
- ✅ Manage system settings
- ✅ Delete any content
- ✅ Access system analytics
- ✅ User account management

### **Role Implementation**
```python
# Current: Basic enum in user model
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

# TODO: Extended role system with permissions
class Permission(str, enum.Enum):
    READ_OWN_EXAMS = "read:own_exams"
    WRITE_OWN_EXAMS = "write:own_exams"
    READ_ALL_EXAMS = "read:all_exams"
    DELETE_ANY_EXAM = "delete:any_exam"
    MANAGE_USERS = "manage:users"
```

---

## 🔒 RESOURCE OWNERSHIP

### **Ownership Model**

**Exam Ownership:**
- Creator has full CRUD access
- Public exams readable by all authenticated users
- Private exams accessible only by creator

**File Ownership:**
- Uploader has full access (read, delete)
- Files are user-scoped by default
- No sharing mechanism (yet)

**Attempt Ownership:**
- Users can only view their own exam attempts
- Exam creators can view attempts on their exams

### **Ownership Validation (TODO)**
```python
# Example implementation needed
async def check_exam_ownership(exam_id: str, user_id: str) -> bool:
    """Check if user owns or can access exam"""
    exam = await exam_repository.get_by_id(exam_id)
    if not exam:
        return False
    
    # Owner access
    if exam.creator_id == user_id:
        return True
    
    # Public exam access
    if exam.is_public:
        return True
        
    return False
```

---

## ⚠️ CURRENT AUTHORIZATION STATUS

### **🚨 CRITICAL SECURITY GAPS**

**No Authorization Middleware:**
- All endpoints currently public
- No role checking implemented
- No ownership validation
- Admin functions accessible to all

**Missing Permission Checks:**
- Users can access any exam by ID
- File uploads not user-scoped
- No resource ownership validation
- Admin endpoints don't exist yet

**No Access Control:**
- Database queries don't filter by user
- No user-scoped data access
- Cross-user data exposure possible

---

## 🎯 IMPLEMENTATION PLAN

### **Phase 1: Basic Authorization (CRITICAL)**

**1. Role-Based Route Protection:**
```python
# TODO: Implement role checker
async def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Usage in endpoints
@router.get("/admin/users")
async def list_users(
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    # Only admins can access
    pass
```

**2. Resource Ownership Validation:**
```python
# TODO: Implement ownership checker
async def check_exam_access(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    exam_service = ExamService(db)
    exam = await exam_service.get_exam_by_id(exam_id)
    
    if not exam:
        raise HTTPException(404, "Exam not found")
    
    # Check ownership or public access
    if exam.creator_id != current_user.id and not exam.is_public:
        raise HTTPException(403, "Access denied")
    
    return exam

# Usage in endpoints
@router.get("/exam/{exam_id}")
async def get_exam(
    exam: dict = Depends(check_exam_access)
):
    return exam
```

### **Phase 2: Advanced Authorization**

**3. Permission-Based System:**
```python
# TODO: Permission decorator
def require_permission(permission: str):
    def permission_checker(current_user: User = Depends(get_current_user)):
        user_permissions = get_user_permissions(current_user.role)
        if permission not in user_permissions:
            raise HTTPException(403, "Permission denied")
        return current_user
    return permission_checker
```

**4. User-Scoped Queries:**
```python
# TODO: Update repositories to filter by user
async def list_user_exams(user_id: str) -> List[Exam]:
    """Get only exams owned by user"""
    return await exam_repository.get_by_creator(user_id)

async def list_accessible_exams(user_id: str) -> List[Exam]:
    """Get exams user can access (owned + public)"""
    owned = await exam_repository.get_by_creator(user_id)
    public = await exam_repository.get_public_exams()
    return owned + public
```

---

## 🔐 ENDPOINT PROTECTION MATRIX

### **Current Status (ALL PUBLIC ⚠️)**

| Endpoint | Current | Should Be | Authorization |
|----------|---------|-----------|---------------|
| `POST /auth/*` | Public ✅ | Public ✅ | None |
| `GET /health` | Public ✅ | Public ✅ | None |
| `POST /exam/generate` | Public ❌ | Auth Required | User+ |
| `POST /exam/save` | Public ❌ | Auth Required | User+ |
| `GET /exam/{id}` | Public ❌ | Auth + Ownership | Owner/Public |
| `POST /upload/upload` | Public ❌ | Auth Required | User+ |
| `GET /upload/{id}` | Public ❌ | Auth + Ownership | Owner Only |
| `DELETE /upload/{id}` | Public ❌ | Auth + Ownership | Owner Only |

### **Planned Admin Endpoints**

| Endpoint | Authorization | Description |
|----------|---------------|-------------|
| `GET /admin/users` | Admin Only | List all users |
| `GET /admin/exams` | Admin Only | List all exams |
| `DELETE /admin/user/{id}` | Admin Only | Delete user |
| `PUT /admin/user/{id}/role` | Admin Only | Change user role |
| `GET /admin/analytics` | Admin Only | System stats |

---

## 🧪 AUTHORIZATION TESTING

### **Test Scenarios (TODO)**

**Role-Based Tests:**
```python
def test_user_cannot_access_admin_endpoints():
    # Regular user tries admin endpoint
    # Should return 403 Forbidden
    pass

def test_admin_can_access_all_endpoints():
    # Admin user accesses all endpoints
    # Should return 200 OK
    pass
```

**Ownership Tests:**
```python
def test_user_cannot_access_others_exams():
    # User A tries to access User B's private exam
    # Should return 403 Forbidden
    pass

def test_user_can_access_public_exams():
    # User A accesses User B's public exam
    # Should return 200 OK
    pass

def test_user_can_access_own_exams():
    # User accesses their own private exam
    # Should return 200 OK
    pass
```

---

## 🎯 IMPLEMENTATION PRIORITIES

### **Immediate (Critical Security)**
1. **Protect exam endpoints** - Require authentication
2. **Protect upload endpoints** - User-scoped access
3. **Add ownership validation** - Check exam access rights
4. **Implement role checker** - Basic RBAC

### **High Priority**
1. **User-scoped database queries** - Filter data by user
2. **Admin role enforcement** - Protect admin functions
3. **Resource ownership validation** - Comprehensive checks
4. **Permission system foundation** - Extensible authorization

### **Medium Priority**
1. **Advanced permissions** - Granular access control
2. **Audit logging** - Track authorization decisions
3. **Rate limiting** - Prevent abuse
4. **Session management** - Multi-device authorization

---

## 🔧 CONFIGURATION

### **Authorization Settings**
```python
# TODO: Add to settings
class Settings:
    # Authorization
    enable_rbac: bool = True
    default_user_role: str = "user"
    admin_email_domains: List[str] = []  # Auto-admin for certain domains
    
    # Permissions
    allow_public_exam_creation: bool = True
    max_exams_per_user: int = 100
    max_upload_size_per_user: int = 100 * 1024 * 1024  # 100MB
```

### **Role Configuration**
```python
# TODO: Configurable role permissions
ROLE_PERMISSIONS = {
    "user": [
        "read:own_profile",
        "write:own_profile", 
        "create:own_exams",
        "read:own_exams",
        "write:own_exams",
        "delete:own_exams",
        "read:public_exams",
        "upload:own_files"
    ],
    "admin": [
        "*"  # All permissions
    ]
}
```

---

## 🚨 SECURITY CONSIDERATIONS

### **Authorization Bypass Prevention**
- ✅ Always validate user identity before authorization
- ✅ Check permissions at API layer, not just frontend
- ✅ Use database-level constraints where possible
- ✅ Log all authorization decisions
- ✅ Fail securely (deny by default)

### **Common Authorization Vulnerabilities**
- **Insecure Direct Object Reference:** User can access others' data by changing IDs
- **Missing Function Level Access Control:** Admin functions accessible to regular users
- **Privilege Escalation:** Users can elevate their own permissions
- **Session Fixation:** Authorization tied to compromised sessions

### **Mitigation Strategies**
- **Input Validation:** Validate all user inputs
- **Output Filtering:** Filter data based on user permissions
- **Least Privilege:** Grant minimum necessary permissions
- **Defense in Depth:** Multiple layers of authorization
- **Regular Audits:** Review and test authorization logic

---

*Authorization system documentation - Implementation required for production security*
