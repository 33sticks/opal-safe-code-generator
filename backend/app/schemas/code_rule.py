"""Code Rule Pydantic schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import RuleType


class CodeRuleBase(BaseModel):
    """Base code rule schema."""
    brand_id: int
    rule_type: RuleType
    rule_content: str = Field(..., min_length=1)
    priority: int = Field(default=1, ge=1, le=10)


class CodeRuleCreate(CodeRuleBase):
    """Schema for creating a code rule."""
    pass


class CodeRuleUpdate(BaseModel):
    """Schema for updating a code rule."""
    brand_id: Optional[int] = None
    rule_type: Optional[RuleType] = None
    rule_content: Optional[str] = Field(None, min_length=1)
    priority: Optional[int] = Field(None, ge=1, le=10)


class CodeRuleResponse(CodeRuleBase):
    """Schema for code rule response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
