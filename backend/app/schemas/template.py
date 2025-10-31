"""Template Pydantic schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import TestType


class TemplateBase(BaseModel):
    """Base template schema."""
    brand_id: int
    test_type: TestType
    template_code: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    version: str = Field(default="1.0", max_length=50)
    is_active: bool = Field(default=True)


class TemplateCreate(TemplateBase):
    """Schema for creating a template."""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""
    brand_id: Optional[int] = None
    test_type: Optional[TestType] = None
    template_code: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    version: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Schema for template response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
