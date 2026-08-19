from datetime import timedelta

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.integrations.email import EmailClient
from app.models.orm.admin_user import AdminUser
from app.repositories.admin_user_repo import AdminUserRepository

logger = structlog.get_logger()

ACCESS_TOKEN_EXPIRE = timedelta(hours=24)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)
RESET_TOKEN_EXPIRE = timedelta(minutes=15)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = AdminUserRepository(session)
        self.email = EmailClient()

    async def signup(self, email: str, password: str, name: str | None = None, role: str = "agent") -> dict:
        existing = await self.repo.find_by_email(email)
        if existing:
            raise ConflictException("A user with this email already exists")

        user = await self.repo.create({
            "email": email.lower().strip(),
            "password_hash": hash_password(password),
            "name": name,
            "role": role,
        })
        logger.info("user_signed_up", user_id=str(user.id), email=email, role=role)
        return self._build_token_response(user)

    async def login(self, email: str, password: str) -> dict:
        user = await self.repo.find_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        logger.info("user_logged_in", user_id=str(user.id), email=email)
        return self._build_token_response(user)

    async def refresh_token(self, refresh_token: str) -> dict:
        payload = decode_access_token(refresh_token)
        if not payload or "sub" not in payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token")

        user = await self.repo.find_by_id(payload["sub"])
        if not user:
            raise UnauthorizedException("User not found")

        return self._build_token_response(user, include_refresh=True)

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> dict:
        user = await self.repo.find_by_id(user_id)
        if not user or not verify_password(old_password, user.password_hash):
            raise UnauthorizedException("Current password is incorrect")

        await self.repo.update_password(user_id, hash_password(new_password))
        logger.info("password_changed", user_id=user_id)
        return {"message": "Password updated successfully"}

    async def reset_password_request(self, email: str) -> dict:
        user = await self.repo.find_by_email(email)
        if not user:
            return {"message": "If that email exists, a reset link has been sent"}

        reset_token = create_access_token(
            {"sub": str(user.id), "type": "reset", "email": email},
            expires_delta=RESET_TOKEN_EXPIRE,
        )

        settings = get_settings()
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        if settings.smtp_is_configured:
            self.email.send_email(
                to=email,
                subject="Reset your password",
                html_body=f"""
                <h2>Password Reset Request</h2>
                <p>Click the link below to reset your password. This link expires in 15 minutes.</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>If you didn't request this, you can safely ignore this email.</p>
                """,
            )
            logger.info("password_reset_emailed", user_id=str(user.id), email=email)
            return {"message": "If that email exists, a reset link has been sent"}

        logger.info("password_reset_requested", user_id=str(user.id), email=email)
        return {
            "message": "If that email exists, a reset link has been sent",
            "reset_token": reset_token,
        }

    async def reset_password_confirm(self, token: str, new_password: str) -> dict:
        payload = decode_access_token(token)
        if not payload or "sub" not in payload or payload.get("type") != "reset":
            raise UnauthorizedException("Invalid or expired reset token")

        await self.repo.update_password(payload["sub"], hash_password(new_password))
        logger.info("password_reset_completed", user_id=payload["sub"])
        return {"message": "Password reset successfully"}

    async def get_user_by_id(self, user_id: str) -> AdminUser | None:
        return await self.repo.find_by_id(user_id)

    def _build_token_response(self, user: AdminUser, include_refresh: bool = True) -> dict:
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        access_token = create_access_token(token_data, expires_delta=ACCESS_TOKEN_EXPIRE)

        response = {
            "access_token": access_token,
            "refresh_token": None,
            "token_type": "bearer",
            "expires_in": int(ACCESS_TOKEN_EXPIRE.total_seconds()),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role,
            },
        }

        if include_refresh:
            refresh_data = {**token_data, "type": "refresh"}
            response["refresh_token"] = create_access_token(refresh_data, expires_delta=REFRESH_TOKEN_EXPIRE)

        return response
