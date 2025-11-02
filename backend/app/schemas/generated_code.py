"""Generated Code Pydantic schemas."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import ValidationStatus, DeploymentStatus, CodeStatus


class ConfidenceBreakdown(BaseModel):
    """Schema for confidence score breakdown."""
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    template_score: float = Field(..., ge=0.0, le=0.3, description="Template adherence score (0-0.3)")
    rule_score: float = Field(..., ge=0.0, le=0.4, description="Rule compliance score (0-0.4)")
    selector_score: float = Field(..., ge=0.0, le=0.3, description="Selector validation score (0-0.3)")
    rule_violations: List[str] = Field(default_factory=list, description="List of rule violations found")
    invalid_selectors: List[str] = Field(default_factory=list, description="List of invalid selectors found")
    is_valid: bool = Field(..., description="Whether code passed validation")
    validation_status: str = Field(..., description="Validation status: passed, failed, or warning")
    recommendation: str = Field(..., description="Recommendation: safe_to_use, review_carefully, or needs_fixes")


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
    confidence_breakdown: Optional[ConfidenceBreakdown] = Field(None, description="Confidence score breakdown if available")
    
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
