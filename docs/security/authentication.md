# Authentication System Documentation

## 🔐 AUTHENTICATION OVERVIEW

Exam Hub sử dụng **JWT-based authentication** với **email verification** và **secure password hashing**.

### **Authentication Flow**
```
Registration → Email Verification → Login → JWT Token → Protected Access
     ↓              ↓                ↓         ↓              ↓
  Hash Password  Send Email      Validate    Generate      Middleware
  Store User     Token Check     Credentials  Access/Refresh Check Token
```

---

## 🏗️ AUTHENTICATION ARCHITECTURE

### **Core Components**

**1. Authentication Service (`auth_service.py`)**
- User registration with email verification
- Login with credential validation
- Password reset functionality
- JWT token management
- Session handling

**2. Security Utilities (`security.py`)**
- Password hashing (Argon2)
- JWT token creation/validation
- Password strength validation
- Token expiration management

**3. User Repository (`user_repository.py`)**
- User CRUD operations
- Token storage and validation
- Email verification handling
- Password reset token management

**4. Email Service (`email_service.py`)**
- Verification email sending
- Password reset emails
- Brevo API integration
- Email template management

---

## 🔑 JWT TOKEN SYSTEM

### **Token Types**

**Access Token:**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "user",
  "exp": 1234567890,
  "iat": 1234567860
}
```
- **Lifetime:** 30 minutes
- **Purpose:** API access authorization
- **Storage:** Frontend memory (not localStorage)

**Refresh Token:**
```json
{
  "sub": "user_id", 
  "type": "refresh",
  "exp": 1234567890,
  "iat": 1234567860
}
```
- **Lifetime:** 7 days (30 days if "remember me")
- **Purpose:** Generate new access tokens
- **Storage:** Database + httpOnly cookie

### **Token Security Features**
- ✅ **Secure Secret:** HS256 algorithm with strong secret key
- ✅ **Expiration:** Short-lived access tokens
- ✅ **Rotation:** Refresh token rotation on use
- ✅ **Revocation:** Database-stored refresh tokens can be revoked
- ⚠️ **TODO:** Token blacklisting for immediate revocation

---

## 🔒 PASSWORD SECURITY

### **Hashing Algorithm**
```python
# Using Argon2 (recommended by OWASP)
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# Hash password
hashed = pwd_context.hash(plain_password)

