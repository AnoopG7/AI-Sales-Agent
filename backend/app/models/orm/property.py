import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.orm.base import Base


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None]
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    property_type: Mapped[str] = mapped_column(String(30), nullable=False)
    bedrooms: Mapped[int] = mapped_column(default=0)
    bathrooms: Mapped[int] = mapped_column(default=0)
    area_sqft: Mapped[float | None]
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]
    amenities: Mapped[list] = mapped_column(JSONB, default=list)
    images: Mapped[list] = mapped_column(JSONB, default=list)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="available")
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
