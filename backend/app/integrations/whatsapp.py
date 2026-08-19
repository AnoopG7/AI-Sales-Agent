"""
WhatsApp Cloud API integration.

Handles sending messages via the Meta WhatsApp Business Platform.
Receives/parses webhook payloads.
"""

import httpx
import structlog

from app.core.config import get_settings

logger = structlog.get_logger()


class WhatsAppClient:
    """Client for the WhatsApp Cloud API."""

    def __init__(self):
        self.settings = get_settings()

    async def send_text_message(self, to: str, text: str) -> dict:
        """Send a plain text message via WhatsApp."""
        url = self.settings.whatsapp_api_url
        headers = {
            "Authorization": f"Bearer {self.settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info("whatsapp_message_sent", to=to, message_id=data.get("messages", [{}])[0].get("id"))
            return data

    @staticmethod
    def parse_webhook_payload(payload: dict) -> dict | None:
        """Extract the relevant message data from a Meta webhook payload."""
        try:
            entry = payload.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})

            messages = value.get("messages", [])
            if not messages:
                return None

            message = messages[0]
            contacts = value.get("contacts", [{}])
            sender_name = contacts[0].get("profile", {}).get("name") if contacts else None

            return {
                "from": message.get("from"),
                "message_id": message.get("id"),
                "timestamp": message.get("timestamp"),
                "type": message.get("type"),
                "text": message.get("text", {}).get("body", ""),
                "sender_name": sender_name,
            }
        except (IndexError, KeyError):
            logger.warning("webhook_parse_failed", payload=payload)
            return None
