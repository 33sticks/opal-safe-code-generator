"""Page Type Knowledge Pydantic schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import TestType


class PageTypeKnowledgeBase(BaseModel):
    """Base page type knowledge schema."""
    brand_id: int
    test_type: TestType
    template_code: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    version: str = Field(default="1.0", max_length=50)
    is_active: bool = Field(default=True)


class PageTypeKnowledgeCreate(PageTypeKnowledgeBase):
    """Schema for creating page type knowledge."""
    pass


class PageTypeKnowledgeUpdate(BaseModel):
    """Schema for updating page type knowledge."""
    brand_id: Optional[int] = None
    test_type: Optional[TestType] = None
    template_code: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    version: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class PageTypeKnowledgeResponse(PageTypeKnowledgeBase):
    """Schema for page type knowledge response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PageTypeKnowledgeEnhancedResponse(PageTypeKnowledgeResponse):
    """Enhanced response with brand name."""
    brand_name: Optional[str] = None
    
    class Config:
        from_attributes = True

