"""Generated Code API endpoints (read-only)."""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from sqlalchemy.orm import selectinload, joinedload

from app.api.deps import get_db
from app.models.generated_code import GeneratedCode
from app.models.user import User
from app.models.brand import Brand
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.enums import CodeStatus
from app.schemas.generated_code import (
    GeneratedCodeResponse,
    GeneratedCodeEnhancedResponse,
    CodeReviewRequest,
    CodeReviewResponse,
    ConversationForCodeResponse
)
from app.core.exceptions import NotFoundException
from app.core.auth import require_role

router = APIRouter()


@router.get("/", response_model=List[GeneratedCodeEnhancedResponse], status_code=status.HTTP_200_OK)
async def list_generated_code(
    status: Optional[str] = Query(None, description="Filter by status"),
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """List all generated code with optional filters and enhanced response."""
    # Build query with joins
    query = (
        select(GeneratedCode)
        .options(
            joinedload(GeneratedCode.brand),
            joinedload(GeneratedCode.user),
            joinedload(GeneratedCode.reviewer)
        )
    )
    
    # Apply filters
    if status:
        try:
            status_enum = CodeStatus(status.lower())
            query = query.where(GeneratedCode.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}. Must be one of: {', '.join([s.value for s in CodeStatus])}"
            )
    
    if brand_id:
        query = query.where(GeneratedCode.brand_id == brand_id)
    
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
            brand_name=code.brand.name if code.brand else None,
            user_email=code.user.email if code.user else None,
            conversation_preview=conversation_preview,
            reviewer_email=code.reviewer.email if code.reviewer else None
        )
        enhanced_codes.append(enhanced_code)
    
    return enhanced_codes


@router.get("/{code_id}", response_model=GeneratedCodeResponse, status_code=status.HTTP_200_OK)
async def get_generated_code(
    code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Get generated code by ID."""
    result = await db.execute(select(GeneratedCode).where(GeneratedCode.id == code_id))
    generated_code = result.scalar_one_or_none()
    
    if not generated_code:
        raise NotFoundException("GeneratedCode", code_id)
    
    return generated_code


@router.post("/{code_id}/review", response_model=CodeReviewResponse, status_code=status.HTTP_200_OK)
async def review_generated_code(
    code_id: int,
    review_request: CodeReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Review generated code (approve or reject)."""
    # Get the generated code
    result = await db.execute(select(GeneratedCode).where(GeneratedCode.id == code_id))
    generated_code = result.scalar_one_or_none()
    
    if not generated_code:
        raise NotFoundException("GeneratedCode", code_id)
    
    # Update review fields
    generated_code.reviewer_id = current_user.id
    generated_code.reviewed_at = datetime.now(timezone.utc)
    generated_code.reviewer_notes = review_request.reviewer_notes
    
    if review_request.status == "approved":
        generated_code.status = CodeStatus.APPROVED
        generated_code.approved_at = datetime.now(timezone.utc)
        generated_code.rejection_reason = None
    elif review_request.status == "rejected":
        generated_code.status = CodeStatus.REJECTED
        generated_code.rejection_reason = review_request.reviewer_notes
        generated_code.approved_at = None
    
    await db.commit()
    await db.refresh(generated_code)
    
    # Load reviewer relationship
    await db.refresh(generated_code, ["reviewer"])
    
    # Build response
    reviewer_info = None
    if generated_code.reviewer:
        reviewer_info = {
            "id": generated_code.reviewer.id,
            "email": generated_code.reviewer.email
        }
    
    return CodeReviewResponse(
        id=generated_code.id,
        status=generated_code.status,
        reviewed_at=generated_code.reviewed_at,
        reviewer=reviewer_info
    )


@router.get("/{code_id}/conversation", response_model=ConversationForCodeResponse, status_code=status.HTTP_200_OK)
async def get_code_conversation(
    code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Get conversation history for a generated code."""
    # Get the generated code
    result = await db.execute(select(GeneratedCode).where(GeneratedCode.id == code_id))
    generated_code = result.scalar_one_or_none()
    
    if not generated_code:
        raise NotFoundException("GeneratedCode", code_id)
    
    if not generated_code.conversation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No conversation associated with this code (legacy code)"
        )
    
    # Get conversation
    conv_result = await db.execute(
        select(Conversation)
        .options(joinedload(Conversation.user), joinedload(Conversation.brand))
        .where(Conversation.id == generated_code.conversation_id)
    )
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get all messages
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()
    
    # Build message responses
    message_responses = [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        }
        for msg in messages
    ]
    
    # Build user info
    user_info = {
        "id": conversation.user.id,
        "email": conversation.user.email,
        "name": conversation.user.name
    }
    
    # Build brand info
    brand_info = None
    if conversation.brand:
        brand_info = {
            "id": conversation.brand.id,
            "name": conversation.brand.name,
            "domain": conversation.brand.domain
        }
    
    return ConversationForCodeResponse(
        conversation_id=str(conversation.id),
        messages=message_responses,
        user=user_info,
        brand=brand_info
    )


@router.delete("/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_generated_code(
    code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Delete generated code."""
    result = await db.execute(select(GeneratedCode).where(GeneratedCode.id == code_id))
    generated_code = result.scalar_one_or_none()
    
    if not generated_code:
        raise NotFoundException("GeneratedCode", code_id)
    
    await db.execute(delete(GeneratedCode).where(GeneratedCode.id == code_id))
    await db.commit()
    
    return None

