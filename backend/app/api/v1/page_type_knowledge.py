"""Page Type Knowledge API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.deps import get_db
from app.models.page_type_knowledge import PageTypeKnowledge
from app.models.brand import Brand
from app.models.user import User
from app.schemas.page_type_knowledge import PageTypeKnowledgeCreate, PageTypeKnowledgeUpdate, PageTypeKnowledgeResponse, PageTypeKnowledgeEnhancedResponse
from app.core.exceptions import NotFoundException
from app.core.auth import require_role, get_user_brand_access

router = APIRouter()


@router.get("/", response_model=List[PageTypeKnowledgeEnhancedResponse], status_code=status.HTTP_200_OK)
async def list_page_type_knowledge(
    skip: int = 0,
    limit: int = 100,
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """List page type knowledge with optional brand filter. Filtered by user's brand access."""
    query = select(PageTypeKnowledge).options(joinedload(PageTypeKnowledge.brand))
    
    # Filter by brand access first
    accessible_brands = get_user_brand_access(current_user)
    if accessible_brands:  # Not super admin - filter to their brand
        query = query.where(PageTypeKnowledge.brand_id.in_(accessible_brands))
    
    # Additional brand_id filter (for super admins)
    if brand_id:
        query = query.where(PageTypeKnowledge.brand_id == brand_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    knowledge_items = result.unique().scalars().all()
    
    # Build enhanced responses with brand_name
    enhanced_knowledge = []
    for knowledge in knowledge_items:
        enhanced_item = PageTypeKnowledgeEnhancedResponse(
            id=knowledge.id,
            brand_id=knowledge.brand_id,
            test_type=knowledge.test_type,
            template_code=knowledge.template_code,
            description=knowledge.description,
            version=knowledge.version,
            is_active=knowledge.is_active,
            created_at=knowledge.created_at,
            updated_at=knowledge.updated_at,
            brand_name=knowledge.brand.name if knowledge.brand else None
        )
        enhanced_knowledge.append(enhanced_item)
    
    return enhanced_knowledge


@router.post("/", response_model=PageTypeKnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_page_type_knowledge(
    knowledge: PageTypeKnowledgeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Create a new page type knowledge entry."""
    # Verify brand exists
    brand_result = await db.execute(select(Brand).where(Brand.id == knowledge.brand_id))
    brand = brand_result.scalar_one_or_none()
    if not brand:
        raise NotFoundException("Brand", knowledge.brand_id)
    
    db_knowledge = PageTypeKnowledge(**knowledge.model_dump())
    db.add(db_knowledge)
    await db.commit()
    await db.refresh(db_knowledge)
    return db_knowledge


@router.get("/{knowledge_id}", response_model=PageTypeKnowledgeEnhancedResponse, status_code=status.HTTP_200_OK)
async def get_page_type_knowledge(
    knowledge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Get page type knowledge by ID."""
    result = await db.execute(
        select(PageTypeKnowledge)
        .options(joinedload(PageTypeKnowledge.brand))
        .where(PageTypeKnowledge.id == knowledge_id)
    )
    knowledge = result.unique().scalar_one_or_none()
    
    if not knowledge:
        raise NotFoundException("Page Type Knowledge", knowledge_id)
    
    return PageTypeKnowledgeEnhancedResponse(
        id=knowledge.id,
        brand_id=knowledge.brand_id,
        test_type=knowledge.test_type,
        template_code=knowledge.template_code,
        description=knowledge.description,
        version=knowledge.version,
        is_active=knowledge.is_active,
        created_at=knowledge.created_at,
        updated_at=knowledge.updated_at,
        brand_name=knowledge.brand.name if knowledge.brand else None
    )


@router.put("/{knowledge_id}", response_model=PageTypeKnowledgeResponse, status_code=status.HTTP_200_OK)
async def update_page_type_knowledge(
    knowledge_id: int,
    knowledge_update: PageTypeKnowledgeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update page type knowledge."""
    result = await db.execute(select(PageTypeKnowledge).where(PageTypeKnowledge.id == knowledge_id))
    knowledge = result.scalar_one_or_none()
    
    if not knowledge:
        raise NotFoundException("Page Type Knowledge", knowledge_id)
    
    # Verify brand exists if brand_id is being updated
    if knowledge_update.brand_id and knowledge_update.brand_id != knowledge.brand_id:
        brand_result = await db.execute(select(Brand).where(Brand.id == knowledge_update.brand_id))
        brand = brand_result.scalar_one_or_none()
        if not brand:
            raise NotFoundException("Brand", knowledge_update.brand_id)
    
    # Update fields
    update_data = knowledge_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(knowledge, field, value)
    
    await db.commit()
    await db.refresh(knowledge)
    return knowledge


@router.delete("/{knowledge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page_type_knowledge(
    knowledge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Delete page type knowledge."""
    result = await db.execute(select(PageTypeKnowledge).where(PageTypeKnowledge.id == knowledge_id))
    knowledge = result.scalar_one_or_none()
    
    if not knowledge:
        raise NotFoundException("Page Type Knowledge", knowledge_id)
    
    await db.delete(knowledge)
    await db.commit()
    return None

