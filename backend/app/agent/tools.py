"""
Groq-compatible function tool definitions + executor functions.

Each tool has:
  - definition: JSON schema for Groq/OpenAI function calling
  - handler: async function that calls the appropriate service layer
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.email import EmailClient
from app.models.lead import LeadUpdate
from app.services.lead_service import LeadService
from app.services.meeting_service import MeetingService
from app.services.property_service import PropertyService

logger = structlog.get_logger()
email_client = EmailClient()

# ─── Tool Definitions (Groq/OpenAI function calling schema) ───────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_properties",
            "description": "Search available Dubai properties by criteria (location, budget in AED, type, bedrooms).",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_type": {
                        "type": "string",
                        "enum": ["apartment", "villa", "townhouse", "penthouse", "studio"],
                        "description": "Type of property",
                    },
                    "location": {
                        "type": "string",
                        "description": "Area or community name in Dubai",
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum budget in AED",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum budget in AED",
                    },
                    "bedrooms": {
                        "type": "integer",
                        "description": "Minimum number of bedrooms",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_all_properties",
            "description": "List all available properties. Use when the lead asks to see everything.",
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
            "name": "get_property_details",
            "description": "Get full details of a specific property by its UUID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "The UUID of the property",
                    },
                },
                "required": ["property_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": (
                "Convert an amount between currencies (e.g. INR to AED). "
                "Use this when a client mentions a budget in a non-AED currency "
                "so you can search properties with the correct AED amount."
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
                        "description": "Source currency code (e.g. INR, USD, GBP)",
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency code (e.g. AED, INR, USD)",
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
                    "email": {"type": "string", "description": "Lead's email address"},
                    "budget_min": {"type": "number", "description": "Minimum budget in AED. Null to clear."},
                    "budget_max": {"type": "number", "description": "Maximum budget in AED. Null to clear."},
                    "property_type": {"type": "string", "description": "Preferred property type"},
                    "bedrooms_min": {"type": "integer", "description": "Minimum bedrooms. Null to clear."},
                    "location": {"type": "string", "description": "Preferred location. Null to clear."},
                    "notes": {"type": "string", "description": "Additional notes"},
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
                            "greeting", "information_gathering", "property_search",
                            "property_presentation", "scheduling", "follow_up", "closed",
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
            "description": "Schedule a property site visit or meeting.",
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
                        "description": "Notes about the meeting or property to visit",
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
            "description": "Send property info or brochure via email to the lead.",
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
            "description": "Transfer to a human team member for complex requests, negotiations, or when asked.",
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
        case "search_properties":
            return await _search_properties(args, session)
        case "list_all_properties":
            return await _list_all_properties(session)
        case "get_property_details":
            return await _get_property_details(args, session)
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


async def _search_properties(args: dict, session: AsyncSession) -> str:
    service = PropertyService(session)
    results = await service.search_properties(
        property_type=args.get("property_type"),
        location=args.get("location"),
        min_price=args.get("min_price"),
        max_price=args.get("max_price"),
        bedrooms=args.get("bedrooms"),
        limit=5,
    )
    if not results:
        return "No properties found matching those criteria."

    lines = [f"Found {len(results)} matching properties:"]
    for p in results:
        beds = f"{p.bedrooms}BR" if p.bedrooms else "Studio"
        lines.append(
            f"- {p.title} | {beds} | AED {p.price:,.0f} | {p.location} | ID: {p.id}"
        )
    return "\n".join(lines)


async def _list_all_properties(session: AsyncSession) -> str:
    service = PropertyService(session)
    results, total = await service.list_properties(page=1, page_size=20, status="available")
    if not results:
        return "No properties available at the moment."

    lines = [f"All available properties ({total} total):"]
    for p in results:
        beds = f"{p.bedrooms}BR" if p.bedrooms else "Studio"
        lines.append(f"- {p.title} | {beds} | AED {p.price:,.0f} | {p.location}")
    return "\n".join(lines)


async def _get_property_details(args: dict, session: AsyncSession) -> str:
    service = PropertyService(session)
    prop = await service.get_property(args["property_id"])
    if not prop:
        return "Property not found."
    area = f"{prop.area_sqft:,.0f}" if isinstance(prop.area_sqft, (int, float)) else "N/A"
    amenities = ", ".join(prop.amenities) if prop.amenities else "N/A"
    return (
        f"🏠 {prop.title}\n"
        f"📍 {prop.location}\n"
        f"💰 AED {prop.price:,.0f}\n"
        f"🛏 {prop.bedrooms}BR | 🛁 {prop.bathrooms}BA | 📐 {area} sq.ft\n"
        f"{'⭐ Featured\n' if prop.featured else ''}"
        f"🏢 Amenities: {amenities}\n"
        f"📝 {prop.description or 'No description'}"
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
        # Fallback to approximate rates (AED as base)
        fallback_to_aed = {
            "INR": 0.044,   # 1 INR ≈ 0.044 AED
            "USD": 3.67,    # 1 USD ≈ 3.67 AED
            "GBP": 4.65,    # 1 GBP ≈ 4.65 AED
            "EUR": 4.00,    # 1 EUR ≈ 4.00 AED
            "AED": 1.0,
        }
        from_rate = fallback_to_aed.get(from_cur)
        to_rate = fallback_to_aed.get(to_cur)
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
        f"Date: {meeting.scheduled_at}\n"
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
