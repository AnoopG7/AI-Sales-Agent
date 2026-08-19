# Backend — LeadGen API

FastAPI backend for the LeadGen lead generation platform. Manages WhatsApp conversations via an AI agent that qualifies leads, searches properties, schedules meetings, and sends email notifications — all through natural conversation. Built for Indian buyers and NRIs investing in Dubai real estate.

## Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.12+ | Modern async/await, pattern matching, type hints |
| Web Framework | FastAPI | 0.115+ | Async REST, auto OpenAPI/Swagger, Pydantic integration |
| ASGI Server | uvicorn | 0.34+ | With standard extras for performance |
| Database Driver | asyncpg | 0.30+ | Native PostgreSQL async protocol |
| ORM | SQLAlchemy | 2.0+ | Async Mapped style, select() queries |
| Migrations | Alembic | 1.14+ | Auto-generated from ORM metadata |
| AI Model | Groq | llama-3.3-70b-versatile | Function calling, 100K TPD free tier |
| AI SDK | groq | 1.2+ | OpenAI-compatible API |
| Auth | python-jose + bcrypt | — | JWT (HS256, 24h access, 7d refresh) |
| WhatsApp | Meta Cloud API | v23.0 | REST API via httpx |
| Email | stdlib smtplib | — | STARTTLS SMTP (dev: console log) |
| Calendar | google-api-python-client | 2.160+ | Stub (returns hardcoded values) |
| Logging | structlog | 24.0+ | Structured JSON, easy production parsing |
| Linting | ruff | 0.11+ | E, F, I, W, UP, B rules (line-length 100) |
| Type Checking | mypy | 1.15+ | Strict mode |
| Testing | pytest + pytest-asyncio | — | Async test support |
| Package Manager | uv | — | Fast dependency resolution and install |

## Features

### WhatsApp AI Agent (Sarah)

- **Natural conversation**: Sarah greets leads, understands Hinglish, asks about preferences conversationally
- **7-stage pipeline**: greeting -> information_gathering -> property_search -> property_presentation -> scheduling -> follow_up -> closed
- **8 tools**: search_properties, list_all_properties, get_property_details, update_lead_info, update_lead_stage, schedule_meeting, send_email, transfer_to_human
- **Parallel tool execution**: Multiple tool calls in one response are executed in parallel
- **10 max tool rounds**: Gives room for search, present, update, re-search, schedule without hitting the wall
- **10 message history**: Balances context with token cost. Fewer than 40 to reduce Groq token consumption and stay within free tier limits.
- **Dual currency display**: AED + INR with lakh/crore notation for Indian buyers
- **Smart fallback**: Contextual message after exhausting tool rounds
- **Groq function calling**: Raw implementation (no LangChain/LangGraph), full control over loop
- **Token budget tracking**: Every call logs prompt_tokens + completion_tokens for daily limit monitoring

### REST API (6 Route Groups)

| Module | Endpoints | Features |
|--------|-----------|----------|
| **Auth** | 8 endpoints | Signup, login, me, refresh, logout, change password, reset password request + confirm |
| **Leads** | 7 endpoints | Paginated list with filters (status, source, search), CRUD, conversation history, internal notes |
| **Properties** | 6 endpoints | Paginated list with search/filters (type, location, price range, bedrooms, status), CRUD, featured toggle |
| **Meetings** | 6 endpoints | Paginated list, upcoming, CRUD schedule/cancel |
| **Analytics** | 4 endpoints | Overview stats, leads over time, status breakdown, source breakdown |
| **WhatsApp** | 2 endpoints | GET verification handshake + POST inbound message processor |

### WhatsApp Webhook (Full Pipeline)

