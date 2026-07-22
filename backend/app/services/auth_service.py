"""Authentication service layer."""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.auth import UserRegister, TokenResponse, UserResponse


async def register_user(db: AsyncSession, data: UserRegister) -> UserResponse:
    """Create a new user account."""
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise ValueError("用户名已存在")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role="user",
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


async def login_user(db: AsyncSession, username: str, password: str) -> TokenResponse:
    """Authenticate a user and return JWT tokens."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise ValueError("用户名或密码错误")

    if not user.is_active:
        raise ValueError("账户已被禁用")

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def change_user_password(
    db: AsyncSession, user_id: UUID, old_password: str, new_password: str
) -> None:
    """Change a user's password."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("用户不存在")

    if not verify_password(old_password, user.password_hash):
        raise ValueError("旧密码不正确")

    user.password_hash = hash_password(new_password)
