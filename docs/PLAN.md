# Lead Generation & AI Automation System — Production Plan

> **Project:** Dubai Real Estate Lead Generation Platform  
> **Stack:** Python (FastAPI) + React (Vite + TypeScript) + Supabase  
> **Date:** May 2026

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Tech Stack](#2-tech-stack)
3. [Directory Structure](#3-directory-structure)
4. [Phased Implementation Plan](#4-phased-implementation-plan)
   - [Phase 0: Project Scaffolding & Tooling](#phase-0-project-scaffolding--tooling)
   - [Phase 1: Frontend Foundation](#phase-1-frontend-foundation)
   - [Phase 2: Backend Foundation](#phase-2-backend-foundation)
   - [Phase 3: WhatsApp Webhook & AI Agent Core](#phase-3-whatsapp-webhook--ai-agent-core)
   - [Phase 4: Lead Management Dashboard](#phase-4-lead-management-dashboard)
   - [Phase 5: Property Management Module](#phase-5-property-management-module)
   - [Phase 6: Meeting Scheduling & Google Calendar Integration](#phase-6-meeting-scheduling--google-calendar-integration)
   - [Phase 7: Notification System (Email + WhatsApp)](#phase-7-notification-system-email--whatsapp)
   - [Phase 8: Admin Panel & Analytics](#phase-8-admin-panel--analytics)
   - [Phase 9: Auth & RBAC](#phase-9-auth--rbac)
   - [Phase 10: Testing, CI/CD & Deployment](#phase-10-testing-cicd--deployment)
5. [Supabase Schema Design](#5-supabase-schema-design)
6. [AI Agent Flow](#6-ai-agent-flow)
7. [Business Rules & Edge Cases](#7-business-rules--edge-cases)

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           META ADS                                  │
│                    (Facebook / Instagram)                            │
└──────────────────────┬──────────────────────────────────────────────┘
                       │ Click → WhatsApp deep link
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      WHATSAPP                                       │
│              User sends message to company number                    │
└──────────────────────┬───────────────────────────────────────────────┘
                       │ Webhook (inbound message)
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│               BACKEND (FastAPI + Python)                             │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ WhatsApp  │  │   AI     │  │ Google   │  │  Notification    │   │
│  │ Webhook  │  │  Agent   │  │ Calendar │  │  Service         │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────┬──────────┘   │
│       │              │             │                │              │
│       └──────────────┴─────────────┴────────────────┘              │
│                              │                                      │
│                              ▼                                      │
│                     ┌────────────────┐                             │
│                     │   Supabase     │                             │
│                     │  (PostgreSQL)  │                             │
│                     └────────────────┘                             │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│               FRONTEND (React + Vite + TypeScript)                   │
│                                                                      │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐       │
│  │  Dashboard      │  │  Lead Mgmt     │  │  Property Mgmt   │       │
│  └────────────────┘  └────────────────┘  └──────────────────┘       │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐       │
│  │  Analytics      │  │  Schedule      │  │  Settings/Admin   │       │
│  └────────────────┘  └────────────────┘  └──────────────────┘       │
└──────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User clicks Meta Ad → WhatsApp deep link opens
2. User sends "Hi" to company WhatsApp number
3. Meta Webhook delivers message to backend /api/v1/whatsapp/webhook
4. Backend verifies webhook signature, stores message in Supabase
5. AI Agent picks up the conversation context
6. Agent engages user: captures name, email, budget, preferences
7. Agent searches available properties in DB → sends options via WhatsApp
8. Agent asks if user wants to schedule a Google Meet
9. If yes → creates Google Calendar event → sends meeting link
10. Notification service sends:
    - Email to lead with meeting details
    - Email to human agent/admin
    - WhatsApp message to human agent
11. All conversation data, lead enrichment, and status updates stored in Supabase
```

---

## 2. Tech Stack

### Backend

| Category              | Choice                        | Rationale                              |
|-----------------------|-------------------------------|----------------------------------------|
| Framework             | FastAPI                       | Async, auto-docs, production-ready     |
| Runtime               | Python 3.12+                  | Modern features, performance           |
| ORM/Database          | supabase-py (raw SQL)         | Direct Supabase access, no heavy ORM   |
| AI Model              | OpenAI API (GPT-4o-mini)      | Cost-effective, fast, json mode        |
| AI Safety             | Pydantic + custom guardrails  | Structured output, input validation    |
| WhatsApp API          | Meta Cloud API (requests)     | Official API, reliable                 |
| Calendar              | Google Calendar API           | Industry standard                      |
| Email                 | Resend / SendGrid             | Reliable transactional email           |
| Background Tasks      | Celery + Redis (or arq)       | Async task processing                  |
| Validation            | Pydantic v2                   | Fast, native FastAPI integration       |
| HTTP Client           | httpx                         | Async, modern                          |
| Auth                  | Supabase Auth (JWT)           | Built-in, Row Level Security           |
| Testing               | pytest + pytest-asyncio       | Standard Python testing                |
| Formatting/Linting    | ruff                          | Fast, unified                          |

### Frontend

| Category              | Choice                        | Rationale                              |
|-----------------------|-------------------------------|----------------------------------------|
| Framework             | React 19 + Vite 8             | Modern, fast, HMR                      |
| Language              | TypeScript 6                  | Type safety                            |
| Routing               | React Router v7               | Standard, nested routes, loaders       |
| Forms                 | React Hook Form + Zod         | Performant forms, schema validation    |
| State Management      | Zustand                       | Lightweight, no boilerplate            |
| HTTP Client           | TanStack Query (React Query)  | Caching, mutations, background sync    |
| UI Library            | shadcn/ui (Radix primitives)  | Accessible, customizable, headless     |
| Styling               | Tailwind CSS v4               | Utility-first, consistent              |
| Icons                 | Lucide React                  | Clean, consistent icons                |
| Charts                | Recharts                      | Composable, React-native               |
| Calendar/Date         | react-day-picker              | Accessible date picker                 |
| Notifications         | Sonner (toast)                | Clean toast notifications              |
| Testing               | Vitest + Testing Library      | Fast, Vite-native                      |

---

## 3. Directory Structure

```
LeadGeneration/
├── backend/
│   ├── .venv/
│   ├── .env
│   ├── .env.example
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── config.py                # Settings (pydantic-settings)
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── client.py            # Supabase client singleton
│   │   │   └── migrations/          # Raw SQL migrations
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── lead.py              # Pydantic models for lead
│   │   │   ├── property.py          # Pydantic models for property
│   │   │   ├── conversation.py      # Pydantic models for messages
│   │   │   ├── meeting.py           # Pydantic models for meetings
│   │   │   └── agent.py             # Pydantic models for agent state
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py        # v1 router aggregator
│   │   │   │   ├── whatsapp.py      # Webhook endpoints
│   │   │   │   ├── leads.py         # Lead CRUD endpoints
│   │   │   │   ├── properties.py    # Property CRUD endpoints
│   │   │   │   ├── meetings.py      # Meeting endpoints
│   │   │   │   ├── auth.py          # Auth endpoints
│   │   │   │   ├── analytics.py     # Analytics endpoints
│   │   │   │   └── webhooks.py      # External webhooks (calendar, etc.)
│   │   │   └── deps.py              # Dependency injection (get_db, get_current_user)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── whatsapp.py          # Meta Cloud API client
│   │   │   ├── agent.py             # AI Agent orchestration
│   │   │   ├── agent_tools.py       # Tools the agent can call
│   │   │   ├── agent_prompts.py     # System prompts & templates
│   │   │   ├── openai_client.py     # OpenAI API client wrapper
│   │   │   ├── calendar.py          # Google Calendar integration
│   │   │   ├── email.py             # Email service
│   │   │   ├── notification.py      # Unified notification dispatcher
│   │   │   ├── lead_enrichment.py   # Lead data processing
│   │   │   └── property_search.py   # Property matching logic
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py          # JWT, hashing, verification
│   │   │   ├── middleware.py        # CORS, logging, rate limiting
│   │   │   └── exceptions.py        # Custom exception handlers
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py        # Phone, email, URL validators
│   │       └── helpers.py           # Misc utility functions
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_whatsapp.py
│   │   ├── test_agent.py
│   │   ├── test_leads.py
│   │   └── test_properties.py
│   └── scripts/
│       ├── seed_properties.py
│       └── migrate.sh
│
├── frontend/
│   ├── .env
│   ├── .env.example
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── components.json            # shadcn/ui config
│   ├── Dockerfile
│   ├── public/
│   │   ├── favicon.svg
│   │   └── og-image.png
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css               # Tailwind imports + theme vars
│       ├── vite-env.d.ts
│       ├── lib/
│       │   ├── utils.ts            # cn() helper
│       │   ├── supabase.ts         # Supabase client
│       │   └── api.ts              # Axios/fetch wrapper
│       ├── hooks/
│       │   ├── use-auth.ts
│       │   ├── use-leads.ts
│       │   ├── use-properties.ts
│       │   ├── use-meetings.ts
│       │   ├── use-analytics.ts
│       │   └── use-media-query.ts
│       ├── stores/
│       │   ├── auth.store.ts
│       │   ├── ui.store.ts
│       │   └── filters.store.ts
│       ├── schemas/
│       │   ├── auth.schema.ts      # Zod schemas
│       │   ├── lead.schema.ts
│       │   ├── property.schema.ts
│       │   ├── meeting.schema.ts
│       │   └── common.schema.ts
│       ├── types/
│       │   ├── index.ts
│       │   ├── lead.ts
│       │   ├── property.ts
│       │   ├── meeting.ts
│       │   ├── auth.ts
│       │   └── analytics.ts
│       ├── components/
│       │   ├── ui/                 # shadcn/ui primitives
│       │   │   ├── button.tsx
│       │   │   ├── input.tsx
│       │   │   ├── dialog.tsx
│       │   │   ├── dropdown-menu.tsx
│       │   │   ├── table.tsx
│       │   │   ├── badge.tsx
│       │   │   ├── card.tsx
│       │   │   ├── avatar.tsx
│       │   │   ├── select.tsx
│       │   │   ├── textarea.tsx
│       │   │   ├── toast.tsx
│       │   │   ├── sheet.tsx
│       │   │   ├── tabs.tsx
│       │   │   ├── skeleton.tsx
│       │   │   ├── separator.tsx
│       │   │   └── tooltip.tsx
│       │   ├── layout/
│       │   │   ├── app-shell.tsx
│       │   │   ├── sidebar.tsx
│       │   │   ├── navbar.tsx
│       │   │   ├── mobile-nav.tsx
│       │   │   └── theme-switcher.tsx
│       │   ├── leads/
│       │   │   ├── lead-table.tsx
│       │   │   ├── lead-card.tsx
│       │   │   ├── lead-details.tsx
│       │   │   ├── lead-filters.tsx
│       │   │   ├── lead-status-badge.tsx
│       │   │   ├── lead-conversation-log.tsx
│       │   │   └── lead-actions.tsx
│       │   ├── properties/
│       │   │   ├── property-grid.tsx
│       │   │   ├── property-card.tsx
│       │   │   ├── property-details.tsx
│       │   │   ├── property-form.tsx
│       │   │   ├── property-filters.tsx
│       │   │   └── property-gallery.tsx
│       │   ├── meetings/
│       │   │   ├── meeting-calendar.tsx
│       │   │   ├── meeting-list.tsx
│       │   │   ├── meeting-scheduler.tsx
│       │   │   └── meeting-card.tsx
│       │   ├── analytics/
│       │   │   ├── stats-cards.tsx
│       │   │   ├── lead-chart.tsx
│       │   │   ├── conversion-funnel.tsx
│       │   │   └── agent-performance.tsx
│       │   ├── auth/
│       │   │   ├── login-form.tsx
│       │   │   ├── signup-form.tsx
│       │   │   ├── forgot-password.tsx
│       │   │   └── protected-route.tsx
│       │   └── shared/
│       │       ├── empty-state.tsx
│       │       ├── error-state.tsx
│       │       ├── loading-state.tsx
│       │       ├── confirm-dialog.tsx
│       │       ├── data-table.tsx
│       │       ├── search-input.tsx
│       │       ├── pagination.tsx
│       │       └── page-header.tsx
│       ├── pages/
│       │   ├── login.tsx
│       │   ├── signup.tsx
│       │   ├── forgot-password.tsx
│       │   ├── dashboard.tsx
│       │   ├── leads/
│       │   │   ├── index.tsx
│       │   │   └── [id].tsx
│       │   ├── properties/
│       │   │   ├── index.tsx
│       │   │   ├── new.tsx
│       │   │   └── [id].tsx
│       │   ├── meetings/
│       │   │   └── index.tsx
│       │   ├── analytics/
│       │   │   └── index.tsx
│       │   ├── settings/
│       │   │   └── index.tsx
│       │   └── not-found.tsx
│       ├── layouts/
│       │   ├── auth-layout.tsx
│       │   └── dashboard-layout.tsx
│       └── constants/
│           ├── index.ts
│           ├── lead-status.ts
│           ├── property-types.ts
│           └── enums.ts
│
├── docs/
│   ├── PLAN.md                    # This file
│   ├── API.md                     # API documentation
│   ├── AGENT.md                   # AI agent behavior docs
│   └── DEPLOYMENT.md              # Deployment guide
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── deploy.yml
│   └── CODEOWNERS
│
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

---

## 4. Phased Implementation Plan

### Phase 0: Project Scaffolding & Tooling

**Goal:** Initialize project structure, tooling, and shared configurations.

#### Backend Tasks

- [ ] Create `pyproject.toml` with dependencies:
  - `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`
  - `supabase`, `httpx`, `openai`, `python-multipart`
  - `celery[redis]` (or `arq` for lighter async tasks)
  - `python-jose[cryptography]` (JWT), `passlib[bcrypt]`
  - `pytest`, `pytest-asyncio`, `ruff`, `mypy`
  - `alembic` (if using raw SQL migrations management)
- [ ] Setup `src/config.py` using `pydantic-settings` — env vars loading
- [ ] Setup `src/main.py` — FastAPI app with CORS, lifespan, router mounts
- [ ] Create `.env.example` with all required env vars:
  - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
  - `OPENAI_API_KEY`, `OPENAI_MODEL` (default: `gpt-4o-mini`)
  - `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`
  - `GOOGLE_CREDENTIALS_JSON` (base64), `GOOGLE_CALENDAR_ID`
  - `RESEND_API_KEY` or `SENDGRID_API_KEY`
  - `CELERY_BROKER_URL` (redis://...)
  - `SECRET_KEY`, `ENVIRONMENT`, `LOG_LEVEL`
  - `FRONTEND_URL`, `ADMIN_WHATSAPP_NUMBER`, `ADMIN_EMAIL`
- [ ] Setup `ruff` and `mypy` config in `pyproject.toml`
- [ ] Create `tests/conftest.py` — test fixtures (mock supabase, mock openai, test client)
- [ ] Create `scripts/migrate.sh` — runs SQL migration files against Supabase

#### Frontend Tasks

- [ ] Install dependencies:
  ```
  npm install react-router-dom react-hook-form @hookform/resolvers zod zustand
  npm install @tanstack/react-query axios sonner recharts lucide-react
  npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
  npm install @radix-ui/react-select @radix-ui/react-tabs
  npm install @radix-ui/react-tooltip @radix-ui/react-sheet
  npm install @radix-ui/react-avatar @radix-ui/react-separator
  npm install class-variance-authority clsx tailwind-merge
  npm install date-fns react-day-picker
  npm install @supabase/supabase-js
  ```
- [ ] Initialize `tailwind.config.ts` with design tokens (blue primary, custom spacing)
- [ ] Setup `postcss.config.js`
- [ ] Create `src/index.css` with Tailwind directives + CSS custom properties for light/dark
- [ ] Initialize shadcn/ui (`npx shadcn@latest init`)
- [ ] Setup `components.json` for shadcn/ui
- [ ] Create `lib/utils.ts` with `cn()` utility
- [ ] Create `lib/supabase.ts` — Supabase client (anon key for public, service role for admin)
- [ ] Create `lib/api.ts` — Axios instance with interceptors (auth token injection, error handling)
- [ ] Setup `tsconfig.json` path aliases: `@/*` → `src/*`

**Dependencies for pyproject.toml:**

```toml
[project]
name = "lead-generation-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    "pydantic>=2.10",
    "pydantic-settings>=2.7",
    "supabase>=2.9",
    "httpx>=0.28",
    "openai>=1.68",
    "python-multipart>=0.0.19",
    "python-jose[cryptography]>=3.3",
    "passlib[bcrypt]>=1.7",
    "celery[redis]>=5.4",
    "redis>=5.2",
    "google-api-python-client>=2.160",
    "google-auth-httplib2>=0.2",
    "google-auth-oauthlib>=1.2",
    "resend>=0.11",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3",
    "pytest-asyncio>=0.25",
    "ruff>=0.11",
    "mypy>=1.15",
    "httpx>=0.28",
]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "ARG", "C4"]

[tool.mypy]
python_version = "3.12"
strict = true
```

---

### Phase 1: Frontend Foundation

**Goal:** Establish design system, theming, layout shell, and all shared UI components.

#### Tasks

- [ ] **Design Tokens (CSS Custom Properties):**
  ```css
  @layer base {
    :root {
      --background: 0 0% 100%;
      --foreground: 222.2 84% 4.9%;
      --primary: 221.2 83.2% 53.3%;       /* Blue-600 */
      --primary-foreground: 210 40% 98%;
      /* ... remaining shadcn vars */
    }
    .dark {
      --background: 222.2 84% 4.9%;
      --foreground: 210 40% 98%;
      --primary: 217.2 91.2% 59.8%;       /* Blue-400 */
      /* ... */
    }
  }
  ```
- [ ] **Theme System:**
  - Create `stores/ui.store.ts` with Zustand — `theme` (light/dark/system), `sidebarOpen`, `isMobile`
  - Create `components/layout/theme-switcher.tsx` — toggle with system detection
  - Persist theme preference in localStorage
  - Add `class="dark"` to `<html>` for dark mode
- [ ] **Layout Shell:**
  - `app-shell.tsx` — sidebar + navbar + main content area (responsive)
  - `sidebar.tsx` — collapsible, navigation links with icons, active state
  - `navbar.tsx` — breadcrumbs, search, notifications badge, user avatar, theme toggle
  - `mobile-nav.tsx` — bottom nav or drawer for mobile
  - `dashboard-layout.tsx` — wraps authenticated pages
  - `auth-layout.tsx` — centered card layout for login/signup
- [ ] **Shared Components (build all):**
  - `page-header.tsx` — title + description + action button slot
  - `empty-state.tsx` — icon + title + description + CTA
  - `error-state.tsx` — error icon + message + retry button
  - `loading-state.tsx` — spinner/skeleton
  - `confirm-dialog.tsx` — reusable confirmation modal
  - `data-table.tsx` — generic sortable, paginated table (TanStack Table or custom)
  - `search-input.tsx` — debounced search
  - `pagination.tsx` — page controls
- [ ] **shadcn/ui primitives:** Generate via CLI: button, input, dialog, dropdown-menu, table, badge, card, avatar, select, textarea, toast, sheet, tabs, skeleton, separator, tooltip
- [ ] **Routing Setup:**
  ```tsx
  <Routes>
    <Route element={<AuthLayout />}>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
    </Route>
    <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
      <Route path="/" element={<Dashboard />} />
      <Route path="/leads" element={<LeadsIndex />} />
      <Route path="/leads/:id" element={<LeadDetail />} />
      <Route path="/properties" element={<PropertiesIndex />} />
      <Route path="/properties/new" element={<PropertyNew />} />
      <Route path="/properties/:id" element={<PropertyDetail />} />
      <Route path="/meetings" element={<MeetingsIndex />} />
      <Route path="/analytics" element={<AnalyticsIndex />} />
      <Route path="/settings" element={<Settings />} />
    </Route>
    <Route path="*" element={<NotFound />} />
  </Routes>
  ```
- [ ] **Auth Flow UI:** Login, Signup, Forgot Password pages with RHF + Zod
- [ ] **Protected Route:** Check auth state, redirect to /login if unauthenticated

**Design Principles:**
- Blue primary palette (#2563eb → #1d4ed8 → #1e40af)
- Clean whitespace, subtle borders, consistent border-radius (8px)
- Cards with soft shadows, hover states on interactive elements
- Loading skeletons for all data-fetching states
- Framer-motion or CSS transitions for sidebar/modal (keep it snappy)

---

### Phase 2: Backend Foundation

**Goal:** Core FastAPI app, database client, auth, and API structure.

#### Tasks

- [ ] **`src/main.py`:**
  ```python
  from contextlib import asynccontextmanager
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware

  @asynccontextmanager
  async def lifespan(app: FastAPI):
      # Startup: verify connections, init clients
      yield
      # Shutdown: cleanup

  app = FastAPI(title="LeadGen API", version="0.1.0", lifespan=lifespan)
  app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, ...)
  app.include_router(v1_router, prefix="/api/v1")
  ```
- [ ] **`src/config.py`:**
  - `Settings(BaseSettings)` class with all env vars
  - `model_config = SettingsConfigDict(env_file=".env")`
- [ ] **`src/database/client.py`:**
  - `create_supabase_client()` — uses `SUPABASE_URL` + `SUPABASE_SERVICE_KEY`
  - Singleton pattern or FastAPI dependency
  - All DB calls go through this client (raw SQL or supabase-py methods)
- [ ] **`src/core/security.py`:**
  - `hash_password()`, `verify_password()` — passlib bcrypt
  - `create_access_token()`, `decode_access_token()` — python-jose JWT
  - `verify_whatsapp_webhook_token()` — Meta webhook verification
- [ ] **`src/api/deps.py`:**
  - `get_supabase()` — yields Supabase client
  - `get_current_user()` — extracts JWT, fetches user from Supabase Auth
  - `require_admin()` — checks user role
- [ ] **`src/core/middleware.py`:**
  - Request ID middleware (uuid per request for tracing)
  - Request logging middleware (method, path, status, duration)
  - Rate limiting middleware (in-memory or Redis-backed)
- [ ] **`src/core/exceptions.py`:**
  - `AppException`, `NotFoundException`, `UnauthorizedException`, `ForbiddenException`
  - Global exception handler → structured JSON response
- [ ] **Auth endpoints (`src/api/v1/auth.py`):**
  - `POST /auth/signup` — register with email + password
  - `POST /auth/login` — returns JWT access + refresh token
  - `POST /auth/refresh` — refresh token endpoint
  - `POST /auth/forgot-password` — sends reset email via Supabase Auth
- [ ] **Create `pyproject.toml`** with all dependencies listed in Phase 0

---

### Phase 3: Supabase Schema Design & Migration

**Goal:** Database schema, RLS policies, and seed data.

**See Section 5 below for full schema.**

#### Tasks

- [ ] Create `backend/src/database/migrations/001_initial_schema.sql` with all tables
- [ ] Create `backend/src/database/migrations/002_rls_policies.sql` — Row Level Security
- [ ] Create `backend/src/database/migrations/003_seed_properties.sql` — sample Dubai properties
- [ ] Run migrations against Supabase project
- [ ] Create `scripts/seed_properties.py` to insert property data programmatically

---

### Phase 4: WhatsApp Webhook & AI Agent Core

**Goal:** Receive WhatsApp messages, process via AI agent, respond.

#### Tasks

**WhatsApp Webhook:**

- [ ] **`src/services/whatsapp.py`:**
  - `send_text_message(to: str, text: str)` → POST to Meta Cloud API
  - `send_template_message(to: str, template_name: str, params: dict)` — for approved templates
  - `send_interactive_list(to: str, header: str, body: str, options: list)` — list of options
  - `send_interactive_buttons(to: str, body: str, buttons: list)` — quick reply buttons
  - `mark_as_read(message_id: str)` — mark webhook message as read
  - `verify_webhook(mode, token, challenge)` — Meta verification handshake
  - `parse_webhook_payload(body: dict)` → normalized message object
- [ ] **`src/api/v1/whatsapp.py`:**
  - `GET /whatsapp/webhook` — verification endpoint (hub.mode, hub.verify_token, hub.challenge)
  - `POST /whatsapp/webhook` — inbound message handler
    - Verify signature
    - Parse message (text, interactive reply, image)
    - Store message in `conversations` table
    - Call AI agent to process
    - Send response via WhatsApp service
  - `POST /whatsapp/send` — admin endpoint to manually send message to a lead

**AI Agent:**

- [ ] **`src/services/openai_client.py`:**
  - `get_chat_response(messages: list, tools: list, json_mode: bool = False)` → response
  - Support streaming (optional for WhatsApp, useful for dashboard preview)
  - Retry logic with exponential backoff
  - Token usage tracking
- [ ] **`src/services/agent_prompts.py`:**
  - `SYSTEM_PROMPT` — full persona definition:
    - Name: "Sarah" (or a Dubai-appropriate name)
    - Role: Real estate consultant for a Dubai-based agency
    - Tone: Professional, warm, helpful, persuasive but not pushy
    - Languages: English (primary), Arabic (optional)
    - Knowledge: Dubai real estate market, neighborhoods, property types
    - Guardrails:
      - Never share pricing outside database
      - Never promise anything not in data
      - If user is angry/abusive → politely escalate to human
      - Always confirm data before saving
      - Never ask for payment or sensitive financial info beyond budget range
    - Conversation flow stages (see Section 6)
  - `TOOL_DESCRIPTIONS` — function definitions for the agent
- [ ] **`src/services/agent_tools.py`:**
  - `search_properties(budget_min, budget_max, property_type, bedrooms, location, ...)` → list
  - `get_property_details(property_id)` → single property with full info
  - `save_lead_info(name, email, phone, budget, preferences)` → lead_id
  - `update_lead_stage(lead_id, stage, notes)` → updates lead pipeline stage
  - `schedule_meeting(lead_id, preferred_datetime, timezone)` → creates Google Calendar event
  - `send_property_images(lead_id, property_ids)` → sends media via WhatsApp
  - `get_lead_context(lead_id)` → conversation history + lead data
  - `escalate_to_human(lead_id, reason)` → flags lead for human attention
- [ ] **`src/services/agent.py`:**
  - `process_message(lead_id: str, message: str) -> str`:
    1. Load conversation history (last N messages) from DB
    2. Load lead data if exists
    3. Build message list: system prompt + conversation history + new message
    4. Call OpenAI with function calling
    5. If function call → execute tool → append result → call OpenAI again
    6. Loop until final response (max 3 tool calls per turn)
    7. Store assistant response in `conversations` table
    8. Return response text
    9. Handle errors gracefully (log, send apology + "we'll get back to you")
- [ ] **WhatsApp + Agent Integration:**
  - Webhook receives message → stores it → calls `agent.process_message()` → sends response via WhatsApp
  - Background task for long-running agent turns (Celery/arq)
  - Idempotency: deduplicate webhook messages using Meta's `message_id`

---

### Phase 5: Lead Management Dashboard

**Goal:** Full CRUD for leads, filtering, conversation log viewer.

#### Frontend Tasks

- [ ] **`leads/lead-table.tsx`:**
  - Columns: Name, Phone, Email, Status, Source, Property Interest, Created At, Last Contacted
  - Sortable columns, client-side or server-side pagination
  - Row click → navigates to lead detail
  - Bulk actions: assign, change status, export CSV
- [ ] **`leads/lead-card.tsx`:** Mobile-friendly card view of lead
- [ ] **`leads/lead-details.tsx`:**
  - Lead info panel (editable fields via sheet/modal)
  - Conversation timeline: chronological log of all WhatsApp messages
  - Activity log: status changes, meeting schedules, notes
    - Status: `new → contacted → qualified → meeting_scheduled → converted → lost`
  - Agent notes section (internal notes for human agents)
  - Action buttons: Send WhatsApp, Schedule Meeting, Mark Converted, Escalate
- [ ] **`leads/lead-filters.tsx`:**
  - Status multi-select, date range, property type, source (meta_ads, manual, referral)
  - Search by name/phone/email
- [ ] **`pages/leads/index.tsx`:** Combines filters + table/card view toggle
- [ ] **`pages/leads/[id].tsx`:** Lead detail page

#### Backend Tasks

- [ ] **`src/api/v1/leads.py`:**
  - `GET /leads` — list with pagination, filters, sorting
  - `GET /leads/{id}` — single lead with full details
  - `PATCH /leads/{id}` — update lead (status, notes, assigned agent)
  - `POST /leads/{id}/assign` — assign to human agent
  - `GET /leads/{id}/conversations` — message history
  - `POST /leads/{id}/notes` — add internal note
  - `GET /leads/export` — CSV export

---

### Phase 6: Property Management Module

**Goal:** CRUD for property listings, search, gallery management.

#### Frontend Tasks

- [ ] **`properties/property-grid.tsx`:** Grid + list toggle view
- [ ] **`properties/property-card.tsx`:**
  - Image carousel/gallery thumbnails
  - Title, price (AED), location, bedrooms/bathrooms, area (sqft)
  - Status badge (available, sold, under_offer, coming_soon)
  - Tags: "Featured", "New Launch", "Ready to Move"
- [ ] **`properties/property-form.tsx`:**
  - Fields: title, description, price, property_type (apartment/villa/office/land), bedrooms, bathrooms, area, location, latitude/longitude, amenities (multi-select), images (drag & drop upload to Supabase Storage), status, featured toggle
  - RHF + Zod validation
  - Image upload with preview, drag-reorder
- [ ] **`properties/property-filters.tsx`:**
  - Price range, property type, bedrooms, location, status
- [ ] **`pages/properties/index.tsx`:** Browse all properties
- [ ] **`pages/properties/new.tsx`:** Create property form
- [ ] **`pages/properties/[id].tsx`:** Property detail + edit capability (inline or sheet)

#### Backend Tasks

- [ ] **`src/api/v1/properties.py`:**
  - `GET /properties` — list with filters, pagination, search
  - `GET /properties/{id}` — full property details
  - `POST /properties` — create property
  - `PUT /properties/{id}` — update property
  - `DELETE /properties/{id}` — soft delete
  - `POST /properties/{id}/images` — upload images to Supabase Storage
  - `DELETE /properties/{id}/images/{image_id}` — remove image
  - `PATCH /properties/{id}/featured` — toggle featured status
- [ ] **Property search logic in `src/services/property_search.py`:**
  - Filtering by budget range, type, bedrooms, location
  - Text search on title/description
  - Geospatial proximity (if lat/lng available)
  - "Best match" scoring for AI agent suggestions

---

### Phase 7: Google Calendar & Meeting Scheduling

**Goal:** Schedule Google Meet via AI agent + admin interfaces.

#### Tasks

- [ ] **Google API Setup:**
  - Service account with Google Calendar API enabled
  - Domain-wide delegation (to create events on behalf of users) OR use a shared calendar
  - Store service account JSON in env var (base64 encoded)
- [ ] **`src/services/calendar.py`:**
  - `create_google_meet(lead_name, lead_email, datetime, duration_minutes=30, timezone)`:
    - Creates Google Calendar event with Google Meet link
    - Sets description with lead info + property context
    - Adds conference data (Google Meet)
    - Returns `meeting_link`, `event_id`
  - `check_availability(datetime, timezone)` — check if slot is free
  - `cancel_meeting(event_id)` — delete/decline event
  - `reschedule_meeting(event_id, new_datetime)` — update event time
- [ ] **AI Agent Integration:**
  - Agent asks: "Would you like to schedule a meeting to see this property?"
  - If yes → agent asks for preferred date/time
  - Tool: `schedule_meeting(lead_id, datetime_str, timezone)`:
    - Calls calendar service
    - Stores meeting record in `meetings` table
    - Returns meeting link
    - Agent sends: "Great! Here's your Google Meet link: [link]"
- [ ] **API Endpoints (`src/api/v1/meetings.py`):**
  - `GET /meetings` — list all meetings with filters
  - `POST /meetings` — manually schedule
  - `PATCH /meetings/{id}` — reschedule
  - `DELETE /meetings/{id}` — cancel
  - `GET /meetings/upcoming` — upcoming meetings (for dashboard widget)

#### Frontend Tasks

- [ ] **`meetings/meeting-calendar.tsx`:** Calendar view (month/week/day)
- [ ] **`meetings/meeting-list.tsx`:** List view with status filters
- [ ] **`meetings/meeting-scheduler.tsx`:** Date/time picker + timezone selector
- [ ] **`pages/meetings/index.tsx`:** Full meetings page

---

### Phase 8: Notification System

**Goal:** Automated email + WhatsApp notifications for meetings and lead events.

#### Tasks

- [ ] **`src/services/email.py`:**
  - `send_email(to: str, subject: str, html_body: str)` → via Resend/SendGrid
  - Templates (use simple HTML or Jinja2):
    - `meeting_confirmation_lead.html` — to lead with meeting details + Google Meet link
    - `meeting_notification_agent.html` — to human agent with lead info + meeting link
    - `new_lead_notification.html` — to admin when new qualified lead comes in
    - `lead_assigned.html` — to agent when lead is assigned
  - Email styling: clean, responsive, brand colors (blue)
- [ ] **`src/services/whatsapp.py` additions:**
  - `send_meeting_confirmation(to, lead_name, meeting_time, meet_link)` — via template
  - `send_new_lead_notification(to, lead_name, lead_phone)` — to admin/agent
- [ ] **`src/services/notification.py`:**
  - `notify_meeting_scheduled(lead, meeting, agent_phone, agent_email)`:
    1. Send email to lead
    2. Send WhatsApp to lead (if template approved)
    3. Send email to agent/admin
    4. Send WhatsApp to agent/admin
  - `notify_lead_qualified(lead)`:
    1. Send notification to admin
    2. Send assignment alert to available agent
  - Queue notifications via Celery for reliability
- [ ] **Celery Tasks:**
  - `tasks/send_email_task`
  - `tasks/send_whatsapp_task`
  - `tasks/process_agent_response_task` (for long-running AI turns)
  - `tasks/send_meeting_reminder_task` (scheduled: 1 hour before meeting)

---

### Phase 9: Admin Panel & Analytics

**Goal:** Dashboard metrics, analytics charts, agent performance.

#### Frontend Tasks

- [ ] **Dashboard Page (`pages/dashboard.tsx`):**
  - Stats cards: Total Leads (today/this week/month), Qualified Leads, Meetings Scheduled, Conversion Rate
  - Chart: Leads over time (line chart, last 30 days)
  - Chart: Lead status breakdown (pie/donut chart)
  - Recent leads widget (last 5 leads)
  - Upcoming meetings widget (next 3 meetings)
  - Agent performance (responses, conversions per agent)
- [ ] **Analytics Page (`pages/analytics/index.tsx`):**
  - Date range picker (presets: 7d, 30d, 90d, custom)
  - Conversion funnel: Ad Click → Message Sent → Data Collected → Meeting Scheduled → Converted
  - Source breakdown (Meta Ads vs Direct vs Referral)
  - Property interest distribution (which properties get most inquiries)
  - Response time metrics (avg time from lead message to agent response)
  - Agent activity heatmap (time of day when leads are most active)
- [ ] **Charts components:**
  - `lead-chart.tsx` — Recharts LineChart with time-based lead data
  - `conversion-funnel.tsx` — custom funnel visualization
  - `stats-cards.tsx` — grid of metric cards
  - `agent-performance.tsx` — bar chart comparison

#### Backend Tasks

- [ ] **`src/api/v1/analytics.py`:**
  - `GET /analytics/overview` — summary stats (totals, conversion rate)
  - `GET /analytics/leads-over-time?range=30d` — daily lead counts
  - `GET /analytics/status-breakdown` — leads grouped by status
  - `GET /analytics/source-breakdown` — leads grouped by source
  - `GET /analytics/conversion-funnel` — counts at each pipeline stage
  - `GET /analytics/agent-performance` — per-agent metrics
  - `GET /analytics/property-interest` — most inquired properties
  - `GET /analytics/response-time` — average response metrics

---

### Phase 10: Auth & RBAC

**Goal:** Role-based access control with Supabase Auth + RLS.

#### Roles

| Role        | Permissions                                                       |
|-------------|-------------------------------------------------------------------|
| `admin`     | Full access — manage users, all leads, properties, settings       |
| `agent`     | View/edit assigned leads, view properties, schedule meetings      |
| `viewer`    | Read-only access to dashboard and reports                         |

#### Tasks

- [ ] **Supabase Auth setup:**
  - Enable email/password auth
  - Custom `user_metadata` field: `role` (admin/agent/viewer)
  - Custom claims or `user_roles` table for role assignment
- [ ] **`src/api/v1/auth.py` additions:**
  - `GET /auth/me` — current user profile + role
  - `GET /auth/users` — admin only: list all users
  - `PATCH /auth/users/{id}/role` — admin only: change user role
- [ ] **Row Level Security (Supabase):**
  - `leads`: agents see only assigned leads, admins see all
  - `properties`: all authenticated users can read, only admins write
  - `meetings`: agents see own meetings, admins see all
- [ ] **Frontend route protection:**
  - `ProtectedRoute` component checks auth + role
  - Role-based navigation (admin sees "Users" in sidebar, agents don't)
  - API middleware checks role on sensitive endpoints

---

### Phase 11: Testing

**Goal:** Comprehensive test coverage for backend and frontend.

#### Backend Tests

- [ ] `tests/conftest.py` — fixtures:
  - `test_client` — FastAPI TestClient
  - `mock_supabase` — mock Supabase client
  - `mock_openai` — mock OpenAI responses
  - `sample_lead`, `sample_property`, `sample_webhook_payload`
- [ ] `tests/test_whatsapp.py`:
  - Webhook verification (GET)
  - Inbound message processing
  - Message sending
  - Invalid signature handling
- [ ] `tests/test_agent.py`:
  - Agent processes greeting message
  - Agent extracts lead info
  - Agent searches properties
  - Agent schedules meeting
  - Agent handles out-of-scope queries
  - Agent respects guardrails
  - Conversation history management
- [ ] `tests/test_leads.py`:
  - CRUD operations
  - Pagination
  - Filtering
  - Authorization (agent vs admin)
- [ ] `tests/test_properties.py`:
  - CRUD operations
  - Search/filter
  - Image upload
- [ ] `tests/test_integration.py`:
  - Full flow: webhook → agent → save lead → schedule meeting → notification

#### Frontend Tests

- [ ] `vitest.config.ts` setup
- [ ] Unit tests for:
  - Stores (Zustand)
  - Schemas (Zod)
  - Hooks
  - Utility functions
- [ ] Component tests for:
  - Lead table rendering
  - Property form validation
  - Auth form validation
  - Theme switching
- [ ] Integration tests for:
  - Lead detail page
  - Dashboard data loading

#### E2E (Optional / Future)

- [ ] Playwright setup for critical flows

---

### Phase 12: CI/CD & Deployment

**Goal:** Automated testing, building, and deployment.

#### Tasks

- [ ] **GitHub Actions (`ci.yml`):**
  - Backend:
    - Run `ruff check .`
    - Run `mypy src/`
    - Run `pytest tests/`
  - Frontend:
    - Run `tsc -b` (type check)
    - Run `npm run lint`
    - Run `npm run build`
- [ ] **Docker:**
  - `backend/Dockerfile` — multi-stage: Python slim, install deps, copy src
  - `frontend/Dockerfile` — multi-stage: build with node, serve with nginx
  - `docker-compose.yml` — backend + frontend + redis (for Celery)
  - `docker-compose.prod.yml` — production overrides
- [ ] **Deployment (`deploy.yml`):**
  - Docker images to container registry (GHCR / Docker Hub)
  - Deploy to VPS / Railway / Render / Fly.io
  - Environment variable injection
  - Health check endpoints
- [ ] **`docs/DEPLOYMENT.md`:**
  - Prerequisites
  - Environment variables reference
  - Docker compose commands
  - Supabase project setup
  - Google API setup
  - WhatsApp Business API setup

---

## 5. Supabase Schema Design

### Tables

#### `leads`
```sql
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  whatsapp_phone TEXT UNIQUE NOT NULL,
  name TEXT,
  email TEXT,
  budget_min NUMERIC(12, 2),
  budget_max NUMERIC(12, 2),
  property_type TEXT,                -- apartment, villa, office, land, any
  bedrooms_min INTEGER,
  location TEXT,                     -- neighborhood/area in Dubai
  status TEXT NOT NULL DEFAULT 'new'
    CHECK (status IN ('new', 'contacted', 'qualified', 'meeting_scheduled',
                      'converted', 'lost', 'spam')),
  source TEXT NOT NULL DEFAULT 'meta_ads'
    CHECK (source IN ('meta_ads', 'manual', 'referral', 'website', 'other')),
  assigned_to UUID REFERENCES auth.users(id),
  conversation_stage TEXT DEFAULT 'greeting'
    CHECK (conversation_stage IN ('greeting', 'information_gathering', 'property_search',
                                  'property_presentation', 'scheduling', 'follow_up', 'closed')),
  notes TEXT,
  metadata JSONB DEFAULT '{}',       -- flexible field for extra data
  last_contacted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_whatsapp ON leads(whatsapp_phone);
CREATE INDEX idx_leads_assigned ON leads(assigned_to);
CREATE INDEX idx_leads_created ON leads(created_at DESC);
```

#### `conversations`
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  message_type TEXT DEFAULT 'text'
    CHECK (message_type IN ('text', 'image', 'interactive', 'template')),
  whatsapp_message_id TEXT,          -- Meta's message ID for dedup
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_conversations_lead ON conversations(lead_id);
CREATE INDEX idx_conversations_created ON conversations(created_at);
```

#### `properties`
```sql
CREATE TABLE properties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  price NUMERIC(12, 2) NOT NULL,
  property_type TEXT NOT NULL
    CHECK (property_type IN ('apartment', 'villa', 'townhouse', 'penthouse',
                             'office', 'commercial', 'land')),
  bedrooms INTEGER DEFAULT 0,
  bathrooms INTEGER DEFAULT 0,
  area_sqft NUMERIC(10, 2),
  location TEXT NOT NULL,
  latitude DECIMAL(10, 7),
  longitude DECIMAL(10, 7),
  amenities TEXT[] DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'available'
    CHECK (status IN ('available', 'sold', 'under_offer', 'coming_soon')),
  featured BOOLEAN DEFAULT false,
  images JSONB DEFAULT '[]',         -- array of {url, alt, order}
  metadata JSONB DEFAULT '{}',       -- developer name, completion year, etc.
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_properties_type ON properties(property_type);
CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_price ON properties(price);
CREATE INDEX idx_properties_location ON properties(location);
CREATE INDEX idx_properties_featured ON properties(featured) WHERE featured = true;
```

#### `meetings`
```sql
CREATE TABLE meetings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  scheduled_at TIMESTAMPTZ NOT NULL,
  duration_minutes INTEGER DEFAULT 30,
  timezone TEXT DEFAULT 'Asia/Dubai',
  google_event_id TEXT,              -- Google Calendar event ID
  meet_link TEXT,                    -- Google Meet URL
  status TEXT NOT NULL DEFAULT 'scheduled'
    CHECK (status IN ('scheduled', 'completed', 'cancelled', 'rescheduled')),
  rescheduled_from UUID REFERENCES meetings(id),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_meetings_lead ON meetings(lead_id);
CREATE INDEX idx_meetings_scheduled ON meetings(scheduled_at);
CREATE INDEX idx_meetings_status ON meetings(status);
```

#### `notifications`
```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
  type TEXT NOT NULL
    CHECK (type IN ('email_lead', 'email_agent', 'whatsapp_lead',
                    'whatsapp_agent', 'meeting_reminder')),
  channel TEXT NOT NULL CHECK (channel IN ('email', 'whatsapp')),
  recipient TEXT NOT NULL,
  subject TEXT,
  body TEXT,
  status TEXT DEFAULT 'pending'
    CHECK (status IN ('pending', 'sent', 'failed')),
  error_message TEXT,
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

#### `user_roles` (if not using auth.users metadata)
```sql
CREATE TABLE user_roles (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('admin', 'agent', 'viewer')),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

#### `settings`
```sql
CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Seed data
INSERT INTO settings (key, value) VALUES
  ('business_hours', '{"timezone": "Asia/Dubai", "weekday": {"start": "09:00", "end": "19:00"}, "friday": {"start": "14:00", "end": "19:00"}}'),
  ('agent_config', '{"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 500}'),
  ('whatsapp_config', '{"greeting_message": "Hello! Welcome to [Company Name]. I''m Sarah, your virtual real estate assistant. How can I help you today? 🏠"}');
```

---

## 6. AI Agent Flow

### Conversation Stages

```
┌──────────┐     ┌──────────────────┐     ┌──────────────────┐
│ GREETING │────>│ INFORMATION_GATH │────>│ PROPERTY_SEARCH  │
│          │     │    ERING         │     │                  │
└──────────┘     └──────────────────┘     └──────────────────┘
                                                │
                                                ▼
                                        ┌──────────────────┐
                                        │ PROPERTY_PRESENT │
                                        │   ATION          │
                                        └──────────────────┘
                                                │
                                    ┌───────────┴───────────┐
                                    ▼                       ▼
                            ┌──────────────┐       ┌──────────────┐
                            │ SCHEDULING   │       │ FOLLOW_UP    │
                            │              │       │              │
                            └──────────────┘       └──────────────┘
                                    │                       │
                                    └───────────┬───────────┘
                                                ▼
                                        ┌──────────────┐
                                        │    CLOSED    │
                                        │              │
                                        └──────────────┘
```

### Stage Details

#### 1. GREETING
- **Trigger:** First message from new lead
- **Agent says:** "Hi! Welcome to [Company Name]. I'm Sarah, your AI real estate assistant. I'd love to help you find your perfect property in Dubai. Could you tell me your name and what kind of property you're looking for?"
- **Data collected:** Name (required to proceed)
- **On failure:** If user doesn't respond with name after 2 tries, agent says "No problem! Feel free to reach out anytime. You can also browse our properties on our website." → status stays `new`

#### 2. INFORMATION_GATHERING
- **Agent asks (one at a time, naturally):**
  1. "What type of property are you looking for? (Apartment, Villa, Townhouse, Penthouse, Office space)"
  2. "What's your budget range? (e.g., 1M - 3M AED)"
  3. "How many bedrooms do you need?"
  4. "Any preferred area in Dubai? (e.g., Dubai Marina, Downtown, Palm Jumeirah, Emirates Hills)"
  5. "What's your email address so I can send you the best options?"
- **State transition:** After collecting budget + property type → move to PROPERTY_SEARCH
- **Partial data:** If user only gives partial info, search with what's available
- **Edge case:** If user says "I don't have a budget" → provide range options

#### 3. PROPERTY_SEARCH
- **Agent searches** `property_search.search()` with collected criteria
- **If results found (≤5):** Present as numbered list with key details (price, bedrooms, location, area)
- **If many results (>5):** "I found X properties matching your criteria. Here are the top 5:" then list
- **If no results:** "I couldn't find exact matches, but here are some similar options:" + list of nearby/close matches. Or ask to adjust criteria.
- **After presenting:** "Would you like to see more details on any of these? Or shall I send you the full list?"
- **User selects:** Send detailed info + images if available
- **State transition:** After showing properties → move to SCHEDULING

#### 4. SCHEDULING
- **Agent asks:** "Would you like to schedule a Google Meet video call with our specialist to see this property in more detail? We can show you a virtual tour and answer all your questions."
- **If yes:**
  - Ask for preferred date and time
  - Validate datetime (within business hours, not in the past)
  - Create Google Calendar event with Meet link
  - Send confirmation: "Perfect! Your meeting is scheduled for [date] at [time] Dubai time. Here's your Google Meet link: [link]"
  - Trigger notifications (email + WhatsApp to lead and agent)
  - Status → `meeting_scheduled`
- **If no:**
  - "No problem at all! Feel free to reach out anytime if you change your mind. I've saved your preferences and will keep you updated on new properties matching your criteria."
  - Status → `qualified`
  - Send follow-up WhatsApp in 24h with new properties (if available)

#### 5. FOLLOW_UP
- **Automatic follow-up after 24h** (if no meeting scheduled and lead is `qualified`):
  - "Hi [name]! Just checking in — we've got some new listings that match your preferences. Would you like to take another look?"
- **Manual follow-up:** Agent can initiate via dashboard

#### 6. CLOSED
- **When:** Lead converts (signed deal) or explicitly says not interested
- **Status:** `converted` or `lost`
- **Converted:** "Congratulations! 🎉 We're thrilled to have helped you find your dream property. Our team will be in touch for the next steps."
- **Lost:** "Thank you for your time! If your situation changes, we're always here to help."

### Agent Guardrails

| Situation | Response |
|-----------|----------|
| User asks for pricing outside DB | "Let me check our current listings for you." (only search DB, never hallucinate) |
| User is abusive | "I'm here to help you find a property. Let me transfer you to a human agent who can assist further." → escalate |
| User asks sensitive info | "I'm sorry, I can only assist with property inquiries. For other questions, please contact our office." |
| User switches language (Arabic) | Recognize and respond in Arabic if possible (future enhancement) |
| Multiple rapid messages | Process all, respond to the latest intent |
| Out of business hours scheduling | "I can schedule a meeting during our business hours (Sun-Thu 9AM-7PM, Fri 2PM-7PM). Would any of these times work?" |
| User says "Call me" | "I'm a chat-based assistant, but I can schedule a video call with our specialist. Would you like to set that up?" |

---

## 7. Business Rules & Edge Cases

### WhatsApp Deep Link
```
https://wa.me/971XXXXXXXXX?text=Hi%20I%27m%20interested%20in%20properties
```
- UTM parameters can be appended for tracking: `?text=...&utm_source=meta&utm_campaign=campaign_name`
- Store `utm_source`, `utm_campaign`, `utm_content` in `leads.metadata`
- This allows tracking which ad campaign generated which lead

### Meta Webhook Reliability
- Meta may send duplicate webhook events (same `message_id`)
- **Solution:** Check `whatsapp_message_id` in `conversations` table before processing
- Meta expects 200 OK within 20 seconds; use background tasks for long processing
- If webhook fails → Meta retries with exponential backoff (max 24h)

### Rate Limiting
- WhatsApp Business API: 250 messages/phone/24h (varies by tier)
- OpenAI API: tier-based rate limits
- **Solution:**
  - Queue WhatsApp sends via Celery
  - Monitor token usage and implement throttling
  - Redis-based rate limiter on webhook endpoint

### Graceful Degradation
- If OpenAI API is down:
  - Fallback message: "Thanks for your message! Our team has been notified and will get back to you shortly."
  - Flag lead for human follow-up
  - No data loss — messages are stored in DB
- If Google Calendar API is down:
  - Store meeting request in DB with status `pending` 
  - Retry with Celery scheduled task every 5 min for up to 2h
  - If still failing → notify admin
- If WhatsApp API is down:
  - Log error, retry up to 3 times
  - Notify admin via email
  - Messages stay queued in DB

### Data Retention
- Conversations: retain for 2 years (adjust for compliance)
- Leads: never delete, only soft-status (lost, spam)
- Meeting records: retain for 1 year after meeting date
- Export capability: CSV export from dashboard

### Compliance Considerations
- **UAE Data Protection Law:** Ensure user data is handled per PDPL
- **WhatsApp opt-in:** Users initiate contact → implicit consent
- **Email marketing:** Include unsubscribe link in all emails
- **Data minimization:** Only collect data needed for the service

---

## Phase Sequencing & Dependencies

```
Phase 0 ────► Phase 1 ──► Phase 5 ──► Phase 7 ──► Phase 9
   │              │           │            │
   │              ▼           ▼            ▼
   └────────► Phase 2 ──► Phase 4     Phase 8
                  │           │
                  ▼           ▼
              Phase 3     Phase 6
                             │
                             ▼
                        Phase 10
                             │
                             ▼
                        Phase 11
                             │
                             ▼
                        Phase 12
```

### Recommended Parallel Tracks

| Track | Phases | Who |
|-------|--------|-----|
| **Foundation** | 0 → 1 → 2 → 3 | Backend + Frontend (sequential) |
| **Core AI** | 4 → 6 → 7 | Backend heavy (after foundation) |
| **Dashboard** | 5 → 8 → 9 | Frontend heavy (can parallel with Core AI) |
| **Hardening** | 10 → 11 → 12 | After all features are stable |

---

> **Note:** This plan is a living document. Each phase should produce a working increment that can be tested. Prioritize the end-to-end flow (Phase 4) early so you can validate the core value proposition before building the full dashboard.