# Verify password  
is_valid = pwd_context.verify(plain_password, hashed)
```

### **Password Requirements**
- ✅ **Minimum Length:** 8 characters
- ⚠️ **TODO:** Complexity requirements (uppercase, lowercase, numbers, symbols)
- ⚠️ **TODO:** Password history (prevent reuse)
- ⚠️ **TODO:** Password strength meter

### **Password Reset Flow**
```
1. User requests reset → Email validation
2. Generate secure token → Store with expiration
3. Send reset email → Token in secure link
4. User clicks link → Validate token + expiration
5. New password → Hash and store → Clear reset token
```

---

## �� EMAIL VERIFICATION

### **Verification Flow**
```
1. User registers → Generate verification token
2. Store token → Send verification email
3. User clicks link → Validate token
4. Mark email verified → Enable full account access
```

### **Email Templates**
**Verification Email:**
- Welcome message with brand identity
- Secure verification link
- Clear instructions
- Security warnings

**Password Reset Email:**
- Security-focused messaging
- Time-limited reset link
- Clear expiration notice
- Support contact information

---

## 🛡️ CURRENT SECURITY STATUS

### **✅ IMPLEMENTED FEATURES**

**User Management:**
- ✅ User registration with validation
- ✅ Email verification required
- ✅ Secure password hashing (Argon2)
- ✅ Password reset functionality
- ✅ Account activation/deactivation

**Token Management:**
- ✅ JWT access token generation
- ✅ Refresh token with database storage
- ✅ Token expiration handling
- ✅ "Remember me" functionality
- ✅ Token refresh endpoint

**Session Management:**
- ✅ Multiple device support
- ✅ Session cleanup on logout
- ✅ Token rotation on refresh
- ✅ Last login tracking

### **⚠️ CRITICAL MISSING PIECES**

**JWT Middleware (HIGH PRIORITY):**
```python
# MISSING: Authentication dependency
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract and validate JWT token, return current user"""
    # TODO: Implement token validation
    # TODO: Handle token expiration
    # TODO: Return user object
    pass

# MISSING: OAuth2 scheme setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
```

**Protected Route Dependencies:**
```python
# MISSING: Route protection
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    # TODO: Only authenticated users can access
    pass
```

**Authorization Middleware:**
```python
# MISSING: Role-based access control
async def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(403, "Insufficient permissions")
        return current_user
    return role_checker
```

---

## 🚨 SECURITY VULNERABILITIES

### **Current Risks**

**1. No Route Protection (CRITICAL):**
- All endpoints are currently public
- No authentication required for sensitive operations
- User data accessible without login

**2. Missing Authorization (HIGH):**
- No role-based access control
- No resource ownership validation
- Admin functions accessible to all users

**3. Token Validation (HIGH):**
- JWT tokens generated but not validated on requests
- No middleware to check token validity
- No automatic token refresh handling

### **Immediate Security Fixes Needed**

**1. Implement JWT Middleware:**
```python
# backend/app/utils/auth_middleware.py
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
        
        # Get user from database
        user = await user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise credentials_exception
            
        return user
    except JWTError:
        raise credentials_exception
```

**2. Protect Critical Endpoints:**
```python
# Protect exam operations
@router.post("/exam/save")
async def save_exam(
    request: SaveExamRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    # Only authenticated users can save exams
    pass

# Protect upload operations  
@router.post("/upload/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Only authenticated users can upload files
    pass
```

---

## 🎯 IMPLEMENTATION ROADMAP

### **Phase 1: Critical Security (IMMEDIATE)**
1. **Create JWT authentication middleware**
2. **Implement get_current_user dependency**
3. **Protect all sensitive endpoints**
4. **Add OAuth2 scheme configuration**

### **Phase 2: Authorization (HIGH PRIORITY)**
1. **Implement role-based access control**
2. **Add resource ownership validation**
3. **Create admin-only endpoints**
4. **Add permission checking utilities**

### **Phase 3: Advanced Security (MEDIUM PRIORITY)**
1. **Token blacklisting system**
2. **Rate limiting for auth endpoints**
3. **Account lockout after failed attempts**
4. **Security audit logging**

### **Phase 4: Production Hardening (BEFORE DEPLOYMENT)**
1. **Security headers middleware**
2. **CORS configuration**
3. **Input sanitization**
4. **SQL injection prevention**

---

## 🧪 TESTING AUTHENTICATION

### **Manual Testing Flow**
```bash
# 1. Register user
curl -X POST "http://localhost:5001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123", "full_name": "Test User"}'

# 2. Verify email (get token from email/logs)
curl -X POST "http://localhost:5001/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{"token": "verification_token_here"}'

# 3. Login
curl -X POST "http://localhost:5001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# 4. Use access token for protected routes (TODO)
curl -X GET "http://localhost:5001/protected" \
  -H "Authorization: Bearer ACCESS_TOKEN_HERE"
```

### **Automated Testing**
```python
# TODO: Comprehensive auth test suite
def test_registration_flow():
    # Test user registration
    # Test email verification
    # Test login with verified account
    pass

def test_password_reset_flow():
    # Test forgot password request
    # Test reset token validation
    # Test password update
    pass

def test_jwt_token_validation():
    # Test valid token acceptance
    # Test expired token rejection
    # Test invalid token rejection
    pass
```

---

## 🔐 PRODUCTION SECURITY CHECKLIST

### **Before Deployment:**
- [ ] Strong SECRET_KEY in production
- [ ] HTTPS enforcement
- [ ] Secure cookie settings
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] Database access restricted
- [ ] Email service configured
- [ ] Token expiration appropriate
- [ ] Password policies enforced
- [ ] Security monitoring enabled

---

*Authentication system documentation based on current implementation and security best practices*
