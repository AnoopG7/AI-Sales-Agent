"""
Pydantic schemas for Property data.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PropertyBase(BaseModel):
    title: str = Field(..., min_length=5)
    description: str | None = None
    price: Decimal = Field(..., gt=0, decimal_places=2, max_digits=12)
    property_type: str
    bedrooms: int = 0
    bathrooms: int = 0
    area_sqft: float | None = None
    location: str
    latitude: float | None = None
    longitude: float | None = None
    amenities: list[str] = []
    featured: bool = False


class PropertyCreate(PropertyBase):
    status: str = "available"


class PropertyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: Decimal | None = Field(None, gt=0, decimal_places=2, max_digits=12)
    property_type: str | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    area_sqft: float | None = None
    location: str | None = None
    amenities: list[str] | None = None
    status: str | None = None
    featured: bool | None = None


class ToggleFeaturedSchema(BaseModel):
    featured: bool | None = None


class PropertyResponse(PropertyBase):
    id: uuid.UUID
    status: str
    images: list[dict] = []
    extra_data: dict = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
