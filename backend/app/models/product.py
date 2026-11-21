"""
Pydantic schemas for Product (sales catalog) data.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2)
    description: str | None = None
    category: str
    price: Decimal = Field(..., ge=0, decimal_places=2, max_digits=12)
    billing_period: str = "monthly"
    min_seats: int = Field(1, ge=1)
    max_seats: int | None = Field(None, ge=1)
    features: list[str] = []
    featured: bool = False


class ProductCreate(ProductBase):
    status: str = "active"


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    price: Decimal | None = Field(None, ge=0, decimal_places=2, max_digits=12)
    billing_period: str | None = None
    min_seats: int | None = Field(None, ge=1)
    max_seats: int | None = Field(None, ge=1)
    features: list[str] | None = None
    status: str | None = None
    featured: bool | None = None


class ToggleFeaturedSchema(BaseModel):
    featured: bool | None = None


class ProductResponse(ProductBase):
    id: uuid.UUID
    status: str
    extra_data: dict = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
