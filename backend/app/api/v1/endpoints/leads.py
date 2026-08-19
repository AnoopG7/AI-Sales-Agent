from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.core.exceptions import NotFoundException
from app.models.common import PaginatedResponse
from app.models.lead import LeadCreate, LeadResponse, LeadUpdate, NoteCreate
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.lead_repo import LeadRepository
from app.services.lead_service import LeadService

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_leads(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status: str | None = None,
    source: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    service = LeadService(db)
    data, total = await service.list_leads(page, page_size, status, source, search)
    return {
        "data": [LeadResponse.model_validate(item) for item in data],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = LeadService(db)
    lead = await service.get_lead(lead_id)
    if not lead:
        raise NotFoundException("Lead not found")
    return lead


@router.post("", status_code=201, response_model=LeadResponse)
async def create_lead(
    body: LeadCreate,
    db: AsyncSession = Depends(get_db),
):
    service = LeadService(db)
    return await service.create_lead(
        phone=body.whatsapp_phone,
        name=body.name,
        source=body.source,
    )


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    body: LeadUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = LeadService(db)
    lead = await service.get_lead(lead_id)
    if not lead:
        raise NotFoundException("Lead not found")
    return await service.update_lead(lead_id, body)


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = LeadService(db)
    lead = await service.get_lead(lead_id)
    if not lead:
        raise NotFoundException("Lead not found")
    repo = LeadRepository(db)
    await repo.delete(lead_id)


@router.get("/{lead_id}/conversations")
async def get_lead_conversations(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = LeadService(db)
    lead = await service.get_lead(lead_id)
    if not lead:
        raise NotFoundException("Lead not found")
    repo = ConversationRepository(db)
    return await repo.get_history(lead_id)


@router.post("/{lead_id}/notes", status_code=201)
async def add_lead_note(
    lead_id: str,
    body: NoteCreate,
    db: AsyncSession = Depends(get_db),
):
    service = LeadService(db)
    lead = await service.get_lead(lead_id)
    if not lead:
        raise NotFoundException("Lead not found")

    existing_notes = lead.notes or ""
    new_note = body.note
    timestamp = datetime.now(UTC).isoformat()
    updated = f"{existing_notes}\n[{timestamp}] {new_note}".strip()

    repo = LeadRepository(db)
    await repo.update(lead_id, {"notes": updated})
    return {"notes": updated}
