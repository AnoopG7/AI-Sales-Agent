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
        "phone": "14155550132",
        "name": "Jordan Lee",
        "email": "jordan@example.com",
        "status": "new",
        "source": "meta_ads",
        "company": "Brightline Logistics",
        "team_size": 25,
        "product_interest": "sales pipeline and forecasting",
        "budget_min": 500,
        "budget_max": 1_500,
    }


@pytest.fixture
def sample_product_data() -> dict:
    """Sample product data for tests."""
    return {
        "name": "CRM Growth",
        "description": "Pipeline automation and forecasting for growing sales teams",
        "category": "crm",
        "price": 39,
        "billing_period": "monthly",
        "min_seats": 5,
        "max_seats": 100,
        "features": ["custom pipelines", "sales forecasting", "email sequences"],
        "status": "active",
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
                                "display_phone_number": "1XXXXXXXXXX",
                                "phone_number_id": "PHONE_NUMBER_ID",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Jordan"},
                                    "wa_id": "14155550132",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "14155550132",
                                    "id": "wamid.test123",
                                    "timestamp": "1714000000",
                                    "type": "text",
                                    "text": {"body": "Hi, I'd like to know about your CRM plans"},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
