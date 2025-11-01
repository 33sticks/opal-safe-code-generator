"""Authentication utilities and dependencies."""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.user import User
from app.models.session import Session
from app.models.enums import UserRole, BrandRole


# Session expiration: 7 days
SESSION_EXPIRATION_DAYS = 7

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    import bcrypt
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    import bcrypt
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def generate_token() -> str:
    """Generate a cryptographically secure token."""
    return secrets.token_urlsafe(32)


async def create_session(
    db: AsyncSession,
    user_id: int,
    expires_in_days: int = SESSION_EXPIRATION_DAYS
) -> Session:
    """Create a new session for a user."""
    token = generate_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
    
    session = Session(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session


async def get_current_user(
    token: str,
    db: AsyncSession
) -> Optional[User]:
    """Validate token and return the associated user."""
    # Find the session by token
    result = await db.execute(
        select(Session).where(Session.token == token)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return None
    
    # Check if session is expired
    if session.expires_at < datetime.now(timezone.utc):
        # Delete expired session
        await db.delete(session)
        await db.commit()
        return None
    
    # Get the user
    result = await db.execute(
        select(User).where(User.id == session.user_id)
    )
    user = result.scalar_one_or_none()
    
    return user


async def get_current_user_dependency(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """FastAPI dependency to get the current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user = await get_current_user(token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def require_admin(
    current_user: User = Depends(get_current_user_dependency)
) -> User:
    """
    Dependency to require user to be super_admin or brand_admin.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: User = Depends(require_admin)
        ):
            ...
    """
    if current_user.brand_role not in [BrandRole.SUPER_ADMIN.value, BrandRole.BRAND_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires admin role"
        )
    return current_user


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: User = Depends(require_role("admin"))
        ):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_user_dependency)
    ) -> User:
        # Special handling for "admin" role - check brand_role instead
        if required_role == "admin":
            if current_user.brand_role not in [BrandRole.SUPER_ADMIN.value, BrandRole.BRAND_ADMIN.value]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This endpoint requires admin role"
                )
        elif current_user.role.value != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This endpoint requires {required_role} role"
            )
        return current_user
    
    return role_checker


def get_user_brand_access(user: User) -> list[int]:
    """
    Get list of brand IDs user can access.
    
    Returns:
        - Empty list for super_admin (access to all brands)
        - List with single brand_id for brand_admin and brand_user
    """
    if user.brand_role == BrandRole.SUPER_ADMIN.value:
        return []  # Empty list = access all
    elif user.brand_id:
        return [user.brand_id]
    else:
        return []  # No brand_id means no access (shouldn't happen, but safe)


def require_brand_access(brand_id: int):
    """
    Dependency factory to check if user can access specific brand.
    
    Usage:
        @router.get("/brands/{brand_id}/data")
        async def get_brand_data(
            brand_id: int,
            current_user: User = Depends(require_brand_access(brand_id))
        ):
            ...
    """
    def check_access(
        current_user: User = Depends(get_current_user_dependency)
    ) -> User:
        if current_user.brand_role == BrandRole.SUPER_ADMIN.value:
            return current_user
        if current_user.brand_id == brand_id:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this brand"
        )
    
    return check_access

