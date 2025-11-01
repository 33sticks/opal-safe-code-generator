"""Analytics Pydantic schemas."""
from typing import Optional, List, Dict
from datetime import date, datetime
from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    """Overview metrics for analytics dashboard."""
    total_code_generations: int
    active_users: int
    average_confidence: float
    approval_rate: float
    rejection_rate: float
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    
    class Config:
        from_attributes = True


class UsageDataPoint(BaseModel):
    """Data point for usage over time chart."""
    date: date
    count: int
    brand_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class QualityMetrics(BaseModel):
    """Quality metrics including confidence distribution."""
    confidence_distribution: Dict[str, int]  # ranges: 0-20%, 20-40%, etc.
    status_breakdown: Dict[str, int]  # generated, approved, rejected
    average_confidence: float
    
    class Config:
        from_attributes = True


class BrandPerformance(BaseModel):
    """Performance metrics per brand."""
    brand_id: int
    brand_name: str
    code_generations: int
    average_confidence: float
    approval_rate: float
    top_users: List[str]  # user emails
    
    class Config:
        from_attributes = True


class UserActivity(BaseModel):
    """User activity metrics."""
    user_id: int
    user_email: str
    user_name: Optional[str] = None
    code_generations: int
    average_confidence: float
    last_active: datetime
    
    class Config:
        from_attributes = True


class LLMCostMetrics(BaseModel):
    """LLM cost metrics (super admin only)."""
    total_cost_usd: float
    average_cost_per_generation: float
    total_tokens: int
    total_generations: int
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    
    class Config:
        from_attributes = True


class BrandLLMCost(BaseModel):
    """LLM cost breakdown by brand (super admin only)."""
    brand_name: str
    total_cost_usd: float
    generations: int
    cost_per_generation: Optional[float] = None  # Calculated
    
    class Config:
        from_attributes = True

