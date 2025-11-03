"""Page Type Knowledge model."""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.enums import TestType


class PageTypeKnowledge(Base):
    """Page Type Knowledge model for page-specific code generation patterns."""
    
    __tablename__ = "page_type_knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    test_type = Column(SQLEnum(TestType, native_enum=False, length=50), nullable=False)
    template_code = Column(Text, nullable=False)
    description = Column(String(500), nullable=True)
    version = Column(String(50), nullable=False, default="1.0")
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="page_type_knowledge")

