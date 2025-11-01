"""User management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.core.auth import get_current_user_dependency, hash_password
from app.models.user import User
from app.models.enums import BrandRole
from app.schemas.user import UserCreate
from app.schemas.auth import UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Create a new user.
    
    Access control:
    - Super admins can create users for any brand with any role
    - Brand admins can create users for their brand only (brand_user or brand_admin roles)
    """
    
    # Check if user is admin
    if current_user.brand_role not in [BrandRole.SUPER_ADMIN.value, BrandRole.BRAND_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users"
        )
    
    # Check brand admin restrictions
    if current_user.brand_role == BrandRole.BRAND_ADMIN.value:
        # Can only create users for their brand
        if user_data.brand_id != current_user.brand_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only create users for your own brand"
            )
        # Cannot create super admins
        if user_data.brand_role == BrandRole.SUPER_ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create super admin users"
            )
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email.lower())
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create user
    new_user = User(
        email=user_data.email.lower(),
        password_hash=password_hash,
        name=user_data.name,
        role=user_data.role or "user",
        brand_id=user_data.brand_id,
        brand_role=user_data.brand_role
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        role=new_user.role,
        brand_id=new_user.brand_id,
        brand_role=new_user.brand_role
    )

