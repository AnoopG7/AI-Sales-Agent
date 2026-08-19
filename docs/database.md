# Database Schema

PostgreSQL 16 running in Docker Compose. SQLAlchemy 2.0 async ORM with asyncpg driver. Alembic for migrations.

## Connection

- **Host**: `localhost:5432`
- **Database**: `leadgen`
- **User**: `postgres`
- **Password**: `postgres`
- **URL**: `postgresql+asyncpg://postgres:postgres@localhost:5432/leadgen`
- **Container**: `leadgen-db` (PostgreSQL 16 Alpine)

## Entity Relationship Diagram

```
+------------------+       +-------------------+
|   ADMIN_USER     |       |      LEADS        |
+------------------+       +-------------------+
| PK id (uuid)     |       | PK id (uuid)      |
| UK email         |<--+   | UK whatsapp_phone |
|    password_hash |   |   |    name           |
|    name          |   |   |    email          |
|    role          |   +---|    assigned_to FK |
|    created_at    |       |    status         |
|    updated_at    |       |    source         |
+------------------+       |    conversation_   |
                           |      stage         |
+------------------+       |    budget_min      |
|   PROPERTIES     |       |    budget_max      |
+------------------+       |    property_type   |
| PK id (uuid)     |       |    bedrooms_min    |
|    title         |       |    location        |
|    description   |       |    notes           |
|    price         |       |    extra_data      |
|    property_type |       |    last_contacted_ |
|    bedrooms      |       |      at            |
|    bathrooms     |       |    created_at      |
|    area_sqft     |       |    updated_at      |
|    location      |       +--------+----------+
|    latitude      |                |
|    longitude     |                | 1
|    amenities     |                |
|    images        |       +--------v----------+
|    featured      |       |  CONVERSATIONS    |
|    status        |       +-------------------+
|    extra_data    |       | PK id (uuid)      |
|    created_at    |       | FK lead_id (CASCADE)
|    updated_at    |       |    role            |
+------------------+       |    content         |
                           |    message_type    |
+------------------+       |    whatsapp_       |
|   SETTINGS       |       |      message_id    |
+------------------+       |    extra_data      |
| PK id (uuid)     |       |    created_at      |
| UK key           |       +-------------------+
|    value         |
|    description   |       +-------------------+
|    updated_at    |       |     MEETINGS       |
+------------------+       +-------------------+
               +---------->| PK id (uuid)      |
               |           | FK lead_id (CASCADE)
               |           |    scheduled_at    |
               |           |    duration_minutes|
               |           |    timezone        |
               |           |    google_event_id |
               |           |    meet_link       |
               |           |    status          |
               |           |    notes           |
               |           |    created_at      |
               |           |    updated_at      |
               |           +-------------------+
               |
+--------------v----+
|  NOTIFICATIONS    |
+-------------------+
| PK id (uuid)      |
| FK lead_id (SETNULL)
|    type           |
|    title          |
|    body           |
|    channel        |
|    read           |
|    extra_data     |
|    created_at     |
+-------------------+

Relationships:
  - LEAD 1 --- * CONVERSATION  (CASCADE delete)
  - LEAD 1 --- * MEETING       (CASCADE delete)
  - LEAD 1 --- * NOTIFICATION  (SET NULL on delete)
  - ADMIN_USER 1 --- * NOTIFICATION
  - * LEAD --- 0..1 ADMIN_USER (assigned_to FK)
```

## Full Table Specifications

### `leads`

Core table — one row per lead (identified by WhatsApp phone number).

```sql
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    whatsapp_phone VARCHAR(20) NOT NULL,
    name VARCHAR,
    email VARCHAR,
    status VARCHAR(30) NOT NULL DEFAULT 'new',
    source VARCHAR(30) NOT NULL DEFAULT 'meta_ads',
    conversation_stage VARCHAR(40) DEFAULT 'greeting',
    budget_min NUMERIC(12, 2),
    budget_max NUMERIC(12, 2),
    property_type VARCHAR,
    bedrooms_min INTEGER,
    location VARCHAR,
    notes TEXT,
    assigned_to VARCHAR,
    extra_data JSONB DEFAULT '{}'::jsonb,
    last_contacted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_leads_whatsapp_phone ON leads (whatsapp_phone);
CREATE INDEX ix_leads_status ON leads (status);
CREATE INDEX ix_leads_source ON leads (source);
CREATE INDEX ix_leads_created_at ON leads (created_at DESC);
```

**Relationships:**
- One-to-many: `conversations` (CASCADE delete)
- One-to-many: `meetings` (CASCADE delete)
- One-to-many: `notifications` (SET NULL on delete)
- Many-to-one: `assigned_to` → `admin_users.id` (optional)

