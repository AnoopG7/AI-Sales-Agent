import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.product import Product
from app.repositories.product_repo import ProductRepository

logger = structlog.get_logger()


class ProductService:
    def __init__(self, session: AsyncSession):
        self.repo = ProductRepository(session)

    async def search_products(
        self,
        category: str | None = None,
        keyword: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        team_size: int | None = None,
        limit: int = 5,
    ) -> list[Product]:
        results = await self.repo.search(
            category=category,
            keyword=keyword,
            min_price=min_price,
            max_price=max_price,
            team_size=team_size,
            limit=limit,
        )
        logger.info("product_search", count=len(results))
        return results

    async def get_product(self, product_id: str) -> Product | None:
        return await self.repo.find_by_id(product_id)

    async def list_products(
        self, page: int = 1, page_size: int = 20,
        status: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        team_size: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Product], int]:
        return await self.repo.list_all(
            page, page_size, status, category,
            min_price, max_price, team_size, search,
        )

    async def create_product(self, data: dict) -> Product:
        product = await self.repo.create(data)
        logger.info("product_created", product_id=str(product.id), name=product.name)
        return product

    async def update_product(self, product_id: str, data: dict) -> Product | None:
        product = await self.repo.update(product_id, data)
        if product:
            logger.info("product_updated", product_id=product_id, fields=list(data.keys()))
        else:
            logger.warning("product_update_not_found", product_id=product_id)
        return product