See [`docs/architecture.md`](../docs/architecture.md#flow-1-whatsapp-message-processing-inbound) for the complete webhook flow diagram. The pipeline covers signature verification → payload parsing → dedup → lead auto-creation → AI agent → reply → persistence.

### Lead Management

- Auto-creation from WhatsApp (phone, source, timestamp)
- `exclude_unset=True` on updates — explicit null clears DB columns (used when lead says "no budget")
- Conversation history linked to lead with CASCADE delete
- Internal notes for human agents
- Status pipeline: new -> contacted -> qualified -> meeting_scheduled -> converted -> lost -> spam
- Source tracking: meta_ads, manual, referral, website, other

### Property Management

- 20 seeded Dubai properties across all types and price ranges (550K AED to 25M AED)
- Search with filters: type, location, price range, bedrooms, status
- Featured toggle for priority listings
- Soft delete (archive instead of hard delete)
- Images stored as JSON array (URL, alt text, order)

### Meeting Scheduling

- Agent-initiated scheduling via natural conversation
- ISO 8601 datetime parsing in meeting service
- Upcoming meetings widget (next 5)
- Status tracking: scheduled, confirmed, completed, cancelled, no_show
- Timezone support (default: Asia/Dubai)
- Google Calendar stub (placeholder for real integration)

### Analytics Dashboard

- Overview: total leads, qualified, upcoming meetings, converted, conversion rate
- Leads over time: daily counts for last N days
- Status breakdown: count + percentage per status
- Source breakdown: count + percentage per source

### Authentication & Security

- bcrypt password hashing (not passlib)
- JWT tokens: 24h access token, 7d refresh token, 15min reset token
- Password reset flow (request + confirm with token)
- WhatsApp webhook HMAC-SHA256 signature verification
- Dev mode: skip signature verification when APP_SECRET is empty
- CORS: allow all in dev, restrict to FRONTEND_URL in production

### Logging (structlog)

Every layer logs with structured context:

| Layer | Context | Example |
|-------|---------|---------|
| HTTP request | method, path, status, duration_ms | api_request method=POST path=/api/v1/whatsapp/webhook status=200 duration_ms=450 |
| Repository | operation, lead_id, filters | lead_repo.find_by_phone phone=+971501234567 found=true |
| Tool execution | tool name, lead_id, args | tool_search_properties lead_id=abc-123 filters={location: "Marina"} |
| LLM API | provider, model, tokens, tool_calls, finish_reason | llm_completion provider=groq model=llama... prompt_tokens=3100 completion_tokens=200 tool_calls=2 |
| Agent round | round number, tool count, has_content | agent_round round=2 tool_count=1 has_content=false |

## API

- Base URL: `http://localhost:8000/api/v1`
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`
- Health: `GET /health`

### Route Summary

6 route groups — see [`docs/api-reference.md`](../docs/api-reference.md) for every endpoint with full request/response JSON.

| Prefix | Auth Required | Purpose |
|--------|---------------|---------|
| /auth | No (except /me) | User registration, login, password management |
| /leads | JWT | Lead CRUD, conversation history, notes |
| /properties | JWT | Property CRUD, search, featured |
| /meetings | JWT | Meeting CRUD, upcoming |
| /analytics | JWT | Dashboard statistics |
| /whatsapp | No (signature-based) | Webhook verification + message processing |

## Setup

Full setup guide at [`docs/setup.md`](../docs/setup.md). Quick reference:

```bash
docker compose up -d        # Start PostgreSQL
uv sync                      # Install dependencies
PYTHONPATH=. .venv/bin/python -m alembic upgrade head   # Migrations
PYTHONPATH=. .venv/bin/python scripts/seed_properties.py # Seed 20 properties
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Start
```

### Environment Variables

**Required for core operation:**
- `GROQ_API_KEY` — Get from console.groq.com

**Required for auth:**
- `SECRET_KEY` — JWT signing key (min 32 characters in production)

**Dev defaults (can leave as-is):**
- `DATABASE_URL` — postgresql+asyncpg://postgres:postgres@localhost:5432/leadgen
- `WHATSAPP_APP_SECRET` — set to "" to skip signature verification
- `SMTP_HOST/USER/PASS` — leave empty to log emails to console
- `GOOGLE_SERVICE_ACCOUNT_JSON` — leave empty (Calendar is stubbed)

### Lint and Type Check

```bash
uv run ruff check app/
uv run mypy app/
```

## Agent CLI (WhatsApp Simulator)

```bash
PYTHONPATH=. .venv/bin/python scripts/agent_cli.py
```

Commands: list, select N, new +phone, say message, history, state, help, quit

Each say command: stores user message -> calls process_message() -> stores assistant response -> displays result + lead state.

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| No LangChain/LangGraph | Raw function calling is simpler, fewer deps, full control over loop and error handling. Orchestrator is ~200 lines. |
| SQLAlchemy async over supabase-py | Full control over database, TCP faster than HTTP/REST, proper Alembic migrations, single Docker container instead of 4. |
| PostgreSQL 16 via Docker | Matches production stack, simple configuration, easy reset/backup. |
| structlog for logging | Machine-parseable JSON in production, colorized in dev. Every layer logs with context. |
| 10 MAX_TOOL_ROUNDS | Room for search -> present -> update -> re-search -> schedule -> email without hitting wall. |
| 10 message history | ~400 tokens for history. Combined with system prompt + tools, stays under 2K tokens. ~50 conversations/day on Groq free tier. |
| Groq over OpenAI | Free 100K TPD vs paid. OpenAI-compatible API = zero migration cost. ~200ms vs ~1s response time. |
| Single Sarah persona | Simpler to build/test/maintain than multi-agent. Stage-based prompting gives specialized behavior without complexity. |
| INR + AED dual pricing | Target audience thinks in INR (lakh/crore) but Dubai real estate is priced in AED. Eliminates mental math. |
| Lazy-init LLMClient | Avoids get_settings() call at module import time. Important for testing and docs generation. |
| exclude_unset=True on updates | Allows explicit null to clear DB columns. Agent uses this when lead says "no budget". |
| Session commit inside repos | Self-contained write operations. Downside: no transactional rollback across multiple repo calls. Acceptable for this app's write patterns. |
| Meeting scheduled_at as string parse | Agent sends ISO 8601 strings, service parses to datetime. Decouples agent from ORM datetime type. |