**Status values:** `new`, `contacted`, `qualified`, `meeting_scheduled`, `converted`, `lost`, `spam`

**Source values:** `meta_ads`, `manual`, `referral`, `website`, `other`

**Conversation stage values:** `greeting`, `information_gathering`, `property_search`, `property_presentation`, `scheduling`, `follow_up`, `closed`

### `properties`

Dubai property listings searchable by the AI agent.

```sql
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    price NUMERIC(12, 2) NOT NULL,
    property_type VARCHAR(30) NOT NULL,
    bedrooms INTEGER NOT NULL DEFAULT 0,
    bathrooms INTEGER NOT NULL DEFAULT 0,
    area_sqft FLOAT,
    location VARCHAR(200) NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    amenities JSONB DEFAULT '[]'::jsonb,
    images JSONB DEFAULT '[]'::jsonb,
    featured BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'available',
    extra_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_properties_status ON properties (status);
CREATE INDEX ix_properties_type ON properties (property_type);
CREATE INDEX ix_properties_location ON properties (location);
CREATE INDEX ix_properties_price ON properties (price);
CREATE INDEX ix_properties_featured ON properties (featured DESC);
CREATE INDEX ix_properties_created_at ON properties (created_at DESC);
```

**Property types:** `apartment`, `villa`, `townhouse`, `penthouse`, `studio`

**Status values:** `available`, `sold`, `rented`, `under_offer`, `archived`

**Images format:**
```json
[
  {"url": "https://...", "alt": "Living room", "order": 1},
  {"url": "https://...", "alt": "Bedroom", "order": 2}
]
```

**Amenities format:**
```json
["pool", "gym", "parking", "concierge", "sea_view"]
```

### `conversations`

WhatsApp message history for each lead. Used by the AI agent for context and by the dashboard for display.

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL DEFAULT 'text',
    whatsapp_message_id VARCHAR,
    extra_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_conversations_lead_id ON conversations (lead_id);
CREATE INDEX ix_conversations_lead_created ON conversations (lead_id, created_at);
```

**Role values:** `user`, `assistant`

**Message type:** `text`, `image`, `interactive`, `template`

**Dedup logic:** The `whatsapp_message_id` field stores Meta's unique message ID. Before processing a webhook message, the system checks if this ID already exists in the table. If it does, the message is skipped (idempotency).

### `meetings`

Scheduled property visits or Google Meet calls.

```sql
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 30,
    timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Dubai',
    google_event_id VARCHAR,
    meet_link VARCHAR,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_meetings_lead_id ON meetings (lead_id);
CREATE INDEX ix_meetings_scheduled_at ON meetings (scheduled_at);
```

**Status values:** `scheduled`, `confirmed`, `completed`, `cancelled`, `no_show`

**Scheduling flow (via AI agent):**
1. Agent asks lead for preferred date/time
2. Agent calls `schedule_meeting` tool with ISO 8601 datetime
3. Meeting service creates DB record + (stub) Google Calendar event
4. Agent confirms with the lead

### `admin_users`

Dashboard user accounts. Authentication via JWT (bcrypt password hashing).

```sql
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name VARCHAR,
    role VARCHAR(20) NOT NULL DEFAULT 'admin',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Role values:** `admin`, `agent`

**Password:** bcrypt hash (via `hash_password()` in `core/security.py`)

### `notifications`

Notification log for system events. Currently populated by the AI agent's actions (meeting scheduled, lead qualified, etc.).

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    type VARCHAR(30) NOT NULL,
    title TEXT NOT NULL,
    body TEXT,
    channel VARCHAR(20) NOT NULL DEFAULT 'in_app',
    read BOOLEAN NOT NULL DEFAULT FALSE,
    extra_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_notifications_lead_id ON notifications (lead_id);
CREATE INDEX ix_notifications_read ON notifications (read);
CREATE INDEX ix_notifications_created_at ON notifications (created_at DESC);
```

**Type values:** `new_lead`, `lead_qualified`, `meeting_scheduled`, `escalation`, `system`

**Channel values:** `in_app`, `email`, `whatsapp`, `all`

### `settings`

Key-value store for application configuration.

```sql
CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Enum Values Reference

| Enum | Values |
|------|--------|
| `LeadStatus` | `new`, `contacted`, `qualified`, `meeting_scheduled`, `converted`, `lost`, `spam` |
| `LeadSource` | `meta_ads`, `manual`, `referral`, `website`, `other` |
| `ConversationStage` | `greeting`, `information_gathering`, `property_search`, `property_presentation`, `scheduling`, `follow_up`, `closed` |
| `MeetingStatus` | `scheduled`, `confirmed`, `completed`, `cancelled`, `no_show` |
| `PropertyStatus` | `available`, `sold`, `rented`, `under_offer`, `archived` |
| `PropertyType` | `apartment`, `villa`, `townhouse`, `penthouse`, `studio` |
| `AdminRole` | `admin`, `agent` |
| `NotificationType` | `new_lead`, `lead_qualified`, `meeting_scheduled`, `escalation`, `system` |
| `NotificationChannel` | `in_app`, `email`, `whatsapp`, `all` |

