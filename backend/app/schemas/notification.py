"""Notification schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Notification response schema."""
    id: int
    user_id: int
    generated_code_id: Optional[int] = None
    type: str
    title: str
    message: str
    read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    """Unread notification count response schema."""
    count: int


class NotificationCreate(BaseModel):
    """Internal schema for creating notifications."""
    user_id: int
    generated_code_id: Optional[int] = None
    type: str = Field(..., description="Notification type: code_approved, code_rejected, code_under_review")
    title: str
    message: str



