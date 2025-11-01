"""Chat Pydantic schemas."""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.enums import ConversationStatus
from app.schemas.generated_code import GeneratedCodeResponse


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    role: str  # 'user' or 'assistant'
    content: str
    created_at: datetime
    generated_code_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class ChatMessageRequest(BaseModel):
    """Schema for chat message request."""
    message: str = Field(..., min_length=1, description="User message content")
    conversation_id: Optional[UUID] = Field(None, description="Conversation ID (optional, creates new if not provided)")


class ConversationPreview(BaseModel):
    """Schema for conversation preview in list."""
    id: UUID
    preview: str = Field(..., description="First user message preview")
    last_message: Optional[str] = Field(None, description="Last message content")
    created_at: datetime
    updated_at: datetime
    status: ConversationStatus
    
    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    conversation_id: UUID
    message: str = Field(..., description="Assistant's response message")
    generated_code: Optional[GeneratedCodeResponse] = Field(None, description="Generated code if ready")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score if code generated")
    status: str = Field(..., description="Status: 'gathering_info' or 'code_generated'")


class ConversationHistoryResponse(BaseModel):
    """Schema for full conversation history."""
    conversation_id: UUID
    messages: List[MessageResponse] = Field(..., description="All messages in conversation")
    generated_code: Optional[GeneratedCodeResponse] = Field(None, description="Generated code if available")
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

