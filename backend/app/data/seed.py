"""Seed the admin user on first startup."""
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session_factory
from app.core.security import hash_password
from app.config import settings
from app.models.user import User


async def seed_admin():
    """Create the default admin account if it doesn't exist."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(User).where(User.username == settings.admin_username)
        )
        existing = result.scalar_one_or_none()

        if existing is None:
            admin = User(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            await db.commit()
            print(f"[Seed] Admin user '{settings.admin_username}' created.")
        else:
            print(f"[Seed] Admin user '{settings.admin_username}' already exists.")
