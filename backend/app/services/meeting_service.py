from datetime import datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.meeting import Meeting
from app.repositories.conversation_repo import MeetingRepository

logger = structlog.get_logger()


class MeetingService:
    def __init__(self, session: AsyncSession):
        self.repo = MeetingRepository(session)

    async def schedule_meeting(
        self, lead_id: str, scheduled_at: str, duration: int = 30,
        timezone: str = "Asia/Dubai", notes: str | None = None,
    ) -> Meeting:
        meeting = await self.repo.create({
            "lead_id": lead_id,
            "scheduled_at": datetime.fromisoformat(scheduled_at),
            "duration_minutes": duration,
            "timezone": timezone,
            "status": "scheduled",
            "notes": notes,
        })
        logger.info("meeting_scheduled", meeting_id=str(meeting.id), lead_id=lead_id)
        return meeting

    async def get_meeting(self, meeting_id: str) -> Meeting | None:
        meeting = await self.repo.find_by_id(meeting_id)
        if meeting:
            logger.debug("meeting_found", meeting_id=meeting_id)
        else:
            logger.warning("meeting_not_found", meeting_id=meeting_id)
        return meeting

    async def list_meetings(
        self, page: int = 1, page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Meeting], int]:
        results, total = await self.repo.list_all(page, page_size, status)
        logger.debug("meetings_listed", total=total, page=page, status=status)
        return results, total

    async def get_upcoming_meetings(self, limit: int = 5) -> list[Meeting]:
        meetings = await self.repo.get_upcoming(limit)
        logger.debug("upcoming_meetings", count=len(meetings))
        return meetings

    async def update_meeting(self, meeting_id: str, data: dict) -> Meeting | None:
        meeting = await self.repo.update(meeting_id, data)
        if meeting:
            logger.info("meeting_updated", meeting_id=meeting_id, fields=list(data.keys()))
        else:
            logger.warning("meeting_update_not_found", meeting_id=meeting_id)
        return meeting
