"""Authentication API endpoints."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db
from app.models.user import User
from app.models.session import Session
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, UserResponse
from app.core.auth import (
    get_current_user_dependency,
    create_session,
    require_role,
    verify_password,
    hash_password,
)
from app.core.exceptions import ConflictException

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password, returns session token."""
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == login_data.email.lower())
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not user.verify_password(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create session
    session = await create_session(db, user.id)
    
    # Return response
    return LoginResponse(
        token=session.token,
        expires_at=session.expires_at.isoformat(),
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            brand_id=user.brand_id
        )
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Logout by invalidating the current session token."""
    # Note: We need the token to delete the session
    # Since we already validated it in get_current_user_dependency,
    # we can get it from the Authorization header via security dependency
    
    # For now, we'll delete all sessions for this user
    # In a production system, you'd want to track the specific token
    # and only delete that one. This is simpler for this implementation.
    
    result = await db.execute(
        select(Session).where(Session.user_id == current_user.id)
    )
    sessions = result.scalars().all()
    
    for session in sessions:
        await db.delete(session)
    
    await db.commit()
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_dependency)
):
    """Get current authenticated user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        brand_id=current_user.brand_id
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Register a new user (admin only)."""
    # Check if user with this email already exists
    result = await db.execute(
        select(User).where(User.email == register_data.email.lower())
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise ConflictException(f"User with email '{register_data.email}' already exists")
    
    # Validate brand_id if provided
    if register_data.brand_id:
        from app.models.brand import Brand
        brand_result = await db.execute(
            select(Brand).where(Brand.id == register_data.brand_id)
        )
        brand = brand_result.scalar_one_or_none()
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with id {register_data.brand_id} not found"
            )
    
    # Create new user
    new_user = User(
        email=register_data.email.lower(),
        name=register_data.name,
        role=register_data.role,
        brand_id=register_data.brand_id
    )
    new_user.set_password(register_data.password)
    
    db.add(new_user)
    
    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise ConflictException(f"User with email '{register_data.email}' already exists")
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        role=new_user.role,
        brand_id=new_user.brand_id
    )

