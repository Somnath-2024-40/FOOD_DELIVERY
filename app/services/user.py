from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Tuple, List
from fastapi import HTTPException, status

from models.user import User, UserRole
from schemas.user import UserCreate, UserAdminUpdate, UserUpdate
from core.security import get_password_hash, verify_password

MAX_PAGE_SIZE = 100

async def _clamp_page_size(page_size: int) -> int:
    return max(1, min(page_size, MAX_PAGE_SIZE))

async def _count(db: AsyncSession, base_query) -> int:
    count_query = select(func.count()).select_from(base_query.subquery())
    result = await db.execute(count_query)
    return result.scalar()

async def _apply_hashed_password(data: dict) -> dict:
    if "password" in data:
        data["hashed_password"] = get_password_hash(data.pop("password"))  # not async
    return data

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()  # ← fixed: added ()

async def get_user_or_404(db: AsyncSession, user_id: int) -> User:
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"             # ← fixed: was "deatil"
        )
    return user

async def _get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()  # ← fixed: added ()

async def get_users_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    user_role: Optional[UserRole] = None,
    active_only: bool = False
) -> Tuple[List[User], int]:

    page_size = await _clamp_page_size(page_size)
    base = select(User).order_by(User.created_at.desc())
    if user_role is not None:
        base = base.where(User.role == user_role)
    if active_only:
        base = base.where(User.is_active.is_(True))  # ← fixed: was "is_axctive"

    total = await _count(db, base)
    result = await db.execute(base.offset((page - 1) * page_size).limit(page_size))
    return result.scalars().all(), total

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    existing = await _get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    data = user.dict(exclude={"password"})  # ← fixed: exclude takes a set, not a string
    hashed_password = get_password_hash(user.password)  # ← fixed: was get_hashed_password
    new_user = User(**data, hashed_password=hashed_password)

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception:
        await db.rollback()
        raise

    return new_user

async def update_user_field(db: AsyncSession, user_in: User, update_data: dict) -> User:
    update_data = await _apply_hashed_password(update_data)
    for field, value in update_data.items():
        setattr(user_in, field, value)
    try:
        await db.commit()
        await db.refresh(user_in)
    except Exception:
        await db.rollback()
        raise
    return user_in

async def update_user(db: AsyncSession, user: User, user_in: UserUpdate) -> User:
    return await update_user_field(db, user, user_in.dict(exclude_unset=True))

async def admin_update_user(
    db: AsyncSession, user: User, user_in: UserAdminUpdate, role: UserRole
) -> User:
    if user.role != role:
        raise HTTPException(                    # ← fixed: was "HTTPExcpeption"
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )
    return await update_user_field(db, user, user_in.dict(exclude_unset=True))

async def delete_user(db: AsyncSession, user: User) -> None:
    user.is_active = False
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await _get_user_by_email(db, email.strip())
    if not user:
        return None
    if user.is_active is False:
        return None
    if not verify_password(password.strip(), user.hashed_password):  
        return None
    return user