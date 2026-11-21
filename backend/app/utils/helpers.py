"""
Utility helper functions.

Shared formatters, validators, and convenience functions
used across multiple layers.
"""

import re
from datetime import UTC, datetime


def format_phone_international(phone: str) -> str:
    """Normalize a phone number to digits only. e.g. "+1 415 555 0132" → "14155550132" """
    return re.sub(r"[^\d]", "", phone)


def format_price(amount: float, currency: str = "USD") -> str:
    """Format a price with its currency code. e.g. 2500000.0 → "USD 2.5M" """
    if amount >= 1_000_000:
        millions = amount / 1_000_000
        if millions == int(millions):
            return f"{currency} {int(millions)}M"
        return f"{currency} {millions:.1f}M"
    elif amount >= 1_000:
        return f"{currency} {amount:,.0f}"
    return f"{currency} {amount:.2f}"


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


def is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_e164_phone(phone: str) -> bool:
    """Check if a phone number has a plausible international (E.164) length."""
    cleaned = format_phone_international(phone)
    return 8 <= len(cleaned) <= 15


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis if it exceeds max_length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