## Index Summary

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| `leads` | `ix_leads_whatsapp_phone` | B-tree (single) | Fast lookup by WhatsApp phone (unique except not enforced in DB, enforced in app) |
| `leads` | `ix_leads_status` | B-tree | Filter leads by status |
| `leads` | `ix_leads_source` | B-tree | Filter leads by source |
| `leads` | `ix_leads_created_at` | B-tree (DESC) | Sort by most recent, pagination |
| `properties` | `ix_properties_status` | B-tree | Filter by availability |
| `properties` | `ix_properties_type` | B-tree | Filter by property type |
| `properties` | `ix_properties_location` | B-tree | Filter by location |
| `properties` | `ix_properties_price` | B-tree | Price range filtering |
| `properties` | `ix_properties_featured` | B-tree (DESC) | Show featured first |
| `properties` | `ix_properties_created_at` | B-tree (DESC) | Sort by newest |
| `conversations` | `ix_conversations_lead_id` | B-tree | Get all messages for a lead |
| `conversations` | `ix_conversations_lead_created` | Composite (lead_id, created_at) | Ordered history retrieval |
| `meetings` | `ix_meetings_lead_id` | B-tree | Get all meetings for a lead |
| `meetings` | `ix_meetings_scheduled_at` | B-tree | Sort by date, upcoming queries |
| `notifications` | `ix_notifications_lead_id` | B-tree | Get notifications for a lead |
| `notifications` | `ix_notifications_read` | B-tree | Filter unread notifications |
| `notifications` | `ix_notifications_created_at` | B-tree (DESC) | Sort by most recent |

## Foreign Key Constraints

| From | To | On Delete | On Update |
|------|-----|-----------|-----------|
| `conversations.lead_id` | `leads.id` | CASCADE | — |
| `meetings.lead_id` | `leads.id` | CASCADE | — |
| `notifications.lead_id` | `leads.id` | SET NULL | — |

## Migration History

| Revision | Date | Description | SQL Changes |
|----------|------|-------------|-------------|
| `5ed85bcb3b71` | 2026-05-09 | Initial schema | Creates all 7 tables (`admin_users`, `leads`, `properties`, `conversations`, `meetings`, `notifications`, `settings`) with all columns, constraints, indexes, and foreign keys |
| `7740dccae86c` | 2026-05-10 | Fix `last_contacted_at` timezone | Alters `leads.last_contacted_at` from `TIMESTAMP` (no timezone) to `TIMESTAMPTZ` (with timezone) |

## Common Query Patterns

### Agent: Search properties by criteria
```python
stmt = select(Property).where(
    Property.status == "available",
    Property.property_type == "apartment",
    Property.price.between(1000000, 2000000),
    Property.bedrooms >= 2,
    Property.location.ilike("%marina%"),
).limit(5)
result = await session.execute(stmt)
properties = result.scalars().all()
```

### Agent: Get lead by phone (create if not found)
```python
stmt = select(Lead).where(Lead.whatsapp_phone == phone)
lead = (await session.execute(stmt)).scalar_one_or_none()
if not lead:
    lead = Lead(whatsapp_phone=phone, source=source)
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
```

### Dashboard: Paginated lead list with filters
```python
query = select(Lead)
if status:
    query = query.where(Lead.status == status)
if search:
    query = query.where(Lead.name.ilike(f"%{search}%"))
total_query = select(func.count()).select_from(query.subquery())
total = (await session.execute(total_query)).scalar()
query = query.order_by(Lead.created_at.desc()).offset(offset).limit(page_size)
result = await session.execute(query)
leads = result.scalars().all()
```

### Analytics: Lead status breakdown
```python
stmt = select(Lead.status, func.count().label("count")).group_by(Lead.status)
result = await session.execute(stmt)
breakdown = result.all()
# Returns: [("new", 15), ("contacted", 8), ("qualified", 5), ...]
```

### Conversation history for agent context
```python
stmt = select(Conversation).where(
    Conversation.lead_id == lead_id
).order_by(Conversation.created_at).limit(40)
result = await session.execute(stmt)
messages = result.scalars().all()
```

### Upcoming meetings (dashboard widget)
```python
stmt = select(Meeting).where(
    Meeting.status.in_(["scheduled", "confirmed"]),
    Meeting.scheduled_at >= utc_now(),
).order_by(Meeting.scheduled_at).limit(5)
result = await session.execute(stmt)
meetings = result.scalars().all()
```
