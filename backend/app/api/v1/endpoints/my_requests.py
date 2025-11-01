"""My Requests API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.api.deps import get_db
from app.models.generated_code import GeneratedCode
from app.models.user import User
from app.models.message import Message
from app.models.brand import Brand
from app.models.enums import CodeStatus
from app.schemas.generated_code import GeneratedCodeEnhancedResponse
from app.core.auth import get_current_user_dependency

router = APIRouter()


@router.get("/", response_model=List[GeneratedCodeEnhancedResponse], status_code=status.HTTP_200_OK)
async def get_my_requests(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get current user's generated code requests."""
    # Build query - only user's own requests
    query = (
        select(GeneratedCode)
        .options(
            joinedload(GeneratedCode.brand),
            joinedload(GeneratedCode.user),
            joinedload(GeneratedCode.reviewer)
        )
        .where(GeneratedCode.user_id == current_user.id)
    )
    
    # Apply status filter
    if status_filter:
        try:
            status_enum = CodeStatus(status_filter.lower())
            query = query.where(GeneratedCode.status == status_enum)
        except ValueError:
            raise status.HTTP_400_BAD_REQUEST
    
    # Order by created_at descending
    query = query.order_by(GeneratedCode.created_at.desc())
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    generated_codes = result.unique().scalars().all()
    
    # Build enhanced responses with conversation preview
    enhanced_codes = []
    for code in generated_codes:
        # Get conversation preview (first user message)
        conversation_preview = None
        if code.conversation_id:
            first_msg_query = (
                select(Message.content)
                .where(Message.conversation_id == code.conversation_id)
                .where(Message.role == 'user')
                .order_by(Message.created_at.asc())
                .limit(1)
            )
            first_msg_result = await db.execute(first_msg_query)
            first_msg = first_msg_result.scalar_one_or_none()
            if first_msg:
                conversation_preview = first_msg[:150]  # Truncate to 150 chars
        
        # Build enhanced response
        # Ensure brand name is properly loaded
        brand_name = None
        if code.brand:
            brand_name = code.brand.name
        elif code.brand_id:
            # Fallback: query brand directly if relationship not loaded
            brand_query = await db.execute(
                select(Brand).where(Brand.id == code.brand_id)
            )
            brand = brand_query.scalar_one_or_none()
            if brand:
                brand_name = brand.name
        
        enhanced_code = GeneratedCodeEnhancedResponse(
            id=code.id,
            brand_id=code.brand_id,
            conversation_id=str(code.conversation_id) if code.conversation_id else None,
            user_id=code.user_id,
            request_data=code.request_data,
            generated_code=code.generated_code,
            confidence_score=code.confidence_score,
            validation_status=code.validation_status,
            user_feedback=code.user_feedback,
            deployment_status=code.deployment_status,
            error_logs=code.error_logs,
            status=code.status,
            reviewer_id=code.reviewer_id,
            reviewed_at=code.reviewed_at,
            reviewer_notes=code.reviewer_notes,
            approved_at=code.approved_at,
            rejection_reason=code.rejection_reason,
            created_at=code.created_at,
            brand_name=brand_name,
            user_email=code.user.email if code.user else None,
            conversation_preview=conversation_preview,
            reviewer_email=code.reviewer.email if code.reviewer else None
        )
        enhanced_codes.append(enhanced_code)
    
    return enhanced_codes

