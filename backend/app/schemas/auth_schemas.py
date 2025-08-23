from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Request schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr 
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str 
    remember_me: bool = False

class EmailVerificationRequest(BaseModel):
    token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

# Response schemas
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
    
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    success: bool = True
