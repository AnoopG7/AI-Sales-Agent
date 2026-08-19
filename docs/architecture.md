# Architecture — System Design

## System Context Diagram

```
+------------------------------------------------------------------+
|                        META ADS PLATFORM                          |
|                   (Facebook / Instagram)                          |
|          Click -> WhatsApp deep link with pre-filled message      |
+----------------------------+-------------------------------------+
                             |
                             v
+------------------------------------------------------------------+
|                     WHATSAPP BUSINESS PLATFORM                    |
|                    (Meta Cloud API v23.0)                        |
|                                                                   |
|  Inbound: User sends message to business number                  |
|  Outbound: API sends text/interactive messages to user           |
|  Webhook: POST /api/v1/whatsapp/webhook                          |
+----------------------------+-------------------------------------+
                             | POST webhook payload (JSON)
                             | X-Hub-Signature-256 header
                             v
+------------------------------------------------------------------+
|                     BACKEND APPLICATION                           |
|                  FastAPI + Python 3.12 + PostgreSQL               |
|                                                                   |
|  +------------------------+  +--------------------------------+  |
|  |    WHATSAPP WEBHOOK    |  |         AI AGENT               |  |
|  |                        |  |                                |  |
|  | 1. Verify signature    |  | process_message() loop:       |  |
|  | 2. Parse payload       |  |   - Groq function calling     |  |
|  | 3. Dedup message ID    |  |   - 8 tools                   |  |
|  | 4. Get/create lead     |  |   - Max 10 rounds             |  |
|  | 5. Store user msg      |  |   - Parallel execution        |  |
|  | 6. Call process_msg()  |  |   - Token tracking            |  |
|  | 7. Send WhatsApp reply |  +--------------------------------+  |
|  | 8. Store agent reply   |                                     |
|  +------------------------+  +--------------------------------+  |
|                               |     TOOL EXECUTORS             |  |
|                               |                                |  |
|                               | search_properties() --+        |  |
|                               | list_all_properties() --+      |  |
|                               | get_property_details() --+     |  |
|                               | update_lead_info() ------+     |  |
|                               | update_lead_stage() -----+     |  |
|                               | schedule_meeting() ------+     |  |
|                               | send_email() ------------+     |  |
|                               | transfer_to_human() -----+     |  |
|                               +--------------------------------+  |
|                                                                   |
|  +------------------------+  +--------------------------------+  |
|  |       API LAYER        |  |      SERVICE LAYER             |  |
|  |  6 route groups        |  |  5 services                    |  |
|  |  Auth, Leads, Props,   |  |  Lead, Property, Meeting,      |  |
|  |  Meetings, Analytics,  |  |  Auth, Analytics               |  |
|  |  WhatsApp              |  +--------------------------------+  |
|  +------------------------+                                     |
|                                                                   |
|  +------------------------+  +--------------------------------+  |
|  |     REPOSITORY LAYER   |  |     ORM MODELS                 |  |
|  |  5 repos, SQLAlchemy   |  |  7 tables, Mapped style       |  |
|  +------------------------+  +--------------------------------+  |
|                                                                   |
+----------------------------+-------------------------------------+
                             | asyncpg (TCP)
                             v
+------------------------------------------------------------------+
|                     POSTGRESQL 16                                 |
|                     Docker Container: leadgen-db                 |
|                                                                   |
|  Tables:                                                         |
|  +------------+  +------------+  +-------------------+           |
|  | admin_users|  |   leads    |  |   properties      |           |
|  +------------+  +------------+  +-------------------+           |
|  | 7 columns   |  | 19 columns |  | 16 columns        |          |
|  | UNIQUE email |  | INDEX phone|  | INDEX price/type  |          |
|  +------------+  +------------+  +-------------------+           |
|                                                                   |
|  +------------+  +-----------+  +--------------+  +-----------+  |
|  |conversatns |  | meetings  |  |notifications  |  | settings  |  |
|  +------------+  +-----------+  +--------------+  +-----------+  |
|                                                                   |
|  Volume: pgdata (Docker named volume)                            |
+------------------------------------------------------------------+
                             |
                             v
+------------------------------------------------------------------+
|                     FRONTEND APPLICATION                          |
|                  React 19 + Vite 8 + TypeScript 6                |
|                                                                   |
|  +------------------------------------------------------------+  |
|  |                    BROWSER                                   |  |
|  |                                                             |  |
|  |  Router (React Router v7):                                  |  |
|  |    AuthLayout: /login                                       |  |
|  |    DashboardLayout: /, /leads, /properties, /meetings,      |  |
|  |                    /analytics, /settings                     |  |
|  |                                                             |  |
|  |  AppShell: Sidebar + Header + Main                          |  |
|  |    Sidebar: collapsible, Lucide icons, active highlighting   |  |
|  |    Header: breadcrumbs, search, notifications, user menu     |  |
|  |    Theme: light/dark/system via next-themes                  |  |
|  |                                                             |  |
|  |  State: Zustand (authStore, filterStore, sidebarStore)      |  |
|  |  API: Axios baseURL /api/v1, interceptor for Bearer token   |  |
|  |  Server State: TanStack Query (5min staleTime, 1 retry)     |  |
|  |  Forms: React Hook Form + Zod (real-time validation)        |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

## Request Flows

### Flow 1: WhatsApp Message Processing (Inbound)

```
User sends WhatsApp
      |
      v
