# Roadmap

## What's Built

### Database (PostgreSQL 16 + SQLAlchemy Async)

- Docker Compose for PostgreSQL 16 Alpine on port 5432 with persistent volume
- SQLAlchemy 2.0 async ORM — 7 models using Mapped style with ForeignKey relationships and cascade rules
- Alembic migrations — 2 applied (initial schema creating all 7 tables, fix_last_contacted_at_timezone)
- 20 Dubai properties seeded across 5 types, 10+ locations, price range 550K–25M AED
- 9 StrEnum definitions for status/types/stages/roles used across ORM and Pydantic layers
- Indexes on all frequently queried columns (phone, status, type, location, price, created_at)

### Backend (FastAPI + Python 3.12)

**Core Infrastructure:**
- FastAPI application factory with lifespan events (init_db/close_db)
- CORS middleware (allow all in dev, FRONTEND_URL in production)
- Request logging middleware (method, path, status, duration_ms via structlog)
- Global exception handlers for 6 custom exception types
- pydantic-settings configuration with 25+ env vars and derived properties
- Async database engine with session factory (pool_size=5, max_overflow=10)
- bcrypt password hashing, JWT creation/validation (HS256, 24h expiry)
- WhatsApp webhook HMAC-SHA256 signature verification

**Authentication (8 endpoints):**
- Signup (register admin user)
- Login (email + password -> JWT with 24h access + 7d refresh)
- Get current user profile
- Refresh access token
- Logout
- Change password (authenticated)
- Request password reset (sends email with token, 15min expiry)
- Confirm password reset

**Lead Management (7 endpoints):**
- Paginated list with filters (status, source, text search)
- Single lead by ID
- Create lead manually
- Partial update (any subset of fields; null clears columns via exclude_unset=True)
- Delete lead (CASCADE deletes conversations + meetings)
- Conversation history for a lead (chronological message list)
- Add internal note

**Property Management (6 endpoints):**
- Paginated list with filters (type, location, price range, bedrooms, status, text search)
- Single property by ID
- Create property
- Full update (PUT)
- Soft delete (sets status to archived)
- Toggle featured status

**Meeting Management (6 endpoints):**
- Paginated list with status filter
- Upcoming meetings (next 5)
- Single meeting by ID
- Schedule meeting (with ISO 8601 datetime parsing)
- Update/reschedule meeting
- Cancel meeting

**Analytics (4 endpoints):**
- Overview dashboard stats (total leads, qualified, upcoming meetings, converted, conversion rate)
- Leads over time (daily counts, configurable day range)
- Status breakdown (count + percentage per status)
- Source breakdown (count + percentage per source)

**WhatsApp Webhook (2 endpoints):**
- GET webhook — Meta verification handshake (hub.mode, hub.verify_token, hub.challenge)
- POST webhook — Full message processing pipeline with signature verification, dedup, lead auto-creation, AI agent, reply sending

### AI Agent (Sarah)

**Agent Architecture:**
- Raw Groq function calling with full orchestrator control (no LangChain/LangGraph)
- 7 conversation stages with stage-specific behavior instructions
- 8 tools with JSON Schema definitions and async handlers
- MAX_TOOL_ROUNDS = 10 with contextual fallback after exhaustion
- MAX_HISTORY_MESSAGES = 10 for context management (keeps token usage within free tier limits)
- Groq 429 retry: 3 attempts with exponential backoff (1s, 3s) before fallback
- JSON parse recovery: catches malformed tool arguments, returns recovery prompt to model
- Session staleness fix: rebuilds system prompt with fresh lead data after each tool round
- Parallel tool call handling (correct OpenAI format: one assistant message with all calls)
- Lazy-init LLMClient to avoid import-time side effects
- Token usage logging (prompt_tokens + completion_tokens per call)

**Agent Persona:**
- "Sarah" — warm, professional Dubai real estate consultant
- Indian buyer/NRI focus with cultural context understanding
- Hinglish language support
- AED + INR dual pricing display (lakh/crore notation)
- Dubai market knowledge (neighborhoods, pricing, legal, visa info)

