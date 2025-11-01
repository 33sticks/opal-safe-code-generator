"""Brand API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db
from app.models.brand import Brand
from app.models.user import User
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse
from app.core.exceptions import NotFoundException, ConflictException
from app.core.auth import require_role

router = APIRouter()


@router.get("/", response_model=List[BrandResponse], status_code=status.HTTP_200_OK)
async def list_brands(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """List all brands with pagination."""
    result = await db.execute(select(Brand).offset(skip).limit(limit))
    brands = result.scalars().all()
    return brands


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand: BrandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Create a new brand."""
    # Check for duplicate name
    result = await db.execute(select(Brand).where(Brand.name == brand.name))
    existing = result.scalar_one_or_none()
    if existing:
        raise ConflictException(f"Brand with name '{brand.name}' already exists")
    
    db_brand = Brand(**brand.model_dump())
    db.add(db_brand)
    await db.commit()
    await db.refresh(db_brand)
    return db_brand


@router.get("/{brand_id}", response_model=BrandResponse, status_code=status.HTTP_200_OK)
async def get_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Get a brand by ID."""
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise NotFoundException("Brand", brand_id)
    
    return brand


@router.put("/{brand_id}", response_model=BrandResponse, status_code=status.HTTP_200_OK)
async def update_brand(
    brand_id: int,
    brand_update: BrandUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update a brand."""
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise NotFoundException("Brand", brand_id)
    
    # Check for duplicate name if name is being updated
    if brand_update.name and brand_update.name != brand.name:
        name_check = await db.execute(select(Brand).where(Brand.name == brand_update.name))
        existing = name_check.scalar_one_or_none()
        if existing:
            raise ConflictException(f"Brand with name '{brand_update.name}' already exists")
    
    # Update fields
    update_data = brand_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)
    
    await db.commit()
    await db.refresh(brand)
    return brand


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Delete a brand."""
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise NotFoundException("Brand", brand_id)
    
    await db.delete(brand)
    await db.commit()
    return None

