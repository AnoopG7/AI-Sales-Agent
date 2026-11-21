from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.core.exceptions import NotFoundException
from app.models.common import PaginatedResponse
from app.models.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ToggleFeaturedSchema,
)
from app.services.product_service import ProductService

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_products(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    team_size: int | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    data, total = await service.list_products(
        page, page_size, status, category,
        min_price, max_price, team_size, search,
    )
    return {
        "data": [ProductResponse.model_validate(p) for p in data],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.get_product(product_id)
    if not product:
        raise NotFoundException("Product not found")
    return product


@router.post("", status_code=201, response_model=ProductResponse)
async def create_product(
    body: ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    return await service.create_product(body.model_dump())


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.get_product(product_id)
    if not product:
        raise NotFoundException("Product not found")
    update_data = body.model_dump(exclude_none=True)
    return await service.update_product(product_id, update_data)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.get_product(product_id)
    if not product:
        raise NotFoundException("Product not found")
    await service.update_product(product_id, {"status": "archived"})


@router.patch("/{product_id}/featured", response_model=ProductResponse)
async def toggle_featured(
    product_id: str,
    body: ToggleFeaturedSchema,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.get_product(product_id)
    if not product:
        raise NotFoundException("Product not found")
    featured = body.featured if body.featured is not None else not product.featured
    return await service.update_product(product_id, {"featured": featured})
