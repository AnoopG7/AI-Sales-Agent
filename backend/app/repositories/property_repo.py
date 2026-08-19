import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.property import Property

logger = structlog.get_logger()


class PropertyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, property_id: str) -> Property | None:
        prop = (await self.session.execute(
            select(Property).where(Property.id == property_id)
        )).scalar_one_or_none()
        if prop:
            logger.debug("property_found_by_id", property_id=property_id)
        return prop

    async def search(
        self,
        property_type: str | None = None,
        location: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        bedrooms: int | None = None,
        limit: int = 10,
    ) -> list[Property]:
        stmt = select(Property).where(Property.status == "available")

        if property_type:
            stmt = stmt.where(Property.property_type == property_type)
        if location:
            stmt = stmt.where(Property.location.ilike(f"%{location}%"))
        if min_price is not None:
            stmt = stmt.where(Property.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Property.price <= max_price)
        if bedrooms is not None:
            stmt = stmt.where(Property.bedrooms >= bedrooms)

        stmt = stmt.order_by(Property.featured.desc()).limit(limit)
        rows = (await self.session.execute(stmt)).scalars().all()
        logger.debug("property_search", count=len(rows), filters={
            "type": property_type, "location": location,
            "min_price": min_price, "max_price": max_price, "bedrooms": bedrooms,
        })
        return list(rows)

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        property_type: str | None = None,
        location: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        bedrooms: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Property], int]:
        base = select(Property)
        count_base = select(func.count()).select_from(Property)

        if status:
            base = base.where(Property.status == status)
            count_base = count_base.where(Property.status == status)
        if property_type:
            base = base.where(Property.property_type == property_type)
            count_base = count_base.where(Property.property_type == property_type)
        if location:
            base = base.where(Property.location.ilike(f"%{location}%"))
            count_base = count_base.where(Property.location.ilike(f"%{location}%"))
        if min_price is not None:
            base = base.where(Property.price >= min_price)
            count_base = count_base.where(Property.price >= min_price)
        if max_price is not None:
            base = base.where(Property.price <= max_price)
            count_base = count_base.where(Property.price <= max_price)
        if bedrooms is not None:
            base = base.where(Property.bedrooms >= bedrooms)
            count_base = count_base.where(Property.bedrooms >= bedrooms)
        if search:
            pattern = f"%{search}%"
            base = base.where(
                or_(
                    Property.title.ilike(pattern),
                    Property.location.ilike(pattern),
                    Property.description.ilike(pattern),
                )
            )
            count_base = count_base.where(
                or_(
                    Property.title.ilike(pattern),
                    Property.location.ilike(pattern),
                    Property.description.ilike(pattern),
                )
            )

        offset = (page - 1) * page_size
        base = base.order_by(Property.created_at.desc()).offset(offset).limit(page_size)

        total = (await self.session.execute(count_base)).scalar() or 0
        rows = (await self.session.execute(base)).scalars().all()
        logger.debug("property_list_all", total=total, page=page)
        return list(rows), total

    async def create(self, data: dict) -> Property:
        prop = Property(**data)
        self.session.add(prop)
        await self.session.commit()
        await self.session.refresh(prop)
        logger.info("property_db_created", property_id=str(prop.id), title=prop.title)
        return prop

    async def update(self, property_id: str, data: dict) -> Property | None:
        prop = await self.find_by_id(property_id)
        if not prop:
            logger.warning("property_update_not_found", property_id=property_id)
            return None
        for key, value in data.items():
            setattr(prop, key, value)
        await self.session.commit()
        await self.session.refresh(prop)
        logger.info("property_db_updated", property_id=property_id, fields=list(data.keys()))
        return prop

    async def delete(self, property_id: str) -> bool:
        prop = await self.find_by_id(property_id)
        if not prop:
            logger.warning("property_delete_not_found", property_id=property_id)
            return False
        await self.session.delete(prop)
        await self.session.commit()
        logger.info("property_db_deleted", property_id=property_id)
        return True
