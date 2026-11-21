import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.orm.product import Product

logger = structlog.get_logger()


def _apply_filters(
    stmt: Select,
    status: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    team_size: int | None = None,
    search: str | None = None,
) -> Select:
    """Shared filter logic for search and paginated listing."""
    if status:
        stmt = stmt.where(Product.status == status)
    if category:
        stmt = stmt.where(Product.category == category)
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)
    if team_size is not None:
        # The plan must accommodate the team: min_seats <= team_size <= max_seats (if capped)
        stmt = stmt.where(Product.min_seats <= team_size).where(
            or_(Product.max_seats.is_(None), Product.max_seats >= team_size)
        )
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
                Product.category.ilike(pattern),
            )
        )
    return stmt


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, product_id: str) -> Product | None:
        product = (await self.session.execute(
            select(Product).where(Product.id == product_id)
        )).scalar_one_or_none()
        if product:
            logger.debug("product_found_by_id", product_id=product_id)
        return product

    async def search(
        self,
        category: str | None = None,
        keyword: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        team_size: int | None = None,
        limit: int = 10,
    ) -> list[Product]:
        stmt = _apply_filters(
            select(Product), status="active", category=category,
            min_price=min_price, max_price=max_price, team_size=team_size, search=keyword,
        )
        stmt = stmt.order_by(Product.featured.desc(), Product.price.asc()).limit(limit)
        rows = (await self.session.execute(stmt)).scalars().all()
        logger.debug("product_search", count=len(rows), filters={
            "category": category, "keyword": keyword,
            "min_price": min_price, "max_price": max_price, "team_size": team_size,
        })
        return list(rows)

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        team_size: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Product], int]:
        filters = dict(
            status=status, category=category, min_price=min_price,
            max_price=max_price, team_size=team_size, search=search,
        )
        base = _apply_filters(select(Product), **filters)
        count_stmt = _apply_filters(select(func.count()).select_from(Product), **filters)

        offset = (page - 1) * page_size
        base = base.order_by(Product.created_at.desc()).offset(offset).limit(page_size)

        total = (await self.session.execute(count_stmt)).scalar() or 0
        rows = (await self.session.execute(base)).scalars().all()
        logger.debug("product_list_all", total=total, page=page)
        return list(rows), total

    async def create(self, data: dict) -> Product:
        product = Product(**data)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        logger.info("product_db_created", product_id=str(product.id), name=product.name)
        return product

    async def update(self, product_id: str, data: dict) -> Product | None:
        product = await self.find_by_id(product_id)
        if not product:
            logger.warning("product_update_not_found", product_id=product_id)
            return None
        for key, value in data.items():
            setattr(product, key, value)
        await self.session.commit()
        await self.session.refresh(product)
        logger.info("product_db_updated", product_id=product_id, fields=list(data.keys()))
        return product

    async def delete(self, product_id: str) -> bool:
        product = await self.find_by_id(product_id)
        if not product:
            logger.warning("product_delete_not_found", product_id=product_id)
            return False
        await self.session.delete(product)
        await self.session.commit()
        logger.info("product_db_deleted", product_id=product_id)
        return True
