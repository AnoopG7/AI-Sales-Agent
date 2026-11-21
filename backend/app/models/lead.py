"""
Pydantic schemas for Lead data.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class LeadBase(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    budget_min: Decimal | None = Field(None, decimal_places=2, max_digits=12)
    budget_max: Decimal | None = Field(None, decimal_places=2, max_digits=12)
    company: str | None = None
    team_size: int | None = Field(None, ge=1)
    product_interest: str | None = None
    notes: str | None = None


class LeadCreate(LeadBase):
    whatsapp_phone: str = Field(..., min_length=10)
    source: str = "meta_ads"


class LeadUpdate(LeadBase):
    status: str | None = None
    assigned_to: str | None = None
    conversation_stage: str | None = None


class NoteCreate(BaseModel):
    note: str = Field(..., min_length=1)


class LeadResponse(LeadBase):
    id: uuid.UUID
    whatsapp_phone: str
    status: str
    source: str
    assigned_to: str | None = None
    conversation_stage: str | None = None
    extra_data: dict = {}
    last_contacted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
