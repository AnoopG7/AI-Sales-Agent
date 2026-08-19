"""
Pydantic schemas for Admin users, Notifications, and Settings.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str | None = None
    role: str = "agent"


class AdminUserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str | None = None
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    lead_id: str | None = None
    type: str
    title: str
    body: str | None = None
    channel: str = "in_app"


class NotificationResponse(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID | None = None
    type: str
    title: str
    body: str | None = None
    channel: str
    read: bool
    extra_data: dict = {}
    created_at: datetime

    class Config:
        from_attributes = True


class SettingUpdate(BaseModel):
    value: dict


class SettingResponse(BaseModel):
    id: uuid.UUID
    key: str
    value: dict
    description: str | None = None
    updated_at: datetime

    class Config:
        from_attributes = True
