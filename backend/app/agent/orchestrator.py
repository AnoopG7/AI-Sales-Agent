"""
AI agent orchestrator — main message processing loop.

Flow:
  1. Load lead data + conversation history
  2. Build messages array with system prompt + stage instructions + history + user message
  3. Call LLM with tool definitions (retry on 429 for Groq)
  4. Execute any tool calls (handling parallel calls correctly), append results
  5. If lead was modified by tools, rebuild system prompt with fresh data
  6. Loop until final text response (max 10 tool rounds)
  7. Return response text
"""

import asyncio
import json
from datetime import UTC, datetime

import structlog
from openai import RateLimitError
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.prompts import render_system_prompt
from app.agent.tools import TOOL_DEFINITIONS, execute_tool
from app.core.config import get_settings
from app.integrations.llm_client import LLMClient
from app.models.orm.lead import Lead
from app.repositories.conversation_repo import ConversationRepository
from app.services.lead_service import LeadService

logger = structlog.get_logger()

MAX_TOOL_ROUNDS = 10
MAX_HISTORY_MESSAGES = 10
LEAD_MODIFYING_TOOLS = {"update_lead_info", "update_lead_stage", "schedule_meeting"}

# Lazy-init to avoid calling get_settings() at import time
_llm_client: LLMClient | None = None


def _get_llm() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


async def process_message(
    lead_id: str,
    message_text: str,
    lead: Lead | None = None,
    session: AsyncSession | None = None,
) -> str:
    """Process an incoming message and return the AI response."""
    if session is None:
        return "Service temporarily unavailable. Please try again later."

    conversation_repo = ConversationRepository(session)
    lead_service = LeadService(session)

    if lead is None:
        lead = await lead_service.get_lead(lead_id)
        if not lead:
            return "I'm sorry, I couldn't find your information. Please start a new conversation."

    # Load conversation history — enough context for continuity
    history = await conversation_repo.get_history(lead_id, limit=MAX_HISTORY_MESSAGES)

    # Build the messages array
    messages = _build_messages(lead, history, message_text)

    logger.info(
        "agent_processing",
        lead_id=lead_id,
        stage=lead.conversation_stage,
        history_len=len(history),
        message_preview=message_text[:80],
    )

    llm = _get_llm()

    # Main agent loop
    for round_num in range(MAX_TOOL_ROUNDS):
        # ── Call LLM with retry on 429 ────────────────────────────────
        response = None
        for attempt in range(3):
            try:
                response = await llm.chat_completion(
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    temperature=0.6,
                    max_tokens=1024,
                )
                break
            except RateLimitError:
                if attempt < 2:
                    wait = 1 + attempt * 2
                    logger.warning(
                        "llm_rate_limited",
                        lead_id=lead_id,
                        round=round_num,
                        attempt=attempt,
                        retry_after=wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    logger.exception("llm_rate_limit_exhausted", lead_id=lead_id, round=round_num)
                    return "I'm experiencing high demand right now. Please try again in a few minutes. 🙏"
            except Exception:
                logger.exception("llm_api_error", lead_id=lead_id, round=round_num)
                return (
                    "I'm having a brief technical issue. Could you please try again in a moment? 🙏"
                )

        content = response.get("content")
        tool_calls = response.get("tool_calls", [])

        logger.info(
            "agent_round",
            round=round_num,
            has_content=bool(content),
            tool_count=len(tool_calls),
        )

        # If no tool calls, we have the final response
        if not tool_calls:
            if content and content.strip():
                return content
            # Model returned empty content — nudge it
            messages.append({"role": "user", "content": "(Please respond to the lead's message.)"})
            continue

        # ── Handle tool calls correctly ──────────────────────────────────────
        # The LLM API returns ALL tool calls in ONE assistant message.
        # We must append ONE assistant message with all tool_calls, then
        # individual tool result messages for each.

        assistant_msg: dict = {
            "role": "assistant",
            "content": content,  # can be None or text alongside tools
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["function"],
                        "arguments": tc["arguments"],
                    },
                }
                for tc in tool_calls
            ],
        }
        messages.append(assistant_msg)

        # Execute each tool and append results
        modified_lead = False
        for tc in tool_calls:
            try:
                args = json.loads(tc["arguments"])
                result = await execute_tool(
                    name=tc["function"],
                    args=args,
                    lead_id=lead_id,
                    session=session,
                )
                if tc["function"] in LEAD_MODIFYING_TOOLS:
                    modified_lead = True
            except json.JSONDecodeError:
                logger.exception(
                    "tool_args_parse_failed",
                    tool=tc["function"],
                    arguments=tc["arguments"],
                )
                result = (
                    "Error: Invalid JSON in tool arguments. Please fix and retry with valid JSON."
                )
            except Exception:
                logger.exception("tool_execution_failed", tool=tc["function"])
                result = f"Error executing {tc['function']}. Please try again."

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                }
            )

        # ── Rebuild system prompt if lead was modified ──────────────
        if modified_lead:
            lead = await lead_service.get_lead(lead_id)
            messages[0]["content"] = _system_prompt(lead)

    # ── Exhausted tool rounds — force a final text-only response ─────────
    try:
        response = await llm.chat_completion(
            messages=messages,
            tools=None,  # no tools for the final call
            tool_choice="none",
            temperature=0.7,
            max_tokens=1024,
        )
        final = response.get("content") or ""
        if final.strip():
            return final
    except Exception:
        logger.exception("llm_final_fallback_error", lead_id=lead_id)

    # Last resort contextual fallback
    lead_name = lead.name or "there"
    return (
        f"Thanks for your patience{', ' + lead_name if lead.name else ''}! "
        "I've noted everything. Would you like to compare plans, "
        "book a demo, or is there anything specific I can help with? 👋"
    )


