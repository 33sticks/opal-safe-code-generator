"""Brand Pydantic schemas."""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import BrandStatus


class BrandBase(BaseModel):
    """Base brand schema."""
    name: str = Field(..., min_length=1, max_length=255)
    domain: str = Field(..., min_length=1, max_length=255)
    status: BrandStatus = BrandStatus.ACTIVE
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class BrandCreate(BrandBase):
    """Schema for creating a brand."""
    pass


class BrandUpdate(BaseModel):
    """Schema for updating a brand."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[BrandStatus] = None
    config: Optional[Dict[str, Any]] = None


class BrandResponse(BrandBase):
    """Schema for brand response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

