"""DOM Selector model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.enums import PageType, SelectorStatus


class DOMSelector(Base):
    """DOM Selector model for brand-specific selectors."""
    
    __tablename__ = "dom_selectors"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    page_type = Column(SQLEnum(PageType, native_enum=False, length=50), nullable=False)
    selector = Column(Text, nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(SQLEnum(SelectorStatus, native_enum=False, length=50), nullable=False, default=SelectorStatus.ACTIVE, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="selectors")
