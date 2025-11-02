"""Code Rule API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.deps import get_db
from app.models.code_rule import CodeRule
from app.models.brand import Brand
from app.models.user import User
from app.schemas.code_rule import CodeRuleCreate, CodeRuleUpdate, CodeRuleResponse, CodeRuleEnhancedResponse
from app.core.exceptions import NotFoundException
from app.core.auth import require_role, get_user_brand_access

router = APIRouter()


@router.get("/", response_model=List[CodeRuleEnhancedResponse], status_code=status.HTTP_200_OK)
async def list_rules(
    skip: int = 0,
    limit: int = 100,
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """List code rules with optional brand filter. Filtered by user's brand access."""
    query = select(CodeRule).options(joinedload(CodeRule.brand))
    
    # Filter by brand access first
    accessible_brands = get_user_brand_access(current_user)
    if accessible_brands:  # Not super admin - filter to their brand
        query = query.where(CodeRule.brand_id.in_(accessible_brands))
    
    # Additional brand_id filter (for super admins)
    if brand_id:
        query = query.where(CodeRule.brand_id == brand_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    rules = result.unique().scalars().all()
    
    # Build enhanced responses with brand_name
    enhanced_rules = []
    for rule in rules:
        enhanced_rule = CodeRuleEnhancedResponse(
            id=rule.id,
            brand_id=rule.brand_id,
            rule_type=rule.rule_type,
            rule_content=rule.rule_content,
            priority=rule.priority,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            brand_name=rule.brand.name if rule.brand else None
        )
        enhanced_rules.append(enhanced_rule)
    
    return enhanced_rules


@router.post("/", response_model=CodeRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule: CodeRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Create a new code rule."""
    # Verify brand exists
    brand_result = await db.execute(select(Brand).where(Brand.id == rule.brand_id))
    brand = brand_result.scalar_one_or_none()
    if not brand:
        raise NotFoundException("Brand", rule.brand_id)
    
    db_rule = CodeRule(**rule.model_dump())
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule


@router.get("/{rule_id}", response_model=CodeRuleEnhancedResponse, status_code=status.HTTP_200_OK)
async def get_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Get a code rule by ID."""
    result = await db.execute(
        select(CodeRule)
        .options(joinedload(CodeRule.brand))
        .where(CodeRule.id == rule_id)
    )
    rule = result.unique().scalar_one_or_none()
    
    if not rule:
        raise NotFoundException("CodeRule", rule_id)
    
    return CodeRuleEnhancedResponse(
        id=rule.id,
        brand_id=rule.brand_id,
        rule_type=rule.rule_type,
        rule_content=rule.rule_content,
        priority=rule.priority,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
        brand_name=rule.brand.name if rule.brand else None
    )


@router.put("/{rule_id}", response_model=CodeRuleResponse, status_code=status.HTTP_200_OK)
async def update_rule(
    rule_id: int,
    rule_update: CodeRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update a code rule."""
    result = await db.execute(select(CodeRule).where(CodeRule.id == rule_id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise NotFoundException("CodeRule", rule_id)
    
    # Verify brand exists if brand_id is being updated
    if rule_update.brand_id and rule_update.brand_id != rule.brand_id:
        brand_result = await db.execute(select(Brand).where(Brand.id == rule_update.brand_id))
        brand = brand_result.scalar_one_or_none()
        if not brand:
            raise NotFoundException("Brand", rule_update.brand_id)
    
    # Update fields
    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Delete a code rule."""
    result = await db.execute(select(CodeRule).where(CodeRule.id == rule_id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise NotFoundException("CodeRule", rule_id)
    
    await db.delete(rule)
    await db.commit()
    return None

