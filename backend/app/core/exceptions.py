"""
Custom exception classes and FastAPI exception handlers.
"""

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        detail: dict | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        msg = f"{resource} not found"
        if resource_id:
            msg = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=msg, status_code=404)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Invalid or missing authentication credentials"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "You don't have permission to perform this action"):
        super().__init__(message=message, status_code=403)


class BadRequestException(AppException):
    def __init__(self, message: str = "Invalid request", detail: dict | None = None):
        super().__init__(message=message, status_code=400, detail=detail)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=409)


class ExternalServiceException(AppException):
    def __init__(self, service: str, message: str = ""):
        msg = f"External service '{service}' failed"
        if message:
            msg += f": {message}"
        super().__init__(message=msg, status_code=502)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "app_exception",
            message=exc.message,
            status_code=exc.status_code,
            detail=exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", error=str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "An internal server error occurred",
                "detail": {},
            },
        )