**Agent Tools:**
- `search_properties` — filter by type, location, price, bedrooms (limit 5)
- `list_all_properties` — show everything available (no filters)
- `get_property_details` — full details by property ID
- `update_lead_info` — save learned preferences (all optional, null to clear)
- `update_lead_stage` — advance through 7-stage pipeline
- `schedule_meeting` — book site visit with ISO datetime
- `send_email` — send property info via SMTP
- `transfer_to_human` — escalate to team member

**Prompt Engineering:**
- Condensed system prompt (~800 tokens)
- Dynamic lead profile context built fresh from DB each call, rebuilt mid-call after tool modifications
- Stage-specific instructions guiding behavior per stage
- Guardrails: no hallucinated pricing, no personal contact sharing, no legal advice, Indian numbering rules, typo correction, no-results alternatives

**Agent CLI (WhatsApp Simulator):**
- `list`, `select`, `new`, `say`, `history`, `state`, `help`, `quit`
- Mirrors webhook flow exactly: store msg -> process_message -> store reply -> display
- Shows lead state after each interaction for debugging

### Integrations

**Groq Client:**
- OpenAI-compatible API wrapper
- Conditional tools/tool_choice support
- Token usage logging per call
- Lazy-init singleton pattern

**WhatsApp Client:**
- Send text messages via Meta Cloud API REST
- Parse webhook payload into normalized format
- HMAC-SHA256 signature verification
- Dev mode: skip verification when APP_SECRET is empty

**Email Client:**
- SMTP via stdlib smtplib with STARTTLS
- Dev mode: log email content to console when SMTP not configured
- SMTP wrapped in `asyncio.to_thread()` — non-blocking in async context

**Google Calendar Client:**
- Stub implementation (returns hardcoded event_id and meet_link)
- Methods: create_event, cancel_event

### Frontend (React 19 + Vite 8 + TypeScript 6)

**Foundation:**
- React 19 + Vite 8 + TypeScript 6 with strict mode
- Tailwind CSS v4 with OKLCH color space and JIT compilation
- 25 shadcn/ui primitives (button, dialog, table, card, badge, tabs, etc.)
- Geist variable font via @fontsource
- Full light/dark/system theme via next-themes with localStorage persistence
- Custom CSS utilities (glass, glass-card, text-gradient, shimmer, scrollbar-thin)
- Gold accent for Dubai branding

**Layout Shell:**
- AppShell with responsive sidebar (desktop) / sheet nav (mobile)
- Collapsible sidebar with Lucide icons, active route highlighting
- Header with breadcrumbs, search, notifications bell, theme switcher, user avatar
- Theme switcher with Sun/Moon/System options

**State Management:**
- authStore (Zustand): user, token, isAuthenticated, isLoading, setAuth, logout, hydrate
- filterStore (Zustand): lead + property filter state with set/reset actions
- sidebarStore (Zustand): isCollapsed, isMobileOpen, toggle actions

**API Layer:**
- Axios instance with baseURL /api/v1, 30s timeout
- Request interceptor: injects Bearer token from localStorage
- Response interceptor: clears auth + redirects to /login on 401
- TanStack Query with 5min staleTime, 1 retry

**Forms (React Hook Form + Zod):**
- LeadForm: all lead fields with phone/budget validation
- PropertyForm: all property fields with price/title validation
- MeetingForm: lead selector, date picker, duration
- LoginForm: email + password with format validation
- SettingsForm: app configuration fields

**Shared Components:**
- DataTable: generic sortable, paginated table with responsive card view
- PageHeader: title + description + optional action
- LoadingState: spinner, skeleton, dots variants
- EmptyState: icon + title + description + optional CTA
- ErrorState: message + retry button
- ConfirmDialog: confirmation modal with variants
- SearchInput: debounced search (300ms) with clear button
- Pagination: page controls with ellipsis
- StatCard: metric card with trend indicator and hover lift
- StatusBadge: color-coded badges for lead/property/meeting statuses

