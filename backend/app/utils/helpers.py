"""
Utility helper functions.

Shared formatters, validators, and convenience functions
used across multiple layers.
"""

import re
from datetime import UTC, datetime


def format_phone_international(phone: str) -> str:
    """Normalize a phone number to digits only. e.g. "+971 50 123 4567" → "971501234567" """
    return re.sub(r"[^\d]", "", phone)


def format_price_aed(amount: float) -> str:
    """Format a price in AED. e.g. 2500000.0 → "AED 2.5M" """
    if amount >= 1_000_000:
        millions = amount / 1_000_000
        if millions == int(millions):
            return f"AED {int(millions)}M"
        return f"AED {millions:.1f}M"
    elif amount >= 1_000:
        return f"AED {amount:,.0f}"
    return f"AED {amount:.2f}"


def format_area_sqft(area: float) -> str:
    """Format area in square feet."""
    return f"{area:,.0f} sq.ft"


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


def is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_uae_phone(phone: str) -> bool:
    """Check if a phone number looks like a UAE number."""
    cleaned = format_phone_international(phone)
    return cleaned.startswith("971") and len(cleaned) >= 12


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis if it exceeds max_length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
