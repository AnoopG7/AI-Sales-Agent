import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.lead import Lead

logger = structlog.get_logger()


class LeadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_phone(self, phone: str) -> Lead | None:
        lead = (await self.session.execute(
            select(Lead).where(Lead.whatsapp_phone == phone)
        )).scalar_one_or_none()
        if lead:
            logger.debug("lead_found_by_phone", lead_id=str(lead.id), phone=phone)
        return lead

    async def find_by_id(self, lead_id: str) -> Lead | None:
        lead = (await self.session.execute(
            select(Lead).where(Lead.id == lead_id)
        )).scalar_one_or_none()
        if lead:
            logger.debug("lead_found_by_id", lead_id=lead_id)
        return lead

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        source: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Lead], int]:
        base = select(Lead)
        count_base = select(func.count()).select_from(Lead)

        if status:
            base = base.where(Lead.status == status)
            count_base = count_base.where(Lead.status == status)
        if source:
            base = base.where(Lead.source == source)
            count_base = count_base.where(Lead.source == source)
        if search:
            pattern = f"%{search}%"
            base = base.where(
                or_(Lead.name.ilike(pattern), Lead.whatsapp_phone.ilike(pattern))
            )
            count_base = count_base.where(
                or_(Lead.name.ilike(pattern), Lead.whatsapp_phone.ilike(pattern))
            )

        offset = (page - 1) * page_size
        base = base.order_by(Lead.created_at.desc()).offset(offset).limit(page_size)

        total = (await self.session.execute(count_base)).scalar() or 0
        rows = (await self.session.execute(base)).scalars().all()
        logger.debug("lead_list_all", total=total, page=page, page_size=page_size, filters={"status": status, "source": source, "search": search})
        return list(rows), total

    async def create(self, data: dict) -> Lead:
        lead = Lead(**data)
        self.session.add(lead)
        await self.session.commit()
        await self.session.refresh(lead)
        logger.info("lead_db_created", lead_id=str(lead.id), phone=data.get("whatsapp_phone"))
        return lead

    async def update(self, lead_id: str, data: dict) -> Lead | None:
        lead = await self.find_by_id(lead_id)
        if not lead:
            logger.warning("lead_update_not_found", lead_id=lead_id)
            return None
        for key, value in data.items():
            setattr(lead, key, value)
        await self.session.commit()
        await self.session.refresh(lead)
        logger.info("lead_db_updated", lead_id=lead_id, fields=list(data.keys()))
        return lead

    async def delete(self, lead_id: str) -> bool:
        lead = await self.find_by_id(lead_id)
        if not lead:
            logger.warning("lead_delete_not_found", lead_id=lead_id)
            return False
        await self.session.delete(lead)
        await self.session.commit()
        logger.info("lead_db_deleted", lead_id=lead_id)
        return True