Meta Cloud API receives message
      |
      v
POST /api/v1/whatsapp/webhook (with X-Hub-Signature-256)
      |
      +---> [whatsapp.py] Verify HMAC-SHA256 signature
      |       If WHATSAPP_APP_SECRET is empty: skip (dev mode)
      |       If signature mismatch: return 403 Forbidden
      |
      +---> [whatsapp.py] Parse webhook payload
      |       Extract: sender_phone, message_text, message_id, message_type
      |
      +---> [conversation_repo.py] Check message_exists(message_id)
      |       If exists: return 200 OK (idempotency)
      |
      +---> [lead_service.py] get_or_create_by_phone(sender_phone, source="meta_ads")
      |       If not found: create new Lead with phone + source
      |       Return: Lead object
      |
      +---> [conversation_repo.py] add_message(lead_id, role="user", content=text)
      |       Store message in conversations table
      |
      +---> [orchestrator.py] process_message(lead_id, text, lead, session)
      |       |
       |       +---> Load 10 most recent conversation messages
      |       +---> Build Groq messages array (system + history + user)
      |       +---> Enter main loop (max 10 rounds):
      |       |       +---> Call Groq chat_completion with tools
      |       |       +---> If tool_calls: execute all, append results, continue
      |       |       +---> If content: return as response
      |       +---> If exhausted: final Groq call with tools=None
      |       +---> Return response string (or fallback)
      |
      +---> [whatsapp.py] send_text_message(sender_phone, response)
      |       POST to graph.facebook.com/v23.0/{phone_id}/messages
      |       Body: {"messaging_product": "whatsapp", "to": phone, ...}
      |
      +---> [conversation_repo.py] add_message(lead_id, role="assistant", content=response)
      |
      +---> Return {"status": "ok"} with 200 OK
```

### Flow 2: Dashboard API Request (Authenticated)

```
Browser makes API call
      |
      v
Axios interceptor adds Authorization: Bearer <token>
      |
      v
Vite proxy (dev) / Nginx (prod) -> http://localhost:8000/api/v1/...
      |
      v
[deps.py] get_current_user():
      +---> Extract Bearer token from Authorization header
      +---> decode_access_token(token) -> payload {sub: user_id, exp: ...}
      +---> select(AdminUser).where(AdminUser.id == payload["sub"])
      +---> Return AdminUser or raise UnauthorizedException
      |
      v
[Endpoint handler] e.g., GET /leads
      +---> Parse query params (page, page_size, status, etc.)
      +---> Call Service method
      |
      v
[Service] e.g., lead_service.list_leads()
      +---> Validate inputs
      +---> Call Repository method
      |
      v
[Repository] e.g., lead_repo.list_all()
      +---> Build SQLAlchemy query with filters
      +---> Execute: select(Lead).where(...).offset().limit()
      +---> Execute: select(func.count()).select_from(subquery) for total
      +---> Return (list[Lead], total_count)
      |
      v
Response: PaginatedResponse with data + pagination metadata
```

### Flow 3: AI Agent Tool Execution

```
Groq returns tool_calls in assistant response
      |
      v
[orchestrator.py] Append ONE assistant message with ALL tool_calls:
      messages.append({
          "role": "assistant",
          "content": null,  // or text alongside tools
          "tool_calls": [
              {"id": "call_1", "type": "function",
               "function": {"name": "update_lead_info",
                            "arguments": '{"name": "Rahul", "budget_max": 3000000}'}},
              {"id": "call_2", "type": "function",
               "function": {"name": "update_lead_stage",
                            "arguments": '{"stage": "property_search"}'}},
          ]
      })
      |
      v
Execute EACH tool call sequentially:
      |
      +---> [tools.py] execute_tool("update_lead_info", args, lead_id, session)
      |       +---> LeadService.update_lead(lead_id, LeadUpdate(**args))
      |       +---> LeadRepository.update(id, update_data)
      |       +---> Return: "Updated: name, budget_max"
      |       +---> messages.append({"role": "tool", "tool_call_id": "call_1", "content": result})
      |
      +---> [tools.py] execute_tool("update_lead_stage", args, lead_id, session)
      |       +---> LeadService.update_lead(lead_id, LeadUpdate(conversation_stage="property_search"))
      |       +---> Return: "Stage updated to: property_search"
      |       +---> messages.append({"role": "tool", "tool_call_id": "call_2", "content": result})
      |
      v
