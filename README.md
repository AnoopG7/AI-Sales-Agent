# AI Sales Agent

A WhatsApp AI sales agent for B2B and B2C teams. Inbound leads (for example from Meta ads) message the business on WhatsApp, and the agent replies instantly: it qualifies the lead (company, team size, use case, budget, timeline), recommends the right plan from the product catalog, books a demo call, emails a summary, and hands off to a human rep for custom pricing or contracts. An admin dashboard manages leads, the catalog and meetings, with analytics.

The agent's name, company and catalog currency are set with environment variables, so the same system can sell any product.

## How It Works

```
WhatsApp message ──> Meta webhook ──> verify HMAC signature ──> dedup by message ID
                                                                       │
                     lead auto-created on first message <──────────────┘
                                                                       │
                     agent loop (Groq / Ollama, 9 tools, max 10 rounds) ┘
                       ├─ search_products / get_product_details / list_all_products
                       ├─ update_lead_info / update_lead_stage   ──> system prompt rebuilt with fresh lead data
                       ├─ schedule_meeting / send_email / convert_currency
                       └─ transfer_to_human
                                                                       │
                     reply sent on WhatsApp, both messages stored <────┘
```

Each lead moves through 7 stages: `greeting → qualification → discovery → proposal → demo_scheduling → follow_up → closed`.

## Design Decisions

| Decision | Why |
|----------|-----|
| Raw function calling instead of LangChain/LangGraph | The whole loop is one ~170-line function; every message, tool call and retry is visible and debuggable |
| Rebuild the system prompt after state-changing tools | Otherwise the model keeps the lead profile from the start of the turn and re-asks questions it just saved the answers to |
| Cap at 10 tool rounds and 10 history messages | Bounds the worst-case token cost per inbound message on free-tier rate limits; a final tools-disabled call guarantees a reply |
| Retry with backoff on 429 | Groq's free tier rate-limits bursts; a short backoff recovers most of them without failing the conversation |
| HMAC verification + message-ID dedup on the webhook | Rejects forged requests, and Meta retries deliveries, so the same message must not be processed twice |
| Catalog data only through tools | The prompt forbids inventing prices or features; everything the agent quotes comes from the database |
| One OpenAI-compatible client for Groq and Ollama | Switch between hosted and local models with one env var |

**Start here, then navigate to the appropriate doc:**
- [`backend/README.md`](backend/README.md) — Backend stack, features, architecture decisions
- [`frontend/README.md`](frontend/README.md) — Frontend stack, components, forms, stores
- [`docs/`](docs/) — Architecture, database, API reference, AI agent, setup, roadmap

## Tech Stack

| Layer | Technology | Version/Purpose |
|-------|-----------|-----------------|
| **Backend Runtime** | Python 3.12+ | Modern async runtime |
| **Web Framework** | FastAPI | Async REST framework with auto-docs |
| **Database** | PostgreSQL 16 | Docker container, port 5432 |
| **ORM** | SQLAlchemy 2.0 | Async ORM with asyncpg driver |
| **Migrations** | Alembic | Auto-generated from ORM models |
| **AI Model** | Groq (`openai/gpt-oss-120b`) | Free tier, fast inference with tool calling |
| **AI Integration** | Groq Python SDK (OpenAI-compatible) | Function/tool calling |
| **Auth** | python-jose + bcrypt | JWT (HS256, 24h expiry), bcrypt password hashing |
| **WhatsApp** | Meta Cloud API v23.0 | Inbound webhook + outbound messaging |
| **Email** | stdlib smtplib + STARTTLS | SMTP (Brevo/Gmail/etc.), logs to console in dev |
| **Calendar** | Google Calendar API | Stub (returns hardcoded values) |
| **Logging** | structlog | Structured JSON logging |
| **Package Manager** | `uv` | Fast Python package manager |
| **Containerization** | Docker Compose | PostgreSQL 16 Alpine container |
| **Frontend Framework** | React 19 + Vite 8 | Modern SPA with HMR |
| **Language** | TypeScript 6 | Full type safety |
| **Styling** | Tailwind CSS v4 | Utility-first, OKLCH color space |
| **UI Library** | shadcn/ui | Radix-based, customizable primitives |
| **State Management** | Zustand | Lightweight, hook-based stores |
| **Forms** | React Hook Form + Zod | Performant forms with schema validation |
| **API Client** | Axios + TanStack Query | Request interceptors, caching, mutations |
| **Charts** | Recharts | Composable React charting |
| **Notifications** | Sonner | Toast notifications |

