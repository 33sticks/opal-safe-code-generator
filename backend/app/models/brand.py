"""Brand model."""
from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.enums import BrandStatus


class Brand(Base):
    """Brand model representing a company/brand."""
    
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    domain = Column(String(255), nullable=False)
    status = Column(SQLEnum(BrandStatus, native_enum=False, length=50), nullable=False, default=BrandStatus.ACTIVE)
    code_template = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    templates = relationship("Template", back_populates="brand", cascade="all, delete-orphan")
    selectors = relationship("DOMSelector", back_populates="brand", cascade="all, delete-orphan")
    rules = relationship("CodeRule", back_populates="brand", cascade="all, delete-orphan")
    generated_code = relationship("GeneratedCode", back_populates="brand", cascade="all, delete-orphan")