def _build_messages(
    lead: Lead,
    history: list,
    user_message: str,
) -> list[dict]:
    """Build the messages array for the LLM API call."""
    messages: list[dict] = [
        {"role": "system", "content": _system_prompt(lead)},
    ]

    # Add conversation history
    for msg in history:
        role = getattr(msg, "role", "user")
        content = getattr(msg, "content", "")
        if content and role in ("user", "assistant"):
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})
    return messages


def _system_prompt(lead: Lead) -> str:
    """System prompt with fresh lead data, persona and stage instructions."""
    settings = get_settings()
    return render_system_prompt(
        lead_context=_build_context(lead, settings.DEFAULT_CURRENCY),
        stage=lead.conversation_stage or "greeting",
        agent_name=settings.AGENT_NAME,
        company_name=settings.COMPANY_NAME,
        currency=settings.DEFAULT_CURRENCY,
        today=datetime.now(UTC).strftime("%A, %d %B %Y (UTC)"),
    )


def _build_context(lead: Lead, currency: str) -> str:
    """Build a structured context block from lead data.

    Uses a readable format (not a single pipe-separated line) so the
    model can clearly see what it knows and what's missing.
    """
    lines = []
    lines.append(f"- Name: {lead.name or 'Not provided yet'}")
    lines.append(f"- Phone: {lead.whatsapp_phone}")

    if lead.email:
        lines.append(f"- Email: {lead.email}")
    else:
        lines.append("- Email: Not collected yet")

    # Budget
    if lead.budget_min and lead.budget_max:
        lines.append(f"- Budget: {currency} {lead.budget_min:,.0f} – {currency} {lead.budget_max:,.0f}")
    elif lead.budget_max:
        lines.append(f"- Budget: Up to {currency} {lead.budget_max:,.0f}")
    elif lead.budget_min:
        lines.append(f"- Budget: From {currency} {lead.budget_min:,.0f}")
    else:
        lines.append("- Budget: Not specified yet")

    # Company & needs
    lines.append(f"- Company: {lead.company or 'Not provided yet'}")
    lines.append(f"- Team size (seats): {lead.team_size or 'Not specified yet'}")
    lines.append(f"- Product interest: {lead.product_interest or 'Not specified yet'}")

    # State
    lines.append(f"- Lead status: {lead.status}")
    lines.append(f"- Conversation stage: {lead.conversation_stage or 'greeting'}")

    if lead.notes:
        lines.append(f"- Notes: {lead.notes}")

    return "\n".join(lines)
