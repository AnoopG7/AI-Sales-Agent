"""
Email integration via smtplib (stdlib, no external dependency).

Configuration via env vars:
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL

When SMTP is not configured, emails are logged to console (dev mode).
"""

import asyncio
import smtplib
from email.message import EmailMessage

import structlog

from app.core.config import get_settings

logger = structlog.get_logger()


class EmailClient:
    async def send_email(self, to: str, subject: str, html_body: str) -> dict:
        settings = get_settings()

        if not settings.smtp_is_configured:
            logger.info("email_dev_stub", to=to, subject=subject)
            return {"id": "dev_stub", "status": "logged"}

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = to
        msg.set_content(html_body, subtype="html")

        try:
            await asyncio.to_thread(self._smtp_send, settings, msg)
            logger.info("email_sent", to=to, subject=subject)
            return {"id": "sent", "status": "sent"}
        except Exception:
            logger.exception("email_send_failed", to=to, subject=subject)
            return {"id": "", "status": "failed"}

    def _smtp_send(self, settings, msg: EmailMessage):
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
