"""Code Rule API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.code_rule import CodeRule
from app.models.brand import Brand
from app.models.user import User
from app.schemas.code_rule import CodeRuleCreate, CodeRuleUpdate, CodeRuleResponse
from app.core.exceptions import NotFoundException
from app.core.auth import require_role

router = APIRouter()


@router.get("/", response_model=List[CodeRuleResponse], status_code=status.HTTP_200_OK)
async def list_rules(
    skip: int = 0,
    limit: int = 100,
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """List all code rules with optional brand filter."""
    query = select(CodeRule)
    
    if brand_id:
        query = query.where(CodeRule.brand_id == brand_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    rules = result.scalars().all()
    return rules


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


@router.get("/{rule_id}", response_model=CodeRuleResponse, status_code=status.HTTP_200_OK)
async def get_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Get a code rule by ID."""
    result = await db.execute(select(CodeRule).where(CodeRule.id == rule_id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise NotFoundException("CodeRule", rule_id)
    
    return rule


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

