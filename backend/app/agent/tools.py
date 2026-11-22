"""
Groq-compatible function tool definitions + executor functions.

Each tool has:
  - definition: JSON schema for Groq/OpenAI function calling
  - handler: async function that calls the appropriate service layer
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.integrations.email import EmailClient
from app.models.lead import LeadUpdate
from app.services.lead_service import LeadService
from app.services.meeting_service import MeetingService
from app.services.product_service import ProductService

logger = structlog.get_logger()
email_client = EmailClient()

# ─── Tool Definitions (Groq/OpenAI function calling schema) ───────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Search active plans/products in the catalog by category, keyword, "
                "price range (catalog currency) and team size."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["crm", "analytics", "automation", "support", "add_on"],
                        "description": "Product category",
                    },
                    "keyword": {
                        "type": "string",
                        "description": "Use case or feature keyword, e.g. 'forecasting' or 'live chat'",
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price in the catalog currency",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in the catalog currency",
                    },
                    "team_size": {
                        "type": "integer",
                        "description": "Number of seats the lead needs",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_all_products",
            "description": "List all active plans/products. Use when the lead asks to see everything.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Get full details of a specific plan/product by its UUID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The UUID of the product",
                    },
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": (
                "Convert an amount between currencies (e.g. INR to USD). "
                "Use this when a lead quotes a budget in a currency other than "
                "the catalog currency, so searches use the right amount."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "The amount to convert",
                    },
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency code (e.g. INR, EUR, GBP)",
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency code (e.g. USD)",
                    },
                },
                "required": ["amount", "from_currency", "to_currency"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_lead_info",
            "description": (
                "Save or update lead information as you learn it. "
                "Pass null to clear a constraint (e.g. budget_max: null = no limit)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Lead's full name"},
                    "email": {"type": "string", "description": "Lead's work email address"},
                    "company": {"type": "string", "description": "Lead's company name"},
                    "team_size": {"type": "integer", "description": "Seats needed. Null to clear."},
                    "product_interest": {
                        "type": "string",
                        "description": "What they want to solve or which product they're interested in",
                    },
                    "budget_min": {"type": "number", "description": "Minimum budget in catalog currency. Null to clear."},
                    "budget_max": {"type": "number", "description": "Maximum budget in catalog currency. Null to clear."},
                    "notes": {"type": "string", "description": "Additional notes (role, timeline, current tools)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_lead_stage",
            "description": "Advance the conversation stage as the lead progresses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "stage": {
                        "type": "string",
                        "enum": [
                            "greeting", "qualification", "discovery",
                            "proposal", "demo_scheduling", "follow_up", "closed",
                        ],
                        "description": "The conversation stage to move to",
                    },
                },
                "required": ["stage"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Book a demo call or meeting with the sales team.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scheduled_at": {
                        "type": "string",
                        "description": "Date and time in ISO 8601 (e.g. 2026-05-15T10:00:00)",
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Duration in minutes (default 30)",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Agenda, products to demo, or attendee notes",
                    },
                },
                "required": ["scheduled_at"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Email the lead a plan summary, pricing overview or meeting details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Lead's email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body text"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_human",
            "description": (
                "Hand off to a human sales rep for custom pricing, contracts, "
                "security reviews, or when the lead asks for a person."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "Reason for escalation"},
                },
                "required": ["reason"],
            },
        },
    },
]


# ─── Tool Name → Handler Mapping ──────────────────────────────────────────────

async def execute_tool(name: str, args: dict, lead_id: str, session: AsyncSession) -> str:
    """Execute a tool by name with given args. Returns a human-readable result string."""
    logger.info("tool_executing", tool=name, lead_id=lead_id, args=args)
    match name:
        case "search_products":
            return await _search_products(args, session)
        case "list_all_products":
            return await _list_all_products(session)
        case "get_product_details":
            return await _get_product_details(args, session)
        case "convert_currency":
            return await _convert_currency(args)
        case "update_lead_info":
            return await _update_lead_info(args, lead_id, session)
        case "update_lead_stage":
            return await _update_lead_stage(args, lead_id, session)
        case "schedule_meeting":
            return await _schedule_meeting(args, lead_id, session)
        case "send_email":
            return await _send_email(args)
        case "transfer_to_human":
            return _transfer_to_human(args)
        case _:
            return f"Unknown tool: {name}"


# ─── Handlers ─────────────────────────────────────────────────────────────────


def _seats(p) -> str:
    if p.max_seats:
        return f"{p.min_seats}-{p.max_seats} seats"
    return f"{p.min_seats}+ seats"


def _price(p) -> str:
    currency = get_settings().DEFAULT_CURRENCY
    period = {"monthly": "/seat/mo", "annual": "/seat/yr", "one_time": " one-time"}.get(p.billing_period, "")
    return f"{currency} {p.price:,.2f}{period}"


async def _search_products(args: dict, session: AsyncSession) -> str:
    service = ProductService(session)
    results = await service.search_products(
        category=args.get("category"),
        keyword=args.get("keyword"),
        min_price=args.get("min_price"),
        max_price=args.get("max_price"),
        team_size=args.get("team_size"),
        limit=5,
    )
    if not results:
        return "No products found matching those criteria."

    lines = [f"Found {len(results)} matching products:"]
    for p in results:
        lines.append(f"- {p.name} | {p.category} | {_price(p)} | {_seats(p)} | ID: {p.id}")
    return "\n".join(lines)


async def _list_all_products(session: AsyncSession) -> str:
    service = ProductService(session)
    results, total = await service.list_products(page=1, page_size=20, status="active")
    if not results:
        return "No products available at the moment."

    lines = [f"All active products ({total} total):"]
    for p in results:
        lines.append(f"- {p.name} | {p.category} | {_price(p)} | {_seats(p)} | ID: {p.id}")
    return "\n".join(lines)


async def _get_product_details(args: dict, session: AsyncSession) -> str:
    service = ProductService(session)
    product = await service.get_product(args["product_id"])
    if not product:
        return "Product not found."
    features = ", ".join(product.features) if product.features else "N/A"
    return (
        f"{product.name} ({product.category})\n"
        f"Price: {_price(product)}\n"
        f"Seats: {_seats(product)}\n"
        f"{'Featured plan\n' if product.featured else ''}"
        f"Features: {features}\n"
        f"{product.description or 'No description'}"
    )


async def _convert_currency(args: dict) -> str:
    """Convert currency using live rates from a free API.

    Falls back to approximate hardcoded rates if the API is unavailable.
    """
    amount = args["amount"]
    from_cur = args["from_currency"].upper()
    to_cur = args["to_currency"].upper()

    if from_cur == to_cur:
        return f"{amount:,.2f} {from_cur} = {amount:,.2f} {to_cur}"

    # Try live rate from exchangerate.host (free, no key required)
    rate = await _fetch_exchange_rate(from_cur, to_cur)

    if rate is None:
        # Fallback to approximate rates (USD as base)
        fallback_to_usd = {
            "USD": 1.0,
            "EUR": 1.08,    # 1 EUR ≈ 1.08 USD
            "GBP": 1.27,    # 1 GBP ≈ 1.27 USD
            "INR": 0.012,   # 1 INR ≈ 0.012 USD
            "AUD": 0.66,    # 1 AUD ≈ 0.66 USD
            "CAD": 0.73,    # 1 CAD ≈ 0.73 USD
            "SGD": 0.74,    # 1 SGD ≈ 0.74 USD
        }
        from_rate = fallback_to_usd.get(from_cur)
        to_rate = fallback_to_usd.get(to_cur)
        if from_rate and to_rate:
            rate = from_rate / to_rate
        else:
            return f"Cannot convert {from_cur} to {to_cur}. Unsupported currency pair."

    converted = amount * rate
    return f"{amount:,.2f} {from_cur} = {converted:,.2f} {to_cur} (rate: {rate:.4f})"


async def _fetch_exchange_rate(from_cur: str, to_cur: str) -> float | None:
    """Fetch live exchange rate from a free API."""
    import httpx

    try:
        url = f"https://api.exchangerate.host/convert?from={from_cur}&to={to_cur}&amount=1"
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                result = data.get("result")
                if result and isinstance(result, (int, float)):
                    logger.info("currency_rate_fetched", from_cur=from_cur, to_cur=to_cur, rate=result)
                    return float(result)
    except Exception:
        logger.warning("currency_api_failed", from_cur=from_cur, to_cur=to_cur)

    return None


async def _update_lead_info(args: dict, lead_id: str, session: AsyncSession) -> str:
    service = LeadService(session)
    update = LeadUpdate(**args)
    await service.update_lead(lead_id, update)
    updated = [k for k in args if args[k] is not None]
    cleared = [k for k in args if args[k] is None]
    parts = []
    if updated:
        parts.append(f"Updated: {', '.join(updated)}")
    if cleared:
        parts.append(f"Cleared: {', '.join(cleared)}")
    return " | ".join(parts) if parts else "No changes made."


async def _update_lead_stage(args: dict, lead_id: str, session: AsyncSession) -> str:
    service = LeadService(session)
    update = LeadUpdate(conversation_stage=args["stage"])
    await service.update_lead(lead_id, update)
    return f"Stage updated to: {args['stage']}"


def _meeting_time(meeting, requested: str) -> str:
    """Show the time in the offset the agent asked for, or in the meeting's timezone."""
    asked = datetime.fromisoformat(requested)
    if asked.tzinfo is not None:
        local = meeting.scheduled_at.astimezone(asked.tzinfo)
        return f"{local:%Y-%m-%d %H:%M} (UTC{local:%z})"
    local = meeting.scheduled_at.astimezone(ZoneInfo(meeting.timezone))
    return f"{local:%Y-%m-%d %H:%M} ({meeting.timezone})"


async def _schedule_meeting(args: dict, lead_id: str, session: AsyncSession) -> str:
    service = MeetingService(session)
    meeting = await service.schedule_meeting(
        lead_id=lead_id,
        scheduled_at=args["scheduled_at"],
        duration=args.get("duration_minutes", 30),
        notes=args.get("notes"),
    )
    return (
        f"Meeting scheduled! 📅\n"
        f"Date: {_meeting_time(meeting, args['scheduled_at'])}\n"
        f"Duration: {meeting.duration_minutes} min\n"
        f"Status: {meeting.status}"
    )


async def _send_email(args: dict) -> str:
    await email_client.send_email(
        to=args["to"],
        subject=args["subject"],
        html_body=args["body"],
    )
    return f"Email sent to {args['to']} with subject: {args['subject']}"


def _transfer_to_human(args: dict) -> str:
    reason = args.get("reason", "Not specified")
    return (
        f"🔄 Transfer requested. Reason: {reason}\n"
        "A member of our team will follow up shortly."
    )
