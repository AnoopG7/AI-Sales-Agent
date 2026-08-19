import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.property import Property
from app.repositories.property_repo import PropertyRepository

logger = structlog.get_logger()


class PropertyService:
    def __init__(self, session: AsyncSession):
        self.repo = PropertyRepository(session)

    async def search_properties(
        self,
        property_type: str | None = None,
        location: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        bedrooms: int | None = None,
        limit: int = 5,
    ) -> list[Property]:
        results = await self.repo.search(
            property_type=property_type,
            location=location,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            limit=limit,
        )
        logger.info("property_search", count=len(results))
        return results

    async def get_property(self, property_id: str) -> Property | None:
        return await self.repo.find_by_id(property_id)

    async def list_properties(
        self, page: int = 1, page_size: int = 20,
        status: str | None = None,
        property_type: str | None = None,
        location: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        bedrooms: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Property], int]:
        return await self.repo.list_all(
            page, page_size, status, property_type, location,
            min_price, max_price, bedrooms, search,
        )

    async def create_property(self, data: dict) -> Property:
        prop = await self.repo.create(data)
        logger.info("property_created", property_id=str(prop.id), title=prop.title)
        return prop

    async def update_property(self, property_id: str, data: dict) -> Property | None:
        prop = await self.repo.update(property_id, data)
        if prop:
            logger.info("property_updated", property_id=property_id, fields=list(data.keys()))
        else:
            logger.warning("property_update_not_found", property_id=property_id)
        return prop
