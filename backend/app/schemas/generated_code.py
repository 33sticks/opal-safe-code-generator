"""Generated Code Pydantic schemas."""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.enums import ValidationStatus, DeploymentStatus


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
    created_at: datetime
    
    class Config:
        from_attributes = True
