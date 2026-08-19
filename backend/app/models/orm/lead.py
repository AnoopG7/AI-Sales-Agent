from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.orm.base import Base

if TYPE_CHECKING:
    from app.models.orm.conversation import Conversation
    from app.models.orm.meeting import Meeting


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    whatsapp_phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str | None]
    email: Mapped[str | None]
    status: Mapped[str] = mapped_column(String(30), default="new")
    source: Mapped[str] = mapped_column(String(30), default="meta_ads")
    conversation_stage: Mapped[str | None] = mapped_column(String(40), default="greeting")
    budget_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    budget_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    property_type: Mapped[str | None]
    bedrooms_min: Mapped[int | None]
    location: Mapped[str | None]
    notes: Mapped[str | None]
    assigned_to: Mapped[str | None]
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    conversations: Mapped[list[Conversation]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    meetings: Mapped[list[Meeting]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
