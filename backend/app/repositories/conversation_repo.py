from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.conversation import Conversation
from app.models.orm.meeting import Meeting

logger = structlog.get_logger()


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_history(self, lead_id: str, limit: int = 50) -> list[Conversation]:
        rows = (await self.session.execute(
            select(Conversation)
            .where(Conversation.lead_id == lead_id)
            .order_by(Conversation.created_at)
            .limit(limit)
        )).scalars().all()
        logger.debug("conversation_history", lead_id=lead_id, count=len(rows))
        return list(rows)

    async def add_message(self, data: dict) -> Conversation:
        msg = Conversation(**data)
        self.session.add(msg)
        await self.session.commit()
        await self.session.refresh(msg)
        logger.debug("conversation_message_added", lead_id=str(data.get("lead_id")),
                      role=data.get("role"), content_len=len(data.get("content", "")))
        return msg

    async def message_exists(self, whatsapp_message_id: str) -> bool:
        count = (await self.session.execute(
            select(func.count())
            .select_from(Conversation)
            .where(Conversation.whatsapp_message_id == whatsapp_message_id)
        )).scalar() or 0
        exists = count > 0
        if exists:
            logger.debug("conversation_duplicate", whatsapp_message_id=whatsapp_message_id)
        return exists


class MeetingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, meeting_id: str) -> Meeting | None:
        meeting = (await self.session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        )).scalar_one_or_none()
        if meeting:
            logger.debug("meeting_found_by_id", meeting_id=meeting_id)
        return meeting

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Meeting], int]:
        base = select(Meeting)
        count_base = select(func.count()).select_from(Meeting)

        if status:
            base = base.where(Meeting.status == status)
            count_base = count_base.where(Meeting.status == status)

        offset = (page - 1) * page_size
        base = base.order_by(Meeting.scheduled_at.desc()).offset(offset).limit(page_size)

        total = (await self.session.execute(count_base)).scalar() or 0
        rows = (await self.session.execute(base)).scalars().all()
        logger.debug("meeting_list_all", total=total, page=page, status=status)
        return list(rows), total

    async def get_upcoming(self, limit: int = 5) -> list[Meeting]:
        rows = (await self.session.execute(
            select(Meeting)
            .where(Meeting.scheduled_at >= datetime.now(UTC))
            .where(Meeting.status.in_(["scheduled", "confirmed"]))
            .order_by(Meeting.scheduled_at)
            .limit(limit)
        )).scalars().all()
        logger.debug("meeting_upcoming", count=len(rows))
        return list(rows)

    async def create(self, data: dict) -> Meeting:
        meeting = Meeting(**data)
        self.session.add(meeting)
        await self.session.commit()
        await self.session.refresh(meeting)
        logger.info("meeting_db_created", meeting_id=str(meeting.id),
                     lead_id=str(data.get("lead_id")), scheduled_at=str(data.get("scheduled_at")))
        return meeting

    async def update(self, meeting_id: str, data: dict) -> Meeting | None:
        meeting = await self.find_by_id(meeting_id)
        if not meeting:
            logger.warning("meeting_update_not_found", meeting_id=meeting_id)
            return None
        for key, value in data.items():
            setattr(meeting, key, value)
        await self.session.commit()
        await self.session.refresh(meeting)
        logger.info("meeting_db_updated", meeting_id=meeting_id, fields=list(data.keys()))
        return meeting
