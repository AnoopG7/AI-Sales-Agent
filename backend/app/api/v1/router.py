"""
API v1 router aggregator.

Mounts all endpoint routers under /api/v1/.
"""

from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.leads import router as leads_router
from app.api.v1.endpoints.meetings import router as meetings_router
from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.whatsapp import router as whatsapp_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(leads_router, prefix="/leads", tags=["Leads"], dependencies=[Depends(get_current_user)])
router.include_router(products_router, prefix="/products", tags=["Products"], dependencies=[Depends(get_current_user)])
router.include_router(meetings_router, prefix="/meetings", tags=["Meetings"], dependencies=[Depends(get_current_user)])
router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"], dependencies=[Depends(get_current_user)])
router.include_router(whatsapp_router, prefix="/whatsapp", tags=["WhatsApp"])
