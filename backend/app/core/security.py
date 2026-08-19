"""
Security utilities.

- WhatsApp webhook signature verification (X-Hub-Signature-256)
- JWT token creation and validation for admin auth
- Password hashing
- In-memory token blacklist for logout
"""

import hashlib
import hmac
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

# ─── Password helpers ─────────────────────────────────────────────────────


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ─── JWT helpers ──────────────────────────────────────────────────────────


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token with the given payload."""
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns None if invalid."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


# ─── WhatsApp signature verification ──────────────────────────────────────


def verify_whatsapp_signature(payload: bytes, signature: str) -> bool:
    settings = get_settings()
    if not settings.WHATSAPP_APP_SECRET:
        return not settings.is_production

    expected_signature = hmac.new(
        key=settings.WHATSAPP_APP_SECRET.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    received_hash = signature.removeprefix("sha256=")
    return hmac.compare_digest(expected_signature, received_hash)
