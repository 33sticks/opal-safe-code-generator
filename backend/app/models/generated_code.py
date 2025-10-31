"""Generated Code model."""
from sqlalchemy import Column, Integer, String, Text, Float, JSON, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.enums import ValidationStatus, DeploymentStatus


class GeneratedCode(Base):
    """Generated Code model for tracking generated code instances."""
    
    __tablename__ = "generated_code"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    request_data = Column(JSON, nullable=True)
    generated_code = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    validation_status = Column(SQLEnum(ValidationStatus, native_enum=False, length=50), nullable=False, default=ValidationStatus.PENDING, index=True)
    user_feedback = Column(Text, nullable=True)
    deployment_status = Column(SQLEnum(DeploymentStatus, native_enum=False, length=50), nullable=False, default=DeploymentStatus.PENDING)
    error_logs = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    brand = relationship("Brand", back_populates="generated_code")
