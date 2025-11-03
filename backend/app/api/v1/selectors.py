"""DOM Selector API endpoints."""
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload

from app.api.deps import get_db
from app.models.dom_selector import DOMSelector
from app.models.brand import Brand
from app.models.user import User
from app.schemas.dom_selector import DOMSelectorCreate, DOMSelectorUpdate, DOMSelectorResponse, DOMSelectorEnhancedResponse
from app.core.exceptions import NotFoundException
from app.core.auth import require_role, get_user_brand_access

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[DOMSelectorEnhancedResponse], status_code=status.HTTP_200_OK)
async def list_selectors(
    skip: int = 0,
    limit: int = 100,
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """List DOM selectors with optional brand filter. Filtered by user's brand access."""
    query = select(DOMSelector).options(joinedload(DOMSelector.brand))
    
    # Filter by brand access first
    accessible_brands = get_user_brand_access(current_user)
    if accessible_brands:  # Not super admin - filter to their brand
        query = query.where(DOMSelector.brand_id.in_(accessible_brands))
    
    # Additional brand_id filter (for super admins)
    if brand_id:
        query = query.where(DOMSelector.brand_id == brand_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    selectors = result.unique().scalars().all()
    
    # Build enhanced responses with brand_name
    enhanced_selectors = []
    for selector in selectors:
        enhanced_selector = DOMSelectorEnhancedResponse(
            id=selector.id,
            brand_id=selector.brand_id,
            page_type=selector.page_type,
            selector=selector.selector,
            description=selector.description,
            status=selector.status,
            relationships=selector.relationships or {},
            created_at=selector.created_at,
            updated_at=selector.updated_at,
            brand_name=selector.brand.name if selector.brand else None
        )
        enhanced_selectors.append(enhanced_selector)
    
    return enhanced_selectors


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


@router.get("/{selector_id}", response_model=DOMSelectorEnhancedResponse, status_code=status.HTTP_200_OK)
async def get_selector(
    selector_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Get a DOM selector by ID."""
    result = await db.execute(
        select(DOMSelector)
        .options(joinedload(DOMSelector.brand))
        .where(DOMSelector.id == selector_id)
    )
    selector = result.unique().scalar_one_or_none()
    
    if not selector:
        raise NotFoundException("DOMSelector", selector_id)
    
    return DOMSelectorEnhancedResponse(
        id=selector.id,
        brand_id=selector.brand_id,
        page_type=selector.page_type,
        selector=selector.selector,
        description=selector.description,
        status=selector.status,
        relationships=selector.relationships or {},
        created_at=selector.created_at,
        updated_at=selector.updated_at,
        brand_name=selector.brand.name if selector.brand else None
    )


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


@router.post("/bulk", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_selectors_bulk(
    selectors: List[DOMSelectorCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Create multiple selectors at once from DOM analysis.
    
    Accepts list of selector objects with relationships metadata.
    Skips duplicates (same brand_id + selector + page_type).
    Returns detailed response with created and skipped counts.
    """
    if not selectors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one selector is required"
        )
    
    # Validate all selectors before creating any
    brand_ids = set()
    for selector in selectors:
        if not selector.selector or not selector.selector.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Selector string cannot be empty for selector: {selector.description or 'Unknown'}"
            )
        brand_ids.add(selector.brand_id)
    
    # Verify all brands exist
    if brand_ids:
        brand_result = await db.execute(
            select(Brand).where(Brand.id.in_(brand_ids))
        )
        existing_brands = {brand.id for brand in brand_result.scalars().all()}
        missing_brands = brand_ids - existing_brands
        if missing_brands:
            raise NotFoundException("Brand", list(missing_brands)[0])
    
    # Check for duplicates before creating
    created_selectors = []
    skipped_count = 0
    
    for selector_data in selectors:
        # Check if selector already exists
        existing_result = await db.execute(
            select(DOMSelector).where(
                and_(
                    DOMSelector.brand_id == selector_data.brand_id,
                    DOMSelector.selector == selector_data.selector,
                    DOMSelector.page_type == selector_data.page_type
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            skipped_count += 1
            logger.info(
                f"Skipping duplicate selector: brand_id={selector_data.brand_id}, "
                f"selector={selector_data.selector}, page_type={selector_data.page_type}"
            )
            continue
        
        # Create new selector
        db_selector = DOMSelector(**selector_data.model_dump())
        db.add(db_selector)
        created_selectors.append(db_selector)
    
    # Commit all new selectors in one transaction
    try:
        await db.commit()
        
        # Refresh all created selectors to get their IDs
        for selector in created_selectors:
            await db.refresh(selector)
        
        logger.info(
            f"Bulk selector creation: {len(created_selectors)} created, {skipped_count} skipped"
        )
        
        # Build response
        response_data = {
            "created": len(created_selectors),
            "skipped": skipped_count,
            "selectors": [
                {
                    "id": s.id,
                    "brand_id": s.brand_id,
                    "page_type": s.page_type,
                    "selector": s.selector,
                    "description": s.description,
                    "status": s.status,
                    "relationships": s.relationships or {},
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "updated_at": s.updated_at.isoformat() if s.updated_at else None,
                }
                for s in created_selectors
            ]
        }
        
        return response_data
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating bulk selectors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create selectors: {str(e)}"
        )

