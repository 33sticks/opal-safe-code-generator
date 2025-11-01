"""Generated Code Pydantic schemas."""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import ValidationStatus, DeploymentStatus, CodeStatus


class GeneratedCodeBase(BaseModel):
    """Base generated code schema."""
    brand_id: int
    request_data: Optional[Dict[str, Any]] = None
    generated_code: str = Field(..., min_length=1)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    validation_status: ValidationStatus = Field(default=ValidationStatus.PENDING)
    user_feedback: Optional[str] = None
    deployment_status: DeploymentStatus = Field(default=DeploymentStatus.PENDING)
    error_logs: Optional[Dict[str, Any]] = None


class GeneratedCodeCreate(GeneratedCodeBase):
    """Schema for creating generated code."""
    pass


class GeneratedCodeUpdate(BaseModel):
    """Schema for updating generated code."""
    brand_id: Optional[int] = None
    request_data: Optional[Dict[str, Any]] = None
    generated_code: Optional[str] = Field(None, min_length=1)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    validation_status: Optional[ValidationStatus] = None
    user_feedback: Optional[str] = None
    deployment_status: Optional[DeploymentStatus] = None
    error_logs: Optional[Dict[str, Any]] = None


class GeneratedCodeResponse(GeneratedCodeBase):
    """Schema for generated code response."""
    id: int
    conversation_id: Optional[str] = None
    user_id: Optional[int] = None
    status: CodeStatus = Field(default=CodeStatus.GENERATED)
    reviewer_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CodeReviewRequest(BaseModel):
    """Schema for code review request."""
    status: str = Field(..., pattern="^(approved|rejected)$")
    reviewer_notes: Optional[str] = None


class CodeReviewResponse(BaseModel):
    """Schema for code review response."""
    id: int
    status: CodeStatus
    reviewed_at: datetime
    reviewer: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class GeneratedCodeEnhancedResponse(GeneratedCodeResponse):
    """Enhanced response with relationships and preview."""
    brand_name: Optional[str] = None
    user_email: Optional[str] = None
    conversation_preview: Optional[str] = None
    reviewer_email: Optional[str] = None
    
    class Config:
        from_attributes = True


class ConversationForCodeResponse(BaseModel):
    """Response for conversation associated with code."""
    conversation_id: str
    messages: list[Dict[str, Any]]
    user: Dict[str, Any]
    brand: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