**Types & Schemas:**
- TypeScript interfaces: Lead, Property, PropertyImage, Conversation, Message, Meeting, AdminUser, AnalyticsOverview, PaginatedResponse, ApiError
- Zod schemas: leadFormSchema, propertyFormSchema, meetingFormSchema, loginSchema, signupSchema, settingsSchema
- Constants: LEAD_STATUSES, LEAD_SOURCES, PROPERTY_TYPES, PROPERTY_STATUSES, MEETING_STATUSES, DUBAI_AREAS (20 areas), NAV_ITEMS (7 items)

## What's Next

### Frontend Pages (Priority)

| Page | Status | What's Needed |
|------|--------|---------------|
| Login page | Components done | Wire up LoginForm + AuthLayout + authStore |
| Dashboard | Components done | StatCards + Recharts (line chart for leads, donut for sources) + DataTable for recent leads |
| Lead list | Components done | DataTable + SearchInput + StatusBadge + filterStore |
| Lead detail | Requires new components | Conversation log (chat bubbles), activity timeline, status history, edit sheet |
| Property grid/list | Components done | DataTable/PropertyCard + SearchInput + filterStore |
| Property create/edit | Form done | PropertyForm wired to API |
| Property detail | Requires new components | Image gallery, full details, matched leads |
| Meeting calendar | Components done | react-day-picker calendar + list toggle + status filters |
| Analytics | Components done | Recharts + StatCard + date range picker |
| Settings | Form done | Tabs for general/WhatsApp/AI/Notifications/Team |

### Backend Enhancements

| Item | Description |
|------|-------------|
| Context window tracking | Monitor prompt_tokens and auto-truncate history if approaching limit |
| No-results handler | Move into search_properties tool: suggest alternatives and nearby areas |

### Testing

| Item | Description |
|------|-------------|
| conftest fixtures | AsyncTestClient, mock Groq, sample leads/properties/webhook payloads |
| Agent tests | Greeting, info extraction, property search, meeting scheduling, out-of-scope, guardrails |
| API endpoint tests | Auth, leads CRUD, properties CRUD, meetings, analytics |
| Webhook tests | Verification, inbound processing, signature check, dedup |
| Frontend unit tests | Zustand stores, Zod schemas, utility functions |
| Frontend component tests | Form validation, DataTable rendering, StatusBadge colors |

### Infrastructure

| Item | Description |
|------|-------------|
| GitHub Actions CI | Backend: ruff check -> mypy -> pytest. Frontend: tsc -> lint -> build |
| Backend Dockerfile | Multi-stage: python:3.12-slim, install deps, copy app |
| Frontend Dockerfile | Multi-stage: node:20 build -> nginx:alpine serve |
| docker-compose.yml | Add backend + frontend + Redis services |
| docker-compose.prod.yml | Production overrides (env, ports, replicas) |
| Deployment workflow | GitHub Actions -> container registry -> VPS/Railway/Fly.io |
| Health check improvements | Add DB connection check, Groq connectivity check |
| Rate limiting | Apply slowapi or custom middleware to webhook and auth endpoints |

### Google Calendar (Replace Stub)

| Item | Description |
|------|-------------|
| Service account auth | Decode GOOGLE_SERVICE_ACCOUNT_JSON, initialize Google API client |
| create_event | Real Google Calendar event with Google Meet conference data |
| cancel_event | Delete/decline calendar event |
| check_availability | Query freebusy API for available slots |
| reschedule_event | Update existing event datetime |

### Notifications (Enhance)

| Item | Description |
|------|-------------|
| Email templates | HTML templates for meeting confirmation, lead notification, agent alert |
| WhatsApp templates | Approved message templates for meeting confirmations |
| Notification service | Unified dispatch: in_app + email + whatsapp |
| Meeting reminders | Scheduled task to send reminder 1 hour before meeting |

### Production Readiness

| Item | Description |
|------|-------------|
| Proper SECRET_KEY | Generate and document for production deployment |
| CORS lockdown | Restrict to FRONTEND_URL only in production |
| HTTPS/TLS | Let's Encrypt via Nginx or Cloudflare |
| Environment separation | staging and production environment configs |
| Monitoring | Health check endpoints, structured logging to stdout |
| Backup strategy | PostgreSQL pg_dump cron job or managed DB backups |
