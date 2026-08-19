# Backend Implementation Plan — Phases 4–8

## Current State Assessment

After auditing all 34 backend files, here's what's **real** vs **stub**:

| Layer | File | Status |
|---|---|---|
| `core/config.py` | ✅ Production-ready | All env vars, derived props |
| `core/database.py` | ✅ Working | Singleton Supabase client |
| `core/security.py` | ✅ Working | JWT, bcrypt, webhook sig verification |
| `core/exceptions.py` | ✅ Working | 6 exception types + global handlers |
| `core/logging.py` | ✅ Working | Structlog setup |
| `main.py` | ✅ Working | App factory, CORS, health check |
| `api/v1/router.py` | ⚠️ Empty | All routes commented out |
| `api/v1/deps.py` | ✅ Working | get_db, get_current_user, require_admin |
| `api/v1/endpoints/` | ❌ Empty directory | No endpoint files exist |
| `models/lead.py` | ✅ Working | Pydantic schemas |
| `models/property.py` | ✅ Working | Pydantic schemas |
| `models/meeting.py` | ✅ Working | Pydantic schemas + ConversationMessage |
| `repositories/lead_repo.py` | ✅ Working | Full CRUD + filtering |
| `repositories/property_repo.py` | ❓ Needs review | Likely scaffold |
| `repositories/conversation_repo.py` | ❓ Needs review | Likely scaffold |
| `services/lead_service.py` | ✅ Working | Business logic with repo |
| `services/property_service.py` | ❓ Needs review | Likely scaffold |
| `services/meeting_service.py` | ❓ Needs review | Likely scaffold |
| `integrations/whatsapp.py` | ✅ Functional | send_text + parse_webhook |
| `integrations/openai_client.py` | ✅ Functional | Chat completion with tools |
| `integrations/google_calendar.py` | 🔴 Stub | Returns hardcoded values |
| `integrations/email.py` | 🔴 Stub | Returns hardcoded values |
| `agent/` | ❌ Empty | No files except __init__.py |
| `utils/helpers.py` | ❓ Needs review | |

> [!IMPORTANT]
> **The biggest gap:** There are **zero API endpoints** — the router has everything commented out. No endpoint files exist in `api/v1/endpoints/`. The app boots and serves `/health`, but nothing else.

---

## Proposed Implementation Order

We follow the plan's recommended priority: **Core AI Flow first** (Phase 4 in PLAN.md), because it's the core value proposition. Then CRUD endpoints (Phase 5-6), then notifications (Phase 7-8).

### Phase A: Database Schema + Seed Data
**Why first:** Everything depends on tables existing in Supabase.

#### [NEW] `database/migrations/001_initial_schema.sql`
- All 6 tables from PLAN.md Section 5: `leads`, `conversations`, `properties`, `meetings`, `notifications`, `settings`
- Indexes for performance (status, phone, created_at, etc.)
- CHECK constraints for enums
- Seed data for `settings` table (business hours, agent config)

#### [NEW] `scripts/seed_properties.py`
- Insert 15-20 realistic Dubai properties (various types, locations, price ranges)
- Used for AI agent testing and demo

> [!IMPORTANT]
> **You need a Supabase project set up** with URL and service role key in your `.env` before we can run migrations. Do you have one? If not, I'll create the SQL files and you can run them in the Supabase dashboard SQL editor.

---

### Phase B: CRUD API Endpoints (Leads, Properties, Meetings)
**Why second:** These are the "boring but necessary" routes the dashboard will call.

#### [NEW] `api/v1/endpoints/leads.py`
- `GET /leads` — paginated list with status/source/search filters
- `GET /leads/{id}` — single lead with full details
- `POST /leads` — create lead (manual entry from dashboard)
- `PATCH /leads/{id}` — update lead (status, notes, assigned agent)
- `GET /leads/{id}/conversations` — message history for a lead
- `POST /leads/{id}/notes` — add internal note

#### [NEW] `api/v1/endpoints/properties.py`
- `GET /properties` — paginated list with type/location/price/status filters
- `GET /properties/{id}` — single property
- `POST /properties` — create property
- `PUT /properties/{id}` — update property
- `DELETE /properties/{id}` — soft delete (set status to archived)
- `PATCH /properties/{id}/featured` — toggle featured

#### [NEW] `api/v1/endpoints/meetings.py`
- `GET /meetings` — paginated list with status filter
- `GET /meetings/upcoming` — next 5 upcoming meetings (dashboard widget)
- `POST /meetings` — manually schedule a meeting
- `PATCH /meetings/{id}` — reschedule
- `DELETE /meetings/{id}` — cancel (set status)

#### [NEW] `api/v1/endpoints/analytics.py`
- `GET /analytics/overview` — stat cards (total leads, qualified, meetings, conversion rate)
- `GET /analytics/leads-over-time?days=30` — daily lead counts
- `GET /analytics/status-breakdown` — leads grouped by status
- `GET /analytics/source-breakdown` — leads grouped by source

#### [MODIFY] `api/v1/router.py`
- Uncomment + wire all endpoint routers

