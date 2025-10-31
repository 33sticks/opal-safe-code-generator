"""Code Rule model."""
from sqlalchemy import Column, Integer, String, Text, Integer as SQLInteger, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.enums import RuleType


class CodeRule(Base):
    """Code Rule model for brand-specific code generation rules."""
    
    __tablename__ = "code_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_type = Column(SQLEnum(RuleType, native_enum=False, length=50), nullable=False)
    rule_content = Column(Text, nullable=False)
    priority = Column(SQLInteger, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="rules")
