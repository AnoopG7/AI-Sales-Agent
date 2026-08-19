from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.core.exceptions import NotFoundException
from app.models.common import PaginatedResponse
from app.models.meeting import MeetingCreate, MeetingResponse, MeetingUpdate
from app.services.meeting_service import MeetingService

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_meetings(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    data, total = await service.list_meetings(page, page_size, status)
    return {
        "data": [MeetingResponse.model_validate(m) for m in data],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/upcoming", response_model=list[MeetingResponse])
async def get_upcoming_meetings(
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    return await service.get_upcoming_meetings()


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    meeting = await service.get_meeting(meeting_id)
    if not meeting:
        raise NotFoundException("Meeting not found")
    return meeting


@router.post("", status_code=201, response_model=MeetingResponse)
async def create_meeting(
    body: MeetingCreate,
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    return await service.schedule_meeting(
        lead_id=body.lead_id,
        scheduled_at=body.scheduled_at.isoformat(),
        duration=body.duration_minutes,
        timezone=body.timezone,
        notes=body.notes,
    )


@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: str,
    body: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    meeting = await service.get_meeting(meeting_id)
    if not meeting:
        raise NotFoundException("Meeting not found")
    update_data = body.model_dump(exclude_none=True)
    return await service.update_meeting(meeting_id, update_data)


@router.delete("/{meeting_id}", status_code=204)
async def cancel_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    meeting = await service.get_meeting(meeting_id)
    if not meeting:
        raise NotFoundException("Meeting not found")
    await service.update_meeting(meeting_id, {"status": "cancelled"})
