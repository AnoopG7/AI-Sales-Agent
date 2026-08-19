"""
API dependencies — DB session, auth, role checks.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.models.orm.admin_user import AdminUser


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException()

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedException()

    stmt = select(AdminUser).where(AdminUser.id == payload["sub"])
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise UnauthorizedException("User not found")
    return user


async def require_admin(
    current_user: AdminUser = Depends(get_current_user),
) -> AdminUser:
    if current_user.role != "admin":
        raise ForbiddenException("Admin access required")
    return current_user
