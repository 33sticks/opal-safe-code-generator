"""Authentication Pydantic schemas."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.enums import UserRole


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class LoginResponse(BaseModel):
    """Schema for login response."""
    token: str = Field(..., description="Session token")
    expires_at: str = Field(..., description="Token expiration timestamp (ISO format)")
    user: "UserResponse" = Field(..., description="User information")


class RegisterRequest(BaseModel):
    """Schema for user registration (admin only)."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")
    name: Optional[str] = Field(None, max_length=255, description="User full name")
    role: UserRole = Field(UserRole.USER, description="User role")
    brand_id: Optional[int] = Field(None, description="Associated brand ID (optional, for regular users)")


class UserResponse(BaseModel):
    """Schema for user information response."""
    id: int
    email: str
    name: Optional[str]
    role: UserRole
    brand_id: Optional[int]
    brand_role: str
    
    class Config:
        from_attributes = True


# Update forward reference
LoginResponse.model_rebuild()

