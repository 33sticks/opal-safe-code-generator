"""Notification API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse, UnreadCountResponse
from app.services.notification_service import NotificationService
from app.core.auth import get_current_user_dependency

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse], status_code=status.HTTP_200_OK)
async def get_notifications(
    unread_only: bool = Query(False, description="Filter to unread notifications only"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of notifications to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get current user's notifications."""
    notifications = await NotificationService.get_user_notifications(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit
    )
    return notifications


@router.post("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Mark a notification as read."""
    success = await NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or you don't have permission to access it"
        )
    
    return {"success": True}


@router.get("/unread-count", response_model=UnreadCountResponse, status_code=status.HTTP_200_OK)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get count of unread notifications for current user."""
    count = await NotificationService.get_unread_count(db=db, user_id=current_user.id)
    return UnreadCountResponse(count=count)



