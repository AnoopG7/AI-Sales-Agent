from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.core.exceptions import NotFoundException
from app.models.common import PaginatedResponse
from app.models.property import (
    PropertyCreate,
    PropertyResponse,
    PropertyUpdate,
    ToggleFeaturedSchema,
)
from app.services.property_service import PropertyService

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_properties(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status: str | None = None,
    property_type: str | None = None,
    location: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    service = PropertyService(db)
    data, total = await service.list_properties(
        page, page_size, status, property_type, location,
        min_price, max_price, bedrooms, search,
    )
    return {
        "data": [PropertyResponse.model_validate(p) for p in data],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = PropertyService(db)
    prop = await service.get_property(property_id)
    if not prop:
        raise NotFoundException("Property not found")
    return prop


@router.post("", status_code=201, response_model=PropertyResponse)
async def create_property(
    body: PropertyCreate,
    db: AsyncSession = Depends(get_db),
):
    service = PropertyService(db)
    return await service.create_property(body.model_dump())


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: str,
    body: PropertyUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = PropertyService(db)
    prop = await service.get_property(property_id)
    if not prop:
        raise NotFoundException("Property not found")
    update_data = body.model_dump(exclude_none=True)
    return await service.update_property(property_id, update_data)


@router.delete("/{property_id}", status_code=204)
async def delete_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = PropertyService(db)
    prop = await service.get_property(property_id)
    if not prop:
        raise NotFoundException("Property not found")
    await service.update_property(property_id, {"status": "archived"})


@router.patch("/{property_id}/featured", response_model=PropertyResponse)
async def toggle_featured(
    property_id: str,
    body: ToggleFeaturedSchema,
    db: AsyncSession = Depends(get_db),
):
    service = PropertyService(db)
    prop = await service.get_property(property_id)
    if not prop:
        raise NotFoundException("Property not found")
    featured = body.featured if body.featured is not None else not prop.featured
    return await service.update_property(property_id, {"featured": featured})