#### [NEW/MODIFY] Repositories
- `repositories/property_repo.py` — full CRUD + filtering (match lead_repo pattern)
- `repositories/conversation_repo.py` — create message, get by lead_id, dedup by whatsapp_message_id
- [NEW] `repositories/meeting_repo.py` — CRUD + upcoming query

#### [NEW/MODIFY] Services
- `services/property_service.py` — CRUD + search/filter logic
- `services/meeting_service.py` — scheduling logic, calendar integration
- [NEW] `services/analytics_service.py` — aggregation queries

---

### Phase C: WhatsApp Webhook + AI Agent (THE CORE)
**Why third:** This is the heart of the product — the AI that talks to leads.

#### [NEW] `api/v1/endpoints/whatsapp.py`
- `GET /whatsapp/webhook` — Meta verification handshake (hub.mode, hub.verify_token, hub.challenge)
- `POST /whatsapp/webhook` — inbound message handler:
  1. Verify `X-Hub-Signature-256`
  2. Parse webhook payload
  3. Dedup by `message_id` (check conversations table)
  4. Get or create lead by phone number
  5. Store user message in `conversations`
  6. Call AI agent to process → get response
  7. Send response via WhatsApp
  8. Store assistant message in `conversations`
  9. Return 200 immediately (process in background)

#### [NEW] `agent/prompts.py`
- `SYSTEM_PROMPT` — full "Sarah" persona as defined in PLAN.md Section 6
- Stage-specific instructions embedded
- Guardrails (no hallucinated pricing, escalation rules, etc.)

#### [NEW] `agent/tools.py`
- Tool function definitions for OpenAI function calling:
  - `search_properties` — query DB with budget/type/bedrooms/location
  - `save_lead_info` — update lead with collected data
  - `update_lead_stage` — change conversation stage
  - `schedule_meeting` — create calendar event + meeting record
  - `get_property_details` — single property info
  - `escalate_to_human` — flag for human attention
- Each tool maps to a real function that calls the service layer

#### [NEW] `agent/orchestrator.py`
- `process_message(phone: str, text: str, sender_name: str | None) -> str`
  1. Load conversation history (last 20 messages) from DB
  2. Load lead data
  3. Build messages array: system prompt + history + new message
  4. Call OpenAI with tool definitions
  5. If tool_call → execute tool → append result → call OpenAI again
  6. Loop until final text response (max 3 tool calls per turn)
  7. Return response text
  8. Graceful error handling (fallback "we'll get back to you" message)

---

### Phase D: External Integrations (Calendar, Email, Notifications)

#### [MODIFY] `integrations/google_calendar.py`
- Replace stubs with real Google Calendar API calls
- Service account auth from `GOOGLE_SERVICE_ACCOUNT_JSON` (base64-decoded)
- `create_event()` → real calendar event with Google Meet link
- `cancel_event()`, `check_availability()`

#### [MODIFY] `integrations/email.py`
- Replace stubs with real Resend API calls
- HTML email templates (Jinja2 or simple f-strings):
  - Meeting confirmation (to lead)
  - Meeting notification (to admin/agent)
  - New qualified lead alert

#### [NEW] `services/notification_service.py`
- `notify_meeting_scheduled(lead, meeting)` — sends email + WhatsApp to lead AND admin
- `notify_lead_qualified(lead)` — alerts admin of hot lead

#### [MODIFY] `integrations/whatsapp.py`
- Add `send_interactive_buttons()` for property selection
- Add `send_template_message()` for meeting confirmations
- Add `mark_as_read()` for UX

---

### Phase E: Auth Endpoints

#### [NEW] `api/v1/endpoints/auth.py`
- `POST /auth/login` — email + password → JWT
- `POST /auth/signup` — register admin user
- `GET /auth/me` — current user profile
- `POST /auth/refresh` — refresh token

---

## Open Questions

> [!IMPORTANT]
> **1. Supabase Project** — Do you already have a Supabase project created? I need to know before I start writing migration SQL.

> [!IMPORTANT]
> **2. External API Keys** — Which of these do you have ready?
> - OpenAI API key (for the AI agent)
> - WhatsApp Business API token + phone number (for webhooks)
> - Google Service Account (for Calendar/Meet)
> - Resend API key (for emails)
>
> We can stub the ones you don't have yet and build them incrementally.

> [!WARNING]
> **3. Background Tasks** — The plan mentions Celery + Redis. For MVP, I recommend skipping Celery and using FastAPI's `BackgroundTasks` (built-in). This avoids deploying Redis. We can add Celery later when you need scheduled tasks (meeting reminders). Agree?

> [!IMPORTANT]
> **4. Start with which phase?** — I recommend A → B → C → D → E. Phase A (schema) is the foundation. But if you already have Supabase tables, we skip to B.

---

## Verification Plan

### After Each Phase
- `uv run ruff check app/` — lint passes
- `uv run python -c "from app.main import app"` — app boots
- Manual test via `/docs` Swagger UI (FastAPI auto-generates it)

### Phase B Verification
- Hit every CRUD endpoint via Swagger
- Verify pagination, filters, error responses

### Phase C Verification  
- Send a test webhook payload via curl
- Verify AI responds correctly through the full pipeline
- Check conversation history is stored in DB

### Phase D Verification
- Schedule a real meeting → verify Google Calendar event created
- Send a real email via Resend → verify delivery
