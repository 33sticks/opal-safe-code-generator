"""Generated Code model."""
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Float, JSON, DateTime, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.enums import ValidationStatus, DeploymentStatus, CodeStatus


class GeneratedCode(Base):
    """Generated Code model for tracking generated code instances."""
    
    __tablename__ = "generated_code"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    request_data = Column(JSON, nullable=True)
    generated_code = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    validation_status = Column(SQLEnum(ValidationStatus, native_enum=False, length=50), nullable=False, default=ValidationStatus.PENDING, index=True)
    user_feedback = Column(Text, nullable=True)
    deployment_status = Column(SQLEnum(DeploymentStatus, native_enum=False, length=50), nullable=False, default=DeploymentStatus.PENDING)
    error_logs = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Review fields
    status = Column(String(50), nullable=False, default='generated', index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # LLM cost tracking fields
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    llm_cost_usd = Column(Numeric(precision=10, scale=4), nullable=True)
    
    # Relationships
    brand = relationship("Brand", back_populates="generated_code")
    conversation = relationship("Conversation", backref="generated_code_items")
    user = relationship("User", backref="generated_code_items", foreign_keys=[user_id])
    reviewer = relationship("User", backref="reviewed_code_items", foreign_keys=[reviewer_id])
