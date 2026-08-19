from collections import defaultdict
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.lead import Lead
from app.models.orm.meeting import Meeting

logger = structlog.get_logger()


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_overview(self) -> dict:
        async def count(stmt) -> int:
            return (await self.session.execute(stmt)).scalar() or 0

        total_leads = await count(select(func.count()).select_from(Lead))
        qualified = await count(select(func.count()).select_from(Lead).where(Lead.status == "qualified"))
        upcoming = await count(
            select(func.count()).select_from(Meeting)
            .where(Meeting.status.in_(["scheduled", "confirmed"]))
        )
        converted = await count(select(func.count()).select_from(Lead).where(Lead.status == "converted"))

        conv_rate = round(converted / total_leads * 100, 1) if total_leads > 0 else 0.0

        logger.info("analytics_overview",
                     total_leads=total_leads, qualified=qualified,
                     upcoming=upcoming, converted=converted, conv_rate=conv_rate)
        return {
            "total_leads": total_leads,
            "qualified_leads": qualified,
            "upcoming_meetings": upcoming,
            "converted_leads": converted,
            "conversion_rate": conv_rate,
        }

    async def get_leads_over_time(self, days: int = 30) -> list[dict]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        stmt = select(Lead.created_at).where(Lead.created_at >= cutoff).order_by(Lead.created_at)
        rows = (await self.session.execute(stmt)).scalars().all()

        daily: dict[str, int] = defaultdict(int)
        for dt in rows:
            daily[dt.strftime("%Y-%m-%d")] += 1
        result = [{"date": d, "count": c} for d, c in sorted(daily.items())]
        logger.info("analytics_leads_over_time", days=days, data_points=len(result))
        return result

    async def get_status_breakdown(self) -> list[dict]:
        stmt = select(Lead.status)
        rows = (await self.session.execute(stmt)).scalars().all()

        counts: dict[str, int] = {}
        for status in rows:
            counts[status] = counts.get(status, 0) + 1

        statuses = (
            "new", "contacted", "qualified", "meeting_scheduled",
            "converted", "lost", "spam",
        )
        result = [{"status": s, "count": counts.get(s, 0)} for s in statuses]
        logger.info("analytics_status_breakdown", breakdown={s: c for s, c in counts.items()})
        return result

    async def get_source_breakdown(self) -> list[dict]:
        stmt = select(Lead.source)
        rows = (await self.session.execute(stmt)).scalars().all()

        counts: dict[str, int] = {}
        for source in rows:
            counts[source] = counts.get(source, 0) + 1

        sources = ("meta_ads", "manual", "referral", "website", "other")
        result = [{"source": s, "count": counts.get(s, 0)} for s in sources]
        logger.info("analytics_source_breakdown", breakdown={s: c for s, c in counts.items()})
        return result
