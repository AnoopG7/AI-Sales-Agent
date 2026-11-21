# Backend — AI Sales Agent API

FastAPI backend for the AI sales agent. It handles inbound WhatsApp conversations with an AI agent that qualifies leads, recommends plans from the product catalog, books demo calls and sends follow-up emails, and exposes a REST API for the admin dashboard.

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

### WhatsApp AI Sales Agent

- **Configurable persona**: `AGENT_NAME`, `COMPANY_NAME` and `DEFAULT_CURRENCY` set who the agent is and what it sells
- **Conversational qualification**: company, team size, use case, budget and timeline, asked one at a time
- **7-stage pipeline**: greeting -> qualification -> discovery -> proposal -> demo_scheduling -> follow_up -> closed
- **9 tools**: search_products, list_all_products, get_product_details, convert_currency, update_lead_info, update_lead_stage, schedule_meeting, send_email, transfer_to_human
- **Multiple tool calls per turn**: all calls from one model response are executed in order and returned in the format OpenAI-compatible APIs expect
- **10 max tool rounds**: Gives room for search, present, update, re-search, schedule without hitting the wall
- **10 message history**: Balances context with token cost. Fewer than 40 to reduce Groq token consumption and stay within free tier limits.
- **Currency conversion**: budgets quoted in other currencies are converted to the catalog currency before searching
- **Smart fallback**: Contextual message after exhausting tool rounds
- **Groq function calling**: Raw implementation (no LangChain/LangGraph), full control over loop
- **Token budget tracking**: Every call logs prompt_tokens + completion_tokens for daily limit monitoring

### REST API (6 Route Groups)

| Module | Endpoints | Features |
|--------|-----------|----------|
| **Auth** | 8 endpoints | Signup, login, me, refresh, logout, change password, reset password request + confirm |
| **Leads** | 7 endpoints | Paginated list with filters (status, source, search), CRUD, conversation history, internal notes |
| **Products** | 6 endpoints | Paginated catalog with search/filters (category, price range, team size, status), CRUD, featured toggle |
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

### Product Catalog

- Sample B2B SaaS catalog seeded by `scripts/seed_products.py` (11 products, 5 categories)
- Search with filters: category, keyword, price range, team size, status
- Seat-range matching: a plan fits a team when `min_seats <= team_size <= max_seats` (no cap if `max_seats` is null)
- Monthly, annual and one-time billing
- Featured toggle for plans the agent should lead with
- Soft delete (archive instead of hard delete)

### Meeting Scheduling

- Agent-initiated scheduling via natural conversation
- ISO 8601 datetime parsing in meeting service
- Upcoming meetings widget (next 5)
- Status tracking: scheduled, confirmed, completed, cancelled, no_show
- Timezone support (default: UTC)
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
| Repository | operation, lead_id, filters | lead_repo.find_by_phone phone=14155550132 found=true |
| Tool execution | tool name, lead_id, args | tool_executing tool=search_products lead_id=abc-123 args={category: "crm", team_size: 25} |
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
| /products | JWT | Product catalog CRUD, search, featured |
| /meetings | JWT | Meeting CRUD, upcoming |
| /analytics | JWT | Dashboard statistics |
| /whatsapp | No (signature-based) | Webhook verification + message processing |

## Setup

Full setup guide at [`docs/setup.md`](../docs/setup.md). Quick reference:

```bash
docker compose up -d        # Start PostgreSQL
uv sync                      # Install dependencies
PYTHONPATH=. .venv/bin/python -m alembic upgrade head   # Migrations
PYTHONPATH=. .venv/bin/python scripts/seed_products.py   # Seed sample catalog
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
- `COMPANY_NAME`, `AGENT_NAME`, `DEFAULT_CURRENCY` — agent persona and catalog currency (defaults: Acme Cloud, Ava, USD)

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
| No LangChain/LangGraph | Raw function calling is simpler, fewer deps, full control over loop and error handling. Orchestrator is under 300 lines. |
| SQLAlchemy async over supabase-py | Full control over database, TCP faster than HTTP/REST, proper Alembic migrations, single Docker container instead of 4. |
| PostgreSQL 16 via Docker | Matches production stack, simple configuration, easy reset/backup. |
| structlog for logging | Machine-parseable JSON in production, colorized in dev. Every layer logs with context. |
| 10 MAX_TOOL_ROUNDS | Room for search -> present -> update -> re-search -> schedule -> email without hitting wall. |
| 10 message history | ~400 tokens for history. Combined with system prompt + tools, stays under 2K tokens. ~50 conversations/day on Groq free tier. |
| Groq over OpenAI | Free 100K TPD vs paid. OpenAI-compatible API = zero migration cost. ~200ms vs ~1s response time. |
| Single configurable persona | Simpler to build/test/maintain than multi-agent. Stage-based prompting gives specialized behavior without complexity. |
| Persona and currency from env vars | The same agent can sell any catalog for any company without code changes. |
| Lazy-init LLMClient | Avoids get_settings() call at module import time. Important for testing and docs generation. |
| exclude_unset=True on updates | Allows explicit null to clear DB columns. Agent uses this when a lead says "budget doesn't matter". |
| Session commit inside repos | Self-contained write operations. Downside: no transactional rollback across multiple repo calls. Acceptable for this app's write patterns. |
| Meeting scheduled_at as string parse | Agent sends ISO 8601 strings, service parses to datetime. Decouples agent from ORM datetime type. |
