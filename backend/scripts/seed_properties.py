"""
Seed script — Populate properties table with realistic Dubai listings.

Usage:
    cd backend && uv run python scripts/seed_properties.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings
from app.models.orm.property import Property

PROPERTIES = [
    # ─── Dubai Marina — Luxury Apartments ──────────────────────────────────
    {
        "title": "Stunning 1BR with Full Marina View",
        "description": "Floor-to-ceiling windows, modern kitchen, balcony overlooking the marina. Building has gym, pool, concierge.",
        "price": 1_850_000,
        "property_type": "apartment",
        "bedrooms": 1,
        "bathrooms": 2,
        "area_sqft": 950,
        "location": "Dubai Marina",
        "latitude": 25.0800,
        "longitude": 55.1400,
        "amenities": ["pool", "gym", "concierge", "parking", "security"],
        "featured": True,
        "status": "available",
    },
    {
        "title": "Executive 2BR High Floor Marina Walk",
        "description": "Spacious layout with panoramic sea views. Master suite with walk-in closet. Close to tram and metro.",
        "price": 3_200_000,
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 3,
        "area_sqft": 1450,
        "location": "Dubai Marina",
        "latitude": 25.0820,
        "longitude": 55.1420,
        "amenities": ["pool", "gym", "concierge", "parking", "security", "kids_area"],
        "featured": False,
        "status": "available",
    },
    {
        "title": "Premium 3BR Penthouse Marina Skyline",
        "description": "Corner unit with private terrace, upgraded interiors, and direct elevator access. Breathtaking views.",
        "price": 6_500_000,
        "property_type": "penthouse",
        "bedrooms": 3,
        "bathrooms": 4,
        "area_sqft": 2800,
        "location": "Dubai Marina",
        "latitude": 25.0840,
        "longitude": 55.1440,
        "amenities": ["pool", "gym", "concierge", "parking", "private_terrace", "maid_room"],
        "featured": True,
        "status": "available",
    },
    # ─── Downtown Dubai — Burj View Properties ──────────────────────────────
    {
        "title": "Elegant 1BR Apartment Near Burj Khalifa",
        "description": "Modern finish, built-in wardrobes, partial Burj view. Steps from Dubai Mall and fountain.",
        "price": 1_950_000,
        "property_type": "apartment",
        "bedrooms": 1,
        "bathrooms": 2,
        "area_sqft": 880,
        "location": "Downtown Dubai",
        "latitude": 25.1950,
        "longitude": 55.2750,
        "amenities": ["pool", "gym", "concierge", "parking", "retail_access"],
        "featured": False,
        "status": "available",
    },
    {
        "title": "Luxurious 2BR with Full Burj View",
        "description": "Rare find — unobstructed Burj Khalifa view from every room. High-end finishes, spacious balcony.",
        "price": 4_500_000,
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 3,
        "area_sqft": 1600,
        "location": "Downtown Dubai",
        "latitude": 25.1970,
        "longitude": 55.2770,
        "amenities": ["pool", "gym", "concierge", "parking", "valet", "spa"],
        "featured": True,
        "status": "available",
    },
    {
        "title": "Grand 4BR Penthouse Opera District",
        "description": "Dual-level penthouse with private pool, panoramic skyline views, and premium Italian marble throughout.",
        "price": 15_000_000,
        "property_type": "penthouse",
        "bedrooms": 4,
        "bathrooms": 5,
        "area_sqft": 4500,
        "location": "Downtown Dubai",
        "latitude": 25.1930,
        "longitude": 55.2790,
        "amenities": ["private_pool", "gym", "concierge", "private_terrace", "maid_room", "driver_room"],
        "featured": True,
        "status": "available",
    },
    # ─── Palm Jumeirah — Exclusive Villas ───────────────────────────────────
    {
        "title": "4BR Beachfront Villa Palm Jumeirah",
        "description": "Private beach access, landscaped garden, and stunning Arabian Gulf views. Modern Arabic architecture.",
        "price": 22_000_000,
        "property_type": "villa",
        "bedrooms": 4,
        "bathrooms": 5,
        "area_sqft": 5200,
        "location": "Palm Jumeirah",
        "latitude": 25.1100,
        "longitude": 55.1350,
        "amenities": ["private_beach", "pool", "garden", "parking", "maid_room", "driver_room"],
        "featured": False,
        "status": "available",
    },
    {
        "title": "5BR Signature Villa Frond G",
        "description": "Brand new, never lived in. Smart home system, infinity pool, direct beach access. Full sea view.",
        "price": 35_000_000,
        "property_type": "villa",
        "bedrooms": 5,
        "bathrooms": 6,
        "area_sqft": 6800,
        "location": "Palm Jumeirah",
        "latitude": 25.1150,
        "longitude": 55.1380,
        "amenities": ["private_beach", "infinity_pool", "garden", "smart_home", "maid_room", "driver_room"],
        "featured": True,
        "status": "under_offer",
    },
    # ─── Arabian Ranches — Family Villas ────────────────────────────────────
    {
        "title": "3BR Townhouse Arabian Ranches II",
        "description": "Corner unit with large garden, open-plan living, and community pool access. Perfect for families.",
        "price": 2_400_000,
        "property_type": "townhouse",
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 2200,
        "location": "Arabian Ranches",
        "latitude": 25.0700,
        "longitude": 55.2900,
        "amenities": ["community_pool", "park", "parking", "kids_play_area"],
        "featured": False,
        "status": "available",
    },
    {
        "title": "4BR Standalone Villa Arabian Ranches I",
        "description": "Golf course view, private pool, modern layout with majlis. Gated community with 24/7 security.",
        "price": 4_800_000,
        "property_type": "villa",
        "bedrooms": 4,
        "bathrooms": 4,
        "area_sqft": 3500,
        "location": "Arabian Ranches",
        "latitude": 25.0730,
        "longitude": 55.2930,
        "amenities": ["private_pool", "garden", "golf_view", "parking", "maid_room"],
        "featured": False,
        "status": "available",
    },
    # ─── Dubai Hills Estate ─────────────────────────────────────────────────
    {
        "title": "2BR Apartment Dubai Hills Grove",
        "description": "Park-facing unit with premium finishes. Access to Dubai Hills Mall and golf course.",
        "price": 2_800_000,
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1250,
        "location": "Dubai Hills Estate",
        "latitude": 25.0600,
        "longitude": 55.2400,
        "amenities": ["pool", "gym", "parking", "park_access", "retail_access"],
        "featured": False,
        "status": "available",
    },
    {
        "title": "5BR Golf Course Villa Dubai Hills",
        "description": "Brand new contemporary villa overlooking the 18th fairway. Open-plan, rooftop terrace, private elevator.",
        "price": 12_500_000,
        "property_type": "villa",
        "bedrooms": 5,
        "bathrooms": 6,
        "area_sqft": 5800,
        "location": "Dubai Hills Estate",
        "latitude": 25.0630,
        "longitude": 55.2430,
        "amenities": ["private_pool", "garden", "golf_view", "roof_terrace", "elevator", "maid_room"],
        "featured": True,
        "status": "available",
    },
    # ─── JVC — Affordable Options ───────────────────────────────────────────
    {
        "title": "Studio Apartment JVC",
        "description": "Smart layout, fully fitted kitchen, built-in storage. Great first home or investment.",
        "price": 520_000,
        "property_type": "apartment",
        "bedrooms": 0,
        "bathrooms": 1,
        "area_sqft": 420,
        "location": "Jumeirah Village Circle",
        "latitude": 25.0400,
        "longitude": 55.2200,
        "amenities": ["pool", "gym", "parking"],
        "featured": False,
        "status": "available",
    },
    {
        "title": "1BR Apartment JVC With Balcony",
        "description": "Spacious 1BR with large balcony and community view. Ready to move in. Low service charges.",
        "price": 780_000,
        "property_type": "apartment",
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqft": 680,
        "location": "Jumeirah Village Circle",
        "latitude": 25.0430,
        "longitude": 55.2230,
        "amenities": ["pool", "gym", "parking", "kids_area"],
        "featured": False,
        "status": "available",
    },
    # ─── Business Bay — Investment Hub ──────────────────────────────────────
    {
        "title": "1BR Modern Apartment Business Bay",
        "description": "Canal view, high floor, neutral decor. Walking distance to Dubai Mall. Ideal for professionals.",
        "price": 1_400_000,
        "property_type": "apartment",
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqft": 780,
        "location": "Business Bay",
        "latitude": 25.1870,
        "longitude": 55.2580,
        "amenities": ["pool", "gym", "concierge", "parking", "canal_view"],
        "featured": False,
        "status": "available",
    },
    {
        "title": "2BR Canal View Executive Apartment",
        "description": "Premium unit with water view, built-in wardrobes, and premium appliances. Close to restaurants and metro.",
        "price": 2_600_000,
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1300,
        "location": "Business Bay",
        "latitude": 25.1890,
        "longitude": 55.2600,
        "amenities": ["pool", "gym", "concierge", "parking", "canal_view", "retail_access"],
        "featured": False,
        "status": "available",
    },
    # ─── Dubai Creek Harbour ────────────────────────────────────────────────
    {
        "title": "1BR with Creek View Dubai Creek Harbour",
        "description": "Brand new community with stunning creek and skyline views. Near Ras Al Khor wildlife sanctuary.",
        "price": 1_650_000,
        "property_type": "apartment",
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqft": 850,
        "location": "Dubai Creek Harbour",
        "latitude": 25.2100,
        "longitude": 55.3250,
        "amenities": ["pool", "gym", "parking", "park_access"],
        "featured": False,
        "status": "available",
    },
    {
        "title": "3BR Family Apartment Creek Harbour",
        "description": "Spacious 3BR with dual balcony, waterfront promenade access. Top-rated school district nearby.",
        "price": 3_900_000,
        "property_type": "apartment",
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 1900,
        "location": "Dubai Creek Harbour",
        "latitude": 25.2130,
        "longitude": 55.3280,
        "amenities": ["pool", "gym", "kids_area", "parking", "waterfront_access"],
        "featured": False,
        "status": "available",
    },
    # ─── Investment / Off-Plan ──────────────────────────────────────────────
    {
        "title": "Studio Off-Plan — Emaar Riverside",
        "description": "Payment plan available. Handover 2027. Prime location in Emaar's newest Dubai South community.",
        "price": 620_000,
        "property_type": "apartment",
        "bedrooms": 0,
        "bathrooms": 1,
        "area_sqft": 400,
        "location": "Dubai South",
        "latitude": 24.9700,
        "longitude": 55.1500,
        "amenities": ["pool", "gym", "parking"],
        "featured": False,
        "status": "available",
    },
    {
        "title": "1BR Off-Plan — Sobha Hartland II",
        "description": "Premium off-plan from Sobha. Expected ROI 8-10%. Near Mohammed Bin Rashid City.",
        "price": 1_200_000,
        "property_type": "apartment",
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqft": 720,
        "location": "Mohammed Bin Rashid City",
        "latitude": 25.1700,
        "longitude": 55.3100,
        "amenities": ["pool", "gym", "parking", "park_access"],
        "featured": False,
        "status": "available",
    },
]


async def seed():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    async with AsyncSession(engine) as session:
        existing = await session.execute(select(Property).limit(1))
        if existing.scalar_one_or_none():
            print("Properties already seeded. Skipping.")
            return

        for prop_data in PROPERTIES:
            prop = Property(**prop_data)
            session.add(prop)
            await session.flush()
            print(f"  Created: {prop.title} ({prop.id})")

        await session.commit()
        print(f"\n✅ {len(PROPERTIES)} properties inserted successfully.")


if __name__ == "__main__":
    print("Seeding properties...\n")
    asyncio.run(seed())
