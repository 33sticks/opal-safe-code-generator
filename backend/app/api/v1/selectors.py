"""DOM Selector API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.dom_selector import DOMSelector
from app.models.brand import Brand
from app.models.user import User
from app.schemas.dom_selector import DOMSelectorCreate, DOMSelectorUpdate, DOMSelectorResponse
from app.core.exceptions import NotFoundException
from app.core.auth import require_role, get_user_brand_access

router = APIRouter()


@router.get("/", response_model=List[DOMSelectorResponse], status_code=status.HTTP_200_OK)
async def list_selectors(
    skip: int = 0,
    limit: int = 100,
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """List DOM selectors with optional brand filter. Filtered by user's brand access."""
    query = select(DOMSelector)
    
    # Filter by brand access first
    accessible_brands = get_user_brand_access(current_user)
    if accessible_brands:  # Not super admin - filter to their brand
        query = query.where(DOMSelector.brand_id.in_(accessible_brands))
    
    # Additional brand_id filter (for super admins)
    if brand_id:
        query = query.where(DOMSelector.brand_id == brand_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    selectors = result.scalars().all()
    return selectors


@router.post("/", response_model=DOMSelectorResponse, status_code=status.HTTP_201_CREATED)
async def create_selector(
    selector: DOMSelectorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Create a new DOM selector."""
    # Verify brand exists
    brand_result = await db.execute(select(Brand).where(Brand.id == selector.brand_id))
    brand = brand_result.scalar_one_or_none()
    if not brand:
        raise NotFoundException("Brand", selector.brand_id)
    
    db_selector = DOMSelector(**selector.model_dump())
    db.add(db_selector)
    await db.commit()
    await db.refresh(db_selector)
    return db_selector


@router.get("/{selector_id}", response_model=DOMSelectorResponse, status_code=status.HTTP_200_OK)
async def get_selector(
    selector_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Get a DOM selector by ID."""
    result = await db.execute(select(DOMSelector).where(DOMSelector.id == selector_id))
    selector = result.scalar_one_or_none()
    
    if not selector:
        raise NotFoundException("DOMSelector", selector_id)
    
    return selector


@router.put("/{selector_id}", response_model=DOMSelectorResponse, status_code=status.HTTP_200_OK)
async def update_selector(
    selector_id: int,
    selector_update: DOMSelectorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update a DOM selector."""
    result = await db.execute(select(DOMSelector).where(DOMSelector.id == selector_id))
    selector = result.scalar_one_or_none()
    
    if not selector:
        raise NotFoundException("DOMSelector", selector_id)
    
    # Verify brand exists if brand_id is being updated
    if selector_update.brand_id and selector_update.brand_id != selector.brand_id:
        brand_result = await db.execute(select(Brand).where(Brand.id == selector_update.brand_id))
        brand = brand_result.scalar_one_or_none()
        if not brand:
            raise NotFoundException("Brand", selector_update.brand_id)
    
    # Update fields
    update_data = selector_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(selector, field, value)
    
    await db.commit()
    await db.refresh(selector)
    return selector


@router.delete("/{selector_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_selector(
    selector_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Delete a DOM selector."""
    result = await db.execute(select(DOMSelector).where(DOMSelector.id == selector_id))
    selector = result.scalar_one_or_none()
    
    if not selector:
        raise NotFoundException("DOMSelector", selector_id)
    
    await db.delete(selector)
    await db.commit()
    return None