## Full Directory Structure

```
AI-LeadGen/
├── README.md                         # This file
├── .gitignore
│
├── backend/
│   ├── README.md
│   ├── .env.example                  # All 25+ env vars documented
│   ├── pyproject.toml                # Dependencies, ruff, mypy, pytest config
│   ├── uv.lock                       # Locked dependency versions
│   ├── docker-compose.yml            # PostgreSQL 16 Alpine
│   ├── alembic.ini                   # Alembic config (URL loaded dynamically)
│   ├── alembic/
│   │   ├── env.py                    # Async Alembic environment
│   │   ├── script.py.mako            # Migration template
│   │   └── versions/
│   │       ├── 5ed85bcb3b71_initial_schema.py
│   │       └── 7740dccae86c_fix_last_contacted_at_timezone.py
│   ├── scripts/
│   │   ├── agent_cli.py              # WhatsApp simulator CLI
│   │   └── seed_products.py          # Seed a sample B2B SaaS catalog
│   ├── tests/
│   │   ├── conftest.py               # Sample data fixtures
│   │   ├── agent/
│   │   ├── api/
│   │   └── services/
│   └── app/
│       ├── __init__.py
│       ├── main.py                   # Application factory, lifecycle, middleware
│       ├── agent/                    # AI agent
│       │   ├── orchestrator.py       # process_message() loop
│       │   ├── prompts.py            # System prompt, stage instructions, guardrails
│       │   └── tools.py              # 9 tool definitions + handlers
│       ├── api/v1/                   # REST API
│       │   ├── router.py             # Route aggregation (6 routers)
│       │   ├── deps.py               # get_db, get_current_user, require_admin
│       │   └── endpoints/
│       │       ├── auth.py           # 8 auth endpoints
│       │       ├── leads.py          # 7 lead endpoints
│       │       ├── products.py       # 6 product catalog endpoints
│       │       ├── meetings.py       # 6 meeting endpoints
│       │       ├── analytics.py      # 4 analytics endpoints
│       │       └── whatsapp.py       # GET (verify) + POST (process webhook)
│       ├── core/                     # Cross-cutting infrastructure
│       │   ├── config.py             # pydantic-settings (all env vars)
│       │   ├── database.py           # AsyncEngine + async_sessionmaker
│       │   ├── enums.py              # 10 StrEnum classes
│       │   ├── exceptions.py         # 6 custom exceptions + handlers
│       │   ├── logging.py            # structlog configuration
│       │   └── security.py           # bcrypt hash/verify, JWT create/decode
│       ├── integrations/             # External service clients
│   │   ├── llm_client.py         # OpenAI-compatible (Groq/Ollama)
│       │   ├── whatsapp.py           # send_text, parse_webhook, verify
│       │   ├── email.py              # SMTP (dev: logs to console)
│       │   └── google_calendar.py    # Stub (hardcoded responses)
│       ├── models/                   # Pydantic schemas
│       │   ├── lead.py               # LeadBase, LeadCreate, LeadUpdate, LeadResponse
│       │   ├── product.py            # ProductBase, ProductCreate, ProductUpdate, ProductResponse
│       │   ├── meeting.py            # MeetingCreate, MeetingUpdate, MeetingResponse, ConversationMessage
│       │   ├── auth.py               # LoginRequest, SignupRequest, TokenResponse, etc.
│       │   ├── admin.py              # AdminUserCreate, AdminUserResponse, etc.
│       │   ├── common.py             # PaginationParams, PaginatedResponse
│       │   └── orm/                  # SQLAlchemy ORM models
│       │       ├── base.py           # DeclarativeBase
│       │       ├── lead.py           # Lead model
│       │       ├── product.py        # Product model
│       │       ├── conversation.py   # Conversation model
│       │       ├── meeting.py        # Meeting model
│       │       ├── admin_user.py     # AdminUser model
│       │       ├── notification.py   # Notification model
│       │       └── setting.py        # Setting model
│       ├── repositories/            # Data access layer
│       │   ├── lead_repo.py          # find_by_phone, find_by_id, list_all, create, update, delete
│       │   ├── product_repo.py       # find_by_id, search, list_all, create, update, delete
│       │   ├── conversation_repo.py  # get_history, add_message, message_exists
│       │   ├── admin_user_repo.py    # find_by_email, find_by_id, create, update_password, update
│       │   └── meeting_repo.py       # find_by_id, list_all, get_upcoming, create, update
│       ├── services/                # Business logic
│       │   ├── lead_service.py       # get_or_create_by_phone, create, update, get, list
│       │   ├── product_service.py    # search, get, list, create, update
│       │   ├── meeting_service.py    # schedule, get, list, upcoming, update
│       │   ├── auth_service.py       # signup, login, refresh, change_password, reset
│       │   └── analytics_service.py  # overview, leads_over_time, status/source breakdown
│       └── utils/
│           └── helpers.py            # format_phone, format_price, utc_now, validators
│
├── frontend/
│   ├── README.md
│   ├── package.json                 # All JS dependencies
│   ├── vite.config.ts               # Vite + React + Tailwind + proxy config
│   ├── tsconfig.json                # TypeScript configuration
│   ├── tsconfig.app.json            # App-specific TS config
│   ├── tsconfig.node.json           # Node-specific TS config
│   ├── eslint.config.js             # ESLint flat config
│   ├── components.json              # shadcn/ui config
│   ├── index.html                   # Entry point with SEO/OG meta tags
│   └── src/
│       ├── main.tsx                  # BrowserRouter + QueryClientProvider
│       ├── App.tsx                   # ThemeProvider + TooltipProvider + Toaster + Router
│       ├── router.tsx                # Routes (lazy-loaded)
│       ├── index.css                 # Tailwind v4 + OKLCH theme + custom utilities
│       ├── components/
│       │   ├── ui/                   # 25 shadcn/ui primitives
│       │   ├── layout/               # AppShell, Sidebar, Header, MobileNav, ThemeSwitcher
│       │   ├── shared/               # DataTable, PageHeader, StatusBadge, etc.
│       │   ├── forms/                # LeadForm, ProductForm, MeetingForm, LoginForm, SettingsForm
│       │   └── auth/                 # ProtectedRoute
│       ├── layouts/
│       │   ├── auth-layout.tsx
│       │   └── dashboard-layout.tsx
│       ├── stores/                   # authStore, filterStore, sidebarStore
│       ├── services/api.ts           # Axios instance with interceptors
│       ├── schemas/validators.ts     # Zod schemas for all forms
│       ├── types/index.ts            # TypeScript interfaces
│       ├── config/constants.ts       # Statuses, categories, billing periods, nav items
│       └── pages/
│           └── homepage.tsx          # All components showcase
│
└── docs/
    ├── architecture.md               # System context, data flow, component layers
    ├── database.md                   # ERD, 7 table schemas, indexes, migrations
    ├── api-reference.md              # All REST endpoints with request/response
    ├── agent.md                      # Persona, tools, orchestrator, token usage
    ├── setup.md                      # Step-by-step guide, env vars, troubleshooting
    └── roadmap.md                    # Current state and planned work
```

