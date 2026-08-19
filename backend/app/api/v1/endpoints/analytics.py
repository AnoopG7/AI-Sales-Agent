from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_overview()


@router.get("/leads-over-time")
async def get_leads_over_time(
    days: Annotated[int, Query(ge=1, le=365)] = 30,
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_leads_over_time(days)


@router.get("/status-breakdown")
async def get_status_breakdown(
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_status_breakdown()


@router.get("/source-breakdown")
async def get_source_breakdown(
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_source_breakdown()
