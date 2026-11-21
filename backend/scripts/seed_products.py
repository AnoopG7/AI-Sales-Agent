"""
Seed script — populate the products table with a sample B2B SaaS catalog.

The catalog is fictional and only exists so the agent has something to
search and recommend in development. Replace it with your own plans.

Usage:
    cd backend && uv run python scripts/seed_products.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings
from app.models.orm.product import Product

PRODUCTS = [
    # ─── CRM ────────────────────────────────────────────────────────────────
    {
        "name": "CRM Starter",
        "description": "Contact and deal management for small teams getting off spreadsheets.",
        "category": "crm",
        "price": 15,
        "billing_period": "monthly",
        "min_seats": 1,
        "max_seats": 10,
        "features": ["contact management", "deal pipeline", "email sync", "mobile app"],
        "featured": False,
        "status": "active",
    },
    {
        "name": "CRM Growth",
        "description": "Pipeline automation and forecasting for growing sales teams.",
        "category": "crm",
        "price": 39,
        "billing_period": "monthly",
        "min_seats": 5,
        "max_seats": 100,
        "features": ["custom pipelines", "sales forecasting", "workflow automation", "email sequences", "API access"],
        "featured": True,
        "status": "active",
    },
    {
        "name": "CRM Enterprise",
        "description": "Advanced permissions, audit logs and SSO for large sales organisations.",
        "category": "crm",
        "price": 79,
        "billing_period": "monthly",
        "min_seats": 50,
        "max_seats": None,
        "features": ["SSO / SAML", "role-based access", "audit logs", "sandbox environment", "dedicated success manager"],
        "featured": False,
        "status": "active",
    },
    # ─── Analytics ──────────────────────────────────────────────────────────
    {
        "name": "Revenue Analytics",
        "description": "Dashboards for pipeline health, win rates and rep performance.",
        "category": "analytics",
        "price": 25,
        "billing_period": "monthly",
        "min_seats": 3,
        "max_seats": None,
        "features": ["pipeline dashboards", "win/loss analysis", "rep leaderboards", "scheduled reports"],
        "featured": True,
        "status": "active",
    },
    {
        "name": "Analytics Pro (Annual)",
        "description": "Revenue Analytics plus cohort analysis and data warehouse export, billed yearly.",
        "category": "analytics",
        "price": 300,
        "billing_period": "annual",
        "min_seats": 10,
        "max_seats": None,
        "features": ["cohort analysis", "warehouse export", "custom metrics", "priority support"],
        "featured": False,
        "status": "active",
    },
    # ─── Automation ─────────────────────────────────────────────────────────
    {
        "name": "Workflow Automation",
        "description": "No-code workflows that route leads, assign owners and trigger follow-ups.",
        "category": "automation",
        "price": 29,
        "billing_period": "monthly",
        "min_seats": 1,
        "max_seats": 50,
        "features": ["lead routing", "round-robin assignment", "follow-up reminders", "webhooks"],
        "featured": False,
        "status": "active",
    },
    {
        "name": "AI Outreach Assistant",
        "description": "Drafts personalised outreach and summarises calls for every rep.",
        "category": "automation",
        "price": 45,
        "billing_period": "monthly",
        "min_seats": 1,
        "max_seats": None,
        "features": ["AI email drafts", "call summaries", "next-step suggestions"],
        "featured": False,
        "status": "beta",
    },
    # ─── Support ────────────────────────────────────────────────────────────
    {
        "name": "Helpdesk Essentials",
        "description": "Shared inbox and ticketing for customer support teams.",
        "category": "support",
        "price": 12,
        "billing_period": "monthly",
        "min_seats": 1,
        "max_seats": 25,
        "features": ["shared inbox", "ticketing", "canned responses", "SLA tracking"],
        "featured": False,
        "status": "active",
    },
    {
        "name": "Omnichannel Support",
        "description": "Email, chat and WhatsApp support in one queue with a knowledge base.",
        "category": "support",
        "price": 35,
        "billing_period": "monthly",
        "min_seats": 5,
        "max_seats": None,
        "features": ["live chat", "WhatsApp channel", "knowledge base", "CSAT surveys", "SLA tracking"],
        "featured": True,
        "status": "active",
    },
    # ─── Add-ons ────────────────────────────────────────────────────────────
    {
        "name": "Onboarding Package",
        "description": "Guided setup, data migration and team training by our solutions team.",
        "category": "add_on",
        "price": 1500,
        "billing_period": "one_time",
        "min_seats": 1,
        "max_seats": None,
        "features": ["data migration", "workspace setup", "2 training sessions"],
        "featured": False,
        "status": "active",
    },
    {
        "name": "Premium Support",
        "description": "24/7 support with a 1-hour response SLA and a named support engineer.",
        "category": "add_on",
        "price": 10,
        "billing_period": "monthly",
        "min_seats": 10,
        "max_seats": None,
        "features": ["24/7 support", "1-hour SLA", "named support engineer"],
        "featured": False,
        "status": "active",
    },
]


async def seed():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    async with AsyncSession(engine) as session:
        existing = await session.execute(select(Product).limit(1))
        if existing.scalar_one_or_none():
            print("Products already seeded. Skipping.")
            return

        for data in PRODUCTS:
            product = Product(**data)
            session.add(product)
            await session.flush()
            print(f"  Created: {product.name} ({product.id})")

        await session.commit()
        print(f"\n✅ {len(PRODUCTS)} products inserted successfully.")


if __name__ == "__main__":
    print("Seeding products...\n")
    asyncio.run(seed())
