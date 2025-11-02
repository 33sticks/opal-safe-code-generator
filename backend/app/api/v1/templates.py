"""Template API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.deps import get_db
from app.models.template import Template
from app.models.brand import Brand
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse, TemplateEnhancedResponse
from app.core.exceptions import NotFoundException
from app.core.auth import require_role, get_user_brand_access

router = APIRouter()


@router.get("/", response_model=List[TemplateEnhancedResponse], status_code=status.HTTP_200_OK)
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """List templates with optional brand filter. Filtered by user's brand access."""
    query = select(Template).options(joinedload(Template.brand))
    
    # Filter by brand access first
    accessible_brands = get_user_brand_access(current_user)
    if accessible_brands:  # Not super admin - filter to their brand
        query = query.where(Template.brand_id.in_(accessible_brands))
    
    # Additional brand_id filter (for super admins)
    if brand_id:
        query = query.where(Template.brand_id == brand_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    templates = result.unique().scalars().all()
    
    # Build enhanced responses with brand_name
    enhanced_templates = []
    for template in templates:
        enhanced_template = TemplateEnhancedResponse(
            id=template.id,
            brand_id=template.brand_id,
            test_type=template.test_type,
            template_code=template.template_code,
            description=template.description,
            version=template.version,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
            brand_name=template.brand.name if template.brand else None
        )
        enhanced_templates.append(enhanced_template)
    
    return enhanced_templates


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Create a new template."""
    # Verify brand exists
    brand_result = await db.execute(select(Brand).where(Brand.id == template.brand_id))
    brand = brand_result.scalar_one_or_none()
    if not brand:
        raise NotFoundException("Brand", template.brand_id)
    
    db_template = Template(**template.model_dump())
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template


@router.get("/{template_id}", response_model=TemplateEnhancedResponse, status_code=status.HTTP_200_OK)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Get a template by ID."""
    result = await db.execute(
        select(Template)
        .options(joinedload(Template.brand))
        .where(Template.id == template_id)
    )
    template = result.unique().scalar_one_or_none()
    
    if not template:
        raise NotFoundException("Template", template_id)
    
    return TemplateEnhancedResponse(
        id=template.id,
        brand_id=template.brand_id,
        test_type=template.test_type,
        template_code=template.template_code,
        description=template.description,
        version=template.version,
        is_active=template.is_active,
        created_at=template.created_at,
        updated_at=template.updated_at,
        brand_name=template.brand.name if template.brand else None
    )


@router.put("/{template_id}", response_model=TemplateResponse, status_code=status.HTTP_200_OK)
async def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update a template."""
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    
    if not template:
        raise NotFoundException("Template", template_id)
    
    # Verify brand exists if brand_id is being updated
    if template_update.brand_id and template_update.brand_id != template.brand_id:
        brand_result = await db.execute(select(Brand).where(Brand.id == template_update.brand_id))
        brand = brand_result.scalar_one_or_none()
        if not brand:
            raise NotFoundException("Brand", template_update.brand_id)
    
    # Update fields
    update_data = template_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Delete a template."""
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    
    if not template:
        raise NotFoundException("Template", template_id)
    
    await db.delete(template)
    await db.commit()
    return None

