"""
Test configuration and shared fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_lead_data() -> dict:
    """Sample lead data for tests."""
    return {
        "phone": "971501234567",
        "name": "Ahmed Al Maktoum",
        "email": "ahmed@example.com",
        "status": "new",
        "source": "meta_ads",
        "budget_min": 1_000_000,
        "budget_max": 3_000_000,
        "preferred_type": "apartment",
        "preferred_location": "Dubai Marina",
        "preferred_bedrooms": 2,
    }


@pytest.fixture
def sample_property_data() -> dict:
    """Sample property data for tests."""
    return {
        "title": "Luxury 2BR Apartment in Dubai Marina",
        "description": "Stunning sea view apartment with modern finishes",
        "type": "apartment",
        "location": "Dubai Marina",
        "price": 2_500_000,
        "bedrooms": 2,
        "bathrooms": 3,
        "area_sqft": 1_450,
        "amenities": ["pool", "gym", "parking", "concierge"],
        "status": "available",
        "featured": True,
    }


@pytest.fixture
def sample_webhook_payload() -> dict:
    """Sample WhatsApp webhook payload from Meta."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "971XXXXXXXXX",
                                "phone_number_id": "PHONE_NUMBER_ID",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Ahmed"},
                                    "wa_id": "971501234567",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "971501234567",
                                    "id": "wamid.test123",
                                    "timestamp": "1714000000",
                                    "type": "text",
                                    "text": {"body": "Hi, I'm interested in properties"},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
