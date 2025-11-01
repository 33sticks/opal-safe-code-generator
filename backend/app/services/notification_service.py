"""Notification service for managing user notifications."""
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.notification import Notification
from app.models.enums import NotificationType


class NotificationService:
    """Service for managing notifications."""
    
    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: int,
        generated_code_id: Optional[int],
        notification_type: str,
        title: str,
        message: str
    ) -> Notification:
        """Create a new notification for a user."""
        notification = Notification(
            user_id=user_id,
            generated_code_id=generated_code_id,
            type=notification_type,
            title=title,
            message=message,
            read=False
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        return notification
    
    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: int,
        unread_only: bool = False,
        limit: int = 20
    ) -> List[Notification]:
        """Get notifications for a user, optionally filtered by read status."""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.read == False)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        notification_id: int,
        user_id: int
    ) -> bool:
        """Mark a notification as read. Returns True if successful, False if not found or not owned by user."""
        result = await db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        notification.read = True
        notification.read_at = datetime.now(timezone.utc)
        
        await db.commit()
        return True
    
    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        result = await db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.read == False
            )
        )
        return result.scalar_one() or 0

