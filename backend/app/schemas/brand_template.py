"""Brand template Pydantic schemas."""
from typing import Dict, Any
from pydantic import BaseModel, Field


class TemplateSummary(BaseModel):
    """Schema for template summary (list endpoint)."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    platform: str = Field(..., description="Platform identifier (e.g., 'optimizely', 'agnostic')")


class TemplateDetail(BaseModel):
    """Schema for full template detail."""
    class Config:
        # Allow arbitrary types for dynamic nested structures
        extra = "allow"
    
    # Required fields
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    platform: str = Field(..., description="Platform identifier")
    
    # Optional fields (dynamic structure)
    code_structure: Dict[str, Any] = Field(default_factory=dict)
    header_format: Dict[str, Any] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    logging: Dict[str, Any] = Field(default_factory=dict)
    utilities: Dict[str, Any] = Field(default_factory=dict)
    error_handling: Dict[str, Any] = Field(default_factory=dict)
    features: Dict[str, Any] = Field(default_factory=dict)

