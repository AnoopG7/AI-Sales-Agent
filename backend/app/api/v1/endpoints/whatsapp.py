"""
WhatsApp webhook endpoints.

- GET  /whatsapp/webhook  — Meta verification handshake
- POST /whatsapp/webhook — Inbound message → AI agent → reply
"""

import json

import structlog
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.orchestrator import process_message
from app.api.v1.deps import get_db
from app.core.config import get_settings
from app.core.exceptions import ForbiddenException
from app.core.security import verify_whatsapp_signature
from app.integrations.whatsapp import WhatsAppClient
from app.repositories.conversation_repo import ConversationRepository
from app.services.lead_service import LeadService

logger = structlog.get_logger()
router = APIRouter()

whatsapp_client = WhatsAppClient()


@router.get("/webhook")
def verify_webhook(
    hub_mode: str | None = None,
    hub_verify_token: str | None = None,
    hub_challenge: str | None = None,
):
    """Meta sends a GET request to verify the webhook endpoint."""
    settings = get_settings()
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("webhook_verified")
        return int(hub_challenge) if hub_challenge else hub_challenge

    logger.warning("webhook_verify_failed", mode=hub_mode)
    raise ForbiddenException("Invalid verify token")


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Receive inbound WhatsApp message, process via AI agent, respond."""
    body = await request.body()
    raw_body = body.decode("utf-8")

    # Verify signature (skip in dev if no secret set)
    signature = request.headers.get("X-Hub-Signature-256", "")
    settings = get_settings()
    if settings.WHATSAPP_APP_SECRET and not verify_whatsapp_signature(body, signature):
        logger.warning("webhook_sig_invalid")
        return {"status": "ignored"}

    payload = json.loads(raw_body)

    # Parse the message
    parsed = WhatsAppClient.parse_webhook_payload(payload)
    if not parsed:
        return {"status": "ok"}

    conversation_repo = ConversationRepository(db)
    lead_service = LeadService(db)

    # Dedup by WhatsApp message ID
    if await conversation_repo.message_exists(parsed["message_id"]):
        logger.info("duplicate_message", message_id=parsed["message_id"])
        return {"status": "ok"}

    # Get or create lead
    lead = await lead_service.get_or_create_by_phone(
        phone=parsed["from"],
        name=parsed.get("sender_name"),
    )

    # Store user message
    await conversation_repo.add_message({
        "lead_id": lead.id,
        "role": "user",
        "content": parsed["text"],
        "message_type": "text",
        "whatsapp_message_id": parsed["message_id"],
    })

    # Process via AI agent
    try:
        reply = await process_message(
            lead_id=str(lead.id),
            message_text=parsed["text"],
            lead=lead,
            session=db,
        )
    except Exception:
        logger.exception("agent_error", lead_id=str(lead.id))
        reply = (
            "Thank you for your message! One of our team members "
            "will get back to you shortly."
        )

    # Send reply via WhatsApp
    try:
        await whatsapp_client.send_text_message(to=parsed["from"], text=reply)
    except Exception:
        logger.exception("whatsapp_send_failed", lead_id=str(lead.id), to=parsed["from"])

    # Store assistant message
    await conversation_repo.add_message({
        "lead_id": lead.id,
        "role": "assistant",
        "content": reply,
        "message_type": "text",
    })

    return {"status": "ok"}
