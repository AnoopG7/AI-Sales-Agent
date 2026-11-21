"""
FastAPI application factory.

Creates and configures the FastAPI app with:
- CORS middleware
- Request logging middleware
- Exception handlers
- API router registration
- Health check endpoint
- Lifespan events (startup/shutdown)
"""

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.database import close_db, init_db
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

logger = structlog.get_logger()


class RequestLogMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request with method, path, status, and duration."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.monotonic()
        response = await call_next(request)
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "api_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — runs on startup and shutdown."""
    setup_logging()
    settings = get_settings()
    await init_db()
    logger.info(
        "app_starting",
        environment=settings.ENVIRONMENT,
        cors_origins=settings.cors_origins,
        version="0.1.0",
    )
    yield
    await close_db()
    logger.info("app_shutting_down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="AI Sales Agent API",
        description="WhatsApp AI sales agent: lead qualification, product recommendations and demo booking",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Request Logging ---
    app.add_middleware(RequestLogMiddleware)

    # --- Exception Handlers ---
    register_exception_handlers(app)

    # --- Routes ---
    @app.get("/health", tags=["System"])
    async def health_check() -> dict:
        logger.info("health_check_ok", environment=settings.ENVIRONMENT)
        return {
            "status": "healthy",
            "version": "0.1.0",
            "environment": settings.ENVIRONMENT,
        }

    logger.info("router_mounted", prefix="/api/v1", routes=len(v1_router.routes))

    # Mount the v1 API router
    app.include_router(v1_router, prefix="/api/v1")

    return app


# Application instance for uvicorn
app = create_app()
