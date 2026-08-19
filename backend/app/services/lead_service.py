import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.models.lead import LeadUpdate
from app.models.orm.lead import Lead
from app.repositories.lead_repo import LeadRepository
from app.utils.helpers import format_phone_international, utc_now

logger = structlog.get_logger()


class LeadService:
    def __init__(self, session: AsyncSession):
        self.repo = LeadRepository(session)

    async def get_or_create_by_phone(self, phone: str, name: str | None = None) -> Lead:
        normalized = format_phone_international(phone)
        now = utc_now()
        lead = await self.repo.find_by_phone(normalized)

        if lead:
            lead.last_contacted_at = now
            await self.repo.session.commit()
            await self.repo.session.refresh(lead)
            logger.info("lead_found", lead_id=str(lead.id), phone=normalized)
            return lead

        new_lead = await self.repo.create({
            "whatsapp_phone": normalized,
            "name": name,
            "status": "new",
            "source": "meta_ads",
            "conversation_stage": "greeting",
            "last_contacted_at": now,
        })
        logger.info("lead_created", lead_id=str(new_lead.id), phone=normalized)
        return new_lead

    async def create_lead(self, phone: str, name: str | None = None, source: str = "meta_ads") -> Lead:
        normalized = format_phone_international(phone)
        existing = await self.repo.find_by_phone(normalized)
        if existing:
            raise ConflictException("Lead with this phone already exists")

        return await self.repo.create({
            "whatsapp_phone": normalized,
            "name": name,
            "status": "new",
            "source": source,
            "conversation_stage": "greeting",
        })

    async def update_lead(self, lead_id: str, data: LeadUpdate) -> Lead | None:
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(lead_id, update_data)

    async def get_lead(self, lead_id: str) -> Lead | None:
        return await self.repo.find_by_id(lead_id)

    async def list_leads(
        self, page: int = 1, page_size: int = 20,
        status: str | None = None, source: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Lead], int]:
        return await self.repo.list_all(page, page_size, status, source, search)
