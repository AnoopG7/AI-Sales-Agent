from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.admin_user import AdminUser


class AdminUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_email(self, email: str) -> AdminUser | None:
        stmt = select(AdminUser).where(AdminUser.email == email.lower().strip())
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def find_by_id(self, user_id: str) -> AdminUser | None:
        stmt = select(AdminUser).where(AdminUser.id == user_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create(self, data: dict) -> AdminUser:
        user = AdminUser(**data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_password(self, user_id: str, password_hash: str) -> AdminUser | None:
        user = await self.find_by_id(user_id)
        if not user:
            return None
        user.password_hash = password_hash
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user_id: str, data: dict) -> AdminUser | None:
        user = await self.find_by_id(user_id)
        if not user:
            return None
        for key, value in data.items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user
