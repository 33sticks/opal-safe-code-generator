"""DOM Selector Pydantic schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import PageType, SelectorStatus


class DOMSelectorBase(BaseModel):
    """Base DOM selector schema."""
    brand_id: int
    page_type: PageType
    selector: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    status: SelectorStatus = Field(default=SelectorStatus.ACTIVE)


class DOMSelectorCreate(DOMSelectorBase):
    """Schema for creating a DOM selector."""
    pass


class DOMSelectorUpdate(BaseModel):
    """Schema for updating a DOM selector."""
    brand_id: Optional[int] = None
    page_type: Optional[PageType] = None
    selector: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[SelectorStatus] = None


class DOMSelectorResponse(DOMSelectorBase):
    """Schema for DOM selector response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
