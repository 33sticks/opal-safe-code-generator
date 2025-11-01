"""User Pydantic schemas."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from app.schemas.auth import UserResponse


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")
    name: str = Field(..., max_length=255, description="User full name")
    brand_id: Optional[int] = Field(None, description="Associated brand ID (None for super_admin users)")
    brand_role: str = Field("brand_user", description="User brand role (super_admin, brand_admin, brand_user)")
    role: Optional[str] = Field("user", description="User role (for backward compatibility)")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