Continue loop -> Call Groq again with updated messages
```

## Module Dependency Graph

```
main.py
  |
  +-- core/config.py          (no deps)
  +-- core/database.py        (depends on config)
  +-- core/exceptions.py      (no deps)
  +-- core/logging.py         (no deps)
  +-- core/security.py        (depends on config)
  +-- core/enums.py           (no deps)
  |
  +-- api/v1/router.py
  |     |
  |     +-- api/v1/deps.py
  |     |     +-- core/database.py
  |     |     +-- core/security.py
  |     |     +-- models/orm/admin_user.py
  |     |
  |     +-- api/v1/endpoints/auth.py
  |     |     +-- services/auth_service.py
  |     |           +-- repositories/admin_user_repo.py
  |     |           +-- core/security.py
  |     |
  |     +-- api/v1/endpoints/leads.py
  |     |     +-- services/lead_service.py
  |     |           +-- repositories/lead_repo.py
  |     |           +-- models/lead.py
  |     |
  |     +-- api/v1/endpoints/properties.py
  |     |     +-- services/property_service.py
  |     |           +-- repositories/property_repo.py
  |     |           +-- models/property.py
  |     |
  |     +-- api/v1/endpoints/meetings.py
  |     |     +-- services/meeting_service.py
  |     |           +-- repositories/meeting_repo.py
  |     |           +-- models/meeting.py
  |     |
  |     +-- api/v1/endpoints/analytics.py
  |     |     +-- services/analytics_service.py
  |     |           +-- repositories/lead_repo.py
  |     |           +-- repositories/meeting_repo.py
  |     |
  |     +-- api/v1/endpoints/whatsapp.py
  |           +-- integrations/whatsapp.py (send, parse, verify)
  |           +-- services/lead_service.py
  |           +-- repositories/conversation_repo.py
  |           +-- agent/orchestrator.py
  |                 +-- agent/prompts.py
  |                 +-- agent/tools.py
  |                 |     +-- services/lead_service.py
  |                 |     +-- services/property_service.py
  |                 |     +-- services/meeting_service.py
  |                 |     +-- integrations/email.py
  |                 +-- integrations/llm_client.py
  |                 +-- repositories/conversation_repo.py
  |                 +-- models/orm/lead.py (for _build_context)
  |
  +-- models/orm/*.py          (7 models, reference each other via FK)
  +-- models/*.py              (Pydantic schemas, no ORM deps)
  +-- utils/helpers.py         (no deps)
```

## Deployment Architecture

```
                         +-----------------------+
                         |   DNS / Load Balancer  |
                         |   (Cloudflare / Nginx) |
                         +----------+------------+
                                    |
                    +---------------+---------------+
                    |                               |
            +-------v-------+             +---------v--------+
            |   Frontend    |             |     Backend      |
            |  Nginx + SPA  |             |  Uvicorn + ASGI  |
            |  Port 80/443  |             |  Port 8000       |
            +---------------+             +--------+---------+
                                                    |
                                           +--------v---------+
                                           |   PostgreSQL 16   |
                                           |   Port 5432       |
                                           +------------------+
```

**Current state:** Only PostgreSQL is containerized. Backend runs via `uv run uvicorn`. Frontend runs via `npm run dev`. Dockerfiles for backend and frontend are planned.

## Data Flow Summary

| Flow | Trigger | Latency | Components |
|------|---------|---------|------------|
| WhatsApp inbound | User sends message | 1-3s | Webhook -> Agent -> Groq -> Tools -> WhatsApp API |
| Dashboard read | Admin opens page | 100-500ms | Browser -> Vite proxy -> FastAPI -> Repo -> DB |
| Dashboard write | Admin creates/updates | 200-600ms | Browser -> API -> Service -> Repo -> DB |
| Agent tool execution | Groq requests tool | 50-200ms per tool | Tools -> Service -> Repo -> DB |
| Email sending | Agent calls send_email | 100-500ms | Tools -> EmailClient -> SMTP server |

## Security Boundaries

| Boundary | Protection | Notes |
|----------|------------|-------|
| External (Internet -> Backend) | CORS, rate limiting (planned) | CORS allows * in dev, FRONTEND_URL in prod |
| WhatsApp -> Webhook | HMAC-SHA256 signature | Skips in dev when WHATSAPP_APP_SECRET is empty |
| Frontend -> API | JWT Bearer token | 24h expiry, verified on every request |
| API -> Database | TCP connection (local) | No TLS in dev (localhost only) |
| Passwords | bcrypt | No plaintext storage |
| Groq API Key | Environment variable | Never logged or exposed |
