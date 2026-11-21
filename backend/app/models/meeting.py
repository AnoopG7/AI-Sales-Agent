"""
Pydantic schemas for Meeting and Conversation data.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MeetingCreate(BaseModel):
    lead_id: str
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    timezone: str = "UTC"
    notes: str | None = None


class MeetingUpdate(BaseModel):
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    status: str | None = None
    notes: str | None = None


class MeetingResponse(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    scheduled_at: datetime
    duration_minutes: int
    timezone: str
    google_event_id: str | None = None
    meet_link: str | None = None
    status: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationMessage(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    role: str
    content: str
    message_type: str = "text"
    whatsapp_message_id: str | None = None
    extra_data: dict = {}
    created_at: datetime

    class Config:
        from_attributes = True
