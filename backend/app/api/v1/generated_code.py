"""Generated Code API endpoints (read-only)."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.generated_code import GeneratedCode
from app.schemas.generated_code import GeneratedCodeResponse
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("/", response_model=List[GeneratedCodeResponse], status_code=status.HTTP_200_OK)
async def list_generated_code(
    skip: int = 0,
    limit: int = 100,
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    db: AsyncSession = Depends(get_db)
):
    """List all generated code with optional brand filter."""
    query = select(GeneratedCode)
    
    if brand_id:
        query = query.where(GeneratedCode.brand_id == brand_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    generated_codes = result.scalars().all()
    return generated_codes


@router.get("/{code_id}", response_model=GeneratedCodeResponse, status_code=status.HTTP_200_OK)
async def get_generated_code(
    code_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get generated code by ID."""
    result = await db.execute(select(GeneratedCode).where(GeneratedCode.id == code_id))
    generated_code = result.scalar_one_or_none()
    
    if not generated_code:
        raise NotFoundException("GeneratedCode", code_id)
    
    return generated_code