## Quick Start

```bash
# 1. Start PostgreSQL
cd backend
docker compose up -d

# 2. Install backend dependencies
uv sync

# 3. Run migrations and seed data
PYTHONPATH=. .venv/bin/python -m alembic upgrade head
PYTHONPATH=. .venv/bin/python scripts/seed_products.py

# 4. Start backend server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Start frontend (separate terminal)
cd frontend
npm install
npm run dev
```

- Backend: `http://localhost:8000` (Swagger UI at `/docs`)
- Frontend: `http://localhost:5173`
- API proxy: Vite proxies `/api` → `localhost:8000`

## Documentation

| File | What it covers |
|------|---------------|
| [`backend/README.md`](backend/README.md) | Backend stack, features, architecture decisions |
| [`frontend/README.md`](frontend/README.md) | Frontend stack, components, forms, stores |
| [`docs/architecture.md`](docs/architecture.md) | System context, WhatsApp webhook lifecycle, AI agent loop, component layers |
| [`docs/database.md`](docs/database.md) | Mermaid ERD, 7 tables with full column specs, all indexes, migrations |
| [`docs/api-reference.md`](docs/api-reference.md) | All REST endpoints with request/response JSON examples |
| [`docs/agent.md`](docs/agent.md) | Persona config, 7 stages, 9 tools, orchestrator flow, prompt assembly |
| [`docs/setup.md`](docs/setup.md) | Prerequisites, step-by-step, env vars table, Alembic commands, CLI usage, troubleshooting |
| [`docs/roadmap.md`](docs/roadmap.md) | All built features, prioritized pending items across frontend/backend/testing/infra |
