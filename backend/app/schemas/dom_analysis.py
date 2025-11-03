"""DOM Analysis Pydantic schemas for Claude API responses."""
from typing import List, Optional
from pydantic import BaseModel, Field


class DomSelector(BaseModel):
    """Schema for a single DOM selector with relationships."""
    selector: str = Field(..., description="CSS selector string")
    description: str = Field(..., description="Human-readable description of the element")
    stability_score: float = Field(..., ge=0.0, le=1.0, description="Stability score between 0.0 and 1.0")
    element_type: str = Field(..., description="Type of element: interactive, content, container, or data")
    parent: Optional[str] = Field(None, description="CSS selector for parent element")
    children: List[str] = Field(default_factory=list, description="List of CSS selectors for child elements")
    siblings: List[str] = Field(default_factory=list, description="List of CSS selectors for sibling elements")


class DomRelationships(BaseModel):
    """Schema for DOM element relationships grouped by type."""
    containers: List[str] = Field(default_factory=list, description="List of container element selectors")
    interactive: List[str] = Field(default_factory=list, description="List of interactive element selectors")
    content: List[str] = Field(default_factory=list, description="List of content element selectors")


class DomAnalysisResult(BaseModel):
    """Complete DOM analysis result from Claude API."""
    selectors: List[DomSelector] = Field(..., description="List of analyzed DOM selectors")
    relationships: DomRelationships = Field(..., description="Element relationships grouped by type")
    patterns: List[str] = Field(..., description="Identified patterns in the DOM structure")
    recommendations: List[str] = Field(..., description="Recommendations for selector stability and automation")
    warnings: List[str] = Field(default_factory=list, description="Warnings about unstable selectors or patterns")

