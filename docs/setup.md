# Setup Guide

## Prerequisites

### System Requirements

| Tool | Version | Check Command | Install |
|------|---------|---------------|---------|
| Python | 3.12+ | `python3 --version` | python.org or pyenv |
| Node.js | 20+ | `node --version` | nodejs.org or nvm |
| npm | 10+ | `npm --version` | Comes with Node.js |
| Docker Desktop | Latest | `docker compose version` | docker.com |
| uv | Latest | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh | sh` |

### Ports Required

| Port | Service | Purpose |
|------|---------|---------|
| 5432 | PostgreSQL | Database |
| 8000 | Backend | FastAPI + API |
| 5173 | Frontend | Vite dev server |

Make sure these ports are free before starting.

## Step-by-Step Setup

### Step 1: Start PostgreSQL

```bash
# Navigate to backend directory
cd backend

# Start PostgreSQL 16 in Docker
docker compose up -d
# Expected output: [+] Running 2/2
#   Container leadgen-db  Started
#   Volume pgdata         Created

# Verify PostgreSQL is ready
docker compose exec db pg_isready -U postgres
# Expected: /var/run/postgresql:5432 - accepting connections

# Optional: verify database exists
docker compose exec db psql -U postgres -d leadgen -c "\dt"
# Expected: "No relations found." (tables not yet created)
```

**What this does:**
- Downloads `postgres:16-alpine` image (first time only)
- Creates container `leadgen-db` on port 5432
- Creates database `leadgen` with user `postgres` / password `postgres`
- Names volume `pgdata` for data persistence (survives container restart)
- Health check every 5 seconds using `pg_isready`

**Troubleshooting:**
- Port 5432 already in use: `lsof -i :5432` to find the process, stop it, then retry
- Docker daemon not running: Start Docker Desktop application
- Permission denied: You may need to use `sudo` or add user to docker group

### Step 2: Configure Backend

```bash
# Still in backend/
cp .env.example .env
```

**Edit `.env` and set these minimum variables:**

```bash
# REQUIRED: Get from https://console.groq.com
GROQ_API_KEY=gsk_your_actual_key_here

# RECOMMENDED: Change for production (min 32 chars)
SECRET_KEY=your-random-secret-key-at-least-32-characters-long
```

All other variables have safe defaults for local development:
- `DATABASE_URL` defaults to local Docker PostgreSQL
- `WHATSAPP_APP_SECRET` defaults to empty (skips webhook verification)
- `SMTP_*` defaults to empty (logs emails to console)
- `GOOGLE_SERVICE_ACCOUNT_JSON` defaults to empty (Calendar is stubbed)

### Step 3: Install Backend Dependencies

```bash
# Still in backend/
uv sync
```

**What this does:**
- Creates `.venv/` virtual environment
- Reads `pyproject.toml` and installs all dependencies
- Creates `uv.lock` with locked versions
- Installs dev dependencies (pytest, ruff, mypy)

**Expected output:** Should complete without errors. Look for "Installed XX packages" at the end.

**Troubleshooting:**
- `uv: command not found`: Install uv first
- `python version requirement not met`: You need Python 3.12+. Check with `python3 --version`
- Dependency conflicts: Run `uv lock` to regenerate lock file, then `uv sync` again

### Step 4: Run Database Migrations

```bash
# Still in backend/
PYTHONPATH=. .venv/bin/python -m alembic upgrade head
```

**What this does:**
- Sets `PYTHONPATH=.` so Python can find the `app` package
- Runs Alembic in online mode (connects to the database)
- `upgrade head` applies all pending migrations
- First migration: creates all 7 tables with indexes and constraints
- Second migration: fixes `last_contacted_at` timezone column

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 5ed85bcb3b71, initial_schema
INFO  [alembic.runtime.migration] Running upgrade 5ed85bcb3b71 -> 7740dccae86c, fix_last_contacted_at_timezone
```

**Verify:**
```bash
docker compose exec db psql -U postgres -d leadgen -c "\dt"
# Should show 7 tables: admin_users, conversations, leads, meetings, notifications, products, settings

docker compose exec db psql -U postgres -d leadgen -c "\di"
# Should show all indexes
```

**Troubleshooting:**
- `FATAL: database "leadgen" does not exist`: Run `docker compose down -v && docker compose up -d` to recreate
- `ModuleNotFoundError: No module named 'app'`: You forgot `PYTHONPATH=.`
- Can't connect to database: Check PostgreSQL is running (`docker ps | grep leadgen-db`)

### Step 5: Seed the Product Catalog

```bash
# Still in backend/
PYTHONPATH=. .venv/bin/python scripts/seed_products.py
```

**What this does:**
- Connects to PostgreSQL using the same database URL
- Checks if products already exist (skips if any found)
- Inserts a sample B2B SaaS catalog of 11 products across 5 categories (CRM, analytics, automation, support, add-ons), with monthly, annual and one-time pricing and different seat ranges, so the agent has something to recommend. Replace it with your own catalog.

**Expected output:**
```
✅ 11 products inserted successfully.
```

Or if already seeded:
```
Products already seeded. Skipping.
```

**Verify:**
```bash
docker compose exec db psql -U postgres -d leadgen -c "SELECT COUNT(*) FROM products;"
# Should return: 11
```

### Step 6: Start Backend Server

```bash
# Still in backend/
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**What this does:**
- Starts uvicorn ASGI server on port 8000
- `--reload`: auto-restarts on file changes (development only)
- `--host 0.0.0.0`: accessible from other devices on network (not just localhost)
- `--port 8000`: standard port for this project

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     setup_logging     environment=development
INFO:     init_db           pool_size=5 max_overflow=10
INFO:     app_starting      environment=development cors_origins=['*'] version='0.1.0'
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify the API is running:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"0.1.0","environment":"development"}
```

Also verify: Open http://localhost:8000/docs in a browser — should show Swagger UI with all 6 route groups.

### Step 7: Setup Frontend

In a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**What `npm install` does:**
- Reads `package.json` for all dependencies (React 19, Vite 8, shadcn/ui, etc.)
- Creates `node_modules/` with all packages
- Creates `package-lock.json` with locked versions

**What `npm run dev` does:**
- Starts Vite dev server on port 5173
- Enables HMR (Hot Module Replacement) for instant feedback
- Proxies `/api` requests to `http://localhost:8000` (configured in `vite.config.ts`)

**Expected output:**
```
VITE v8.x.x  ready in 150ms
  Local:   http://localhost:5173/
```

**Verify:**
- Open http://localhost:5173 in a browser
- You should see the homepage with all components rendered (showcase page)
- API proxy should work: the page makes requests to `/api/v1/products` which Vite proxies to `localhost:8000`

### Step 8: Create an Admin User

```bash
# In a new terminal
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123", "name": "Admin"}'
```

**Expected output:**
```json
{"id": "uuid", "email": "admin@example.com", "name": "Admin", "role": "admin", "created_at": "..."}
```

**Login to get a JWT token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

Save the `access_token` from the response — you'll need it to test authenticated endpoints.

### Step 9: Test Authenticated API

```bash
# Set your token
TOKEN="eyJhbGciOiJIUzI1NiIs..."

# List products (should show the 11 seeded products)
curl http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $TOKEN"

# List leads (should be empty initially)
curl http://localhost:8000/api/v1/leads \
  -H "Authorization: Bearer $TOKEN"

# Get analytics overview
curl http://localhost:8000/api/v1/analytics/overview \
  -H "Authorization: Bearer $TOKEN"
```

## Environment Variables Reference

### Backend (.env)

#### Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `development` | Controls CORS, docs, debug mode. Values: `development`, `staging`, `production` |
| `SECRET_KEY` | Recommended | `change-me-in-production-min-32-chars` | JWT signing key. Must be 32+ chars in production. Generate: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity. Values: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `FRONTEND_URL` | No | `http://localhost:5173` | CORS origin in production. In development, all origins are allowed |
| `BACKEND_URL` | No | `http://localhost:8000` | Self-referencing URL for callbacks |

#### Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `postgresql+asyncpg://postgres:postgres@localhost:5432/leadgen` | PostgreSQL connection string with async driver. Format: `postgresql+asyncpg://user:pass@host:port/dbname` |

#### Business

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COMPANY_NAME` | No | `Acme Cloud` | Company the agent represents |
| `AGENT_NAME` | No | `Ava` | Name the agent introduces itself with |
| `DEFAULT_CURRENCY` | No | `USD` | Currency the product catalog is priced in |

#### Groq (AI)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | **Yes** | — | Groq API key from https://console.groq.com. Free tier: 100K tokens/day |
| `GROQ_MODEL` | No | `openai/gpt-oss-120b` | Model ID. A lighter option is `openai/gpt-oss-20b` (separate daily limit, weaker tool use) |

#### WhatsApp

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WHATSAPP_TOKEN` | No | `""` | Meta Cloud API access token. Created in Meta Business Suite > WhatsApp > API Setup |
| `WHATSAPP_PHONE_NUMBER_ID` | No | `""` | Phone number ID from Meta Business Suite |
| `WHATSAPP_VERIFY_TOKEN` | No | `""` | Custom string you define. Must match what you enter in Meta webhook setup |
| `WHATSAPP_APP_SECRET` | No | `""` | Meta App Secret from Meta Developer Portal. Set to `""` to skip signature verification in dev |
| `WHATSAPP_API_VERSION` | No | `v23.0` | Meta Graph API version |

#### Google Calendar

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | No | `""` | Base64-encoded Google service account JSON key. Leave empty for dev (Calendar is stubbed) |
| `GOOGLE_CALENDAR_ID` | No | `primary` | Calendar ID to create events in. Usually `primary` for the service account's calendar |
| `GOOGLE_CALENDAR_TIMEZONE` | No | `UTC` | Default timezone for calendar events |

#### Email (SMTP)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SMTP_HOST` | No | `""` | SMTP server hostname. Leave empty to log emails to console. Examples: `smtp.gmail.com`, `smtp-relay.brevo.com` |
| `SMTP_PORT` | No | `587` | SMTP port. 587 for STARTTLS, 465 for SSL |
| `SMTP_USER` | No | `""` | SMTP authentication username |
| `SMTP_PASS` | No | `""` | SMTP authentication password (or app password) |
| `FROM_EMAIL` | No | `noreply@example.com` | From address for outgoing emails |

#### Admin

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ADMIN_EMAIL` | No | `""` | Admin email for notifications |
| `ADMIN_WHATSAPP_NUMBER` | No | `""` | Admin WhatsApp number for alerts (digits only, with country code, e.g. 14155550132) |

### Frontend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | No | `/api/v1` | API base URL. Relative path works because Vite proxies /api to backend |

## Alembic Commands

```bash
# Run all pending migrations
PYTHONPATH=. .venv/bin/python -m alembic upgrade head

# Rollback one step
PYTHONPATH=. .venv/bin/python -m alembic downgrade -1

# Rollback to a specific revision
PYTHONPATH=. .venv/bin/python -m alembic downgrade <revision_id>

# Create a new auto-generated migration (after changing ORM models)
PYTHONPATH=. .venv/bin/python -m alembic revision --autogenerate -m "description_of_change"

# View migration history
PYTHONPATH=. .venv/bin/python -m alembic history

# View current migration
PYTHONPATH=. .venv/bin/python -m alembic current

# Show SQL for a migration (without applying it)
PYTHONPATH=. .venv/bin/python -m alembic upgrade head --sql
```

## Lint & Type Check

```bash
# Lint backend
cd backend
uv run ruff check app/

# Auto-fix lint issues
uv run ruff check app/ --fix

# Type check (strict mode)
uv run mypy app/
```

## Testing

```bash
# Backend tests
cd backend
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ -v --cov=app

# Specific test file
uv run pytest tests/test_agent.py -v

# Frontend (when tests are added)
cd frontend
npm run test
```

## Agent CLI

See [`agent.md`](agent.md#agent-cli) for full CLI reference including commands table and example session.

```bash
cd backend
PYTHONPATH=. .venv/bin/python scripts/agent_cli.py
```

## Docker Commands

```bash
# Start PostgreSQL
docker compose up -d

# Stop PostgreSQL (keeps data)
docker compose stop

# Stop and remove container (keeps data volume)
docker compose down

# Stop and remove everything including data (WARNING: destroys data)
docker compose down -v

# View logs
docker compose logs -f db

# Execute SQL query directly
docker compose exec db psql -U postgres -d leadgen -c "SELECT * FROM leads;"

# Interactive psql shell
docker compose exec db psql -U postgres -d leadgen

# Check container health
docker compose ps
```

## Troubleshooting

### Database

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `Cannot connect to PostgreSQL` | Container not running | `docker compose up -d` and wait 5 seconds |
| `FATAL: database "leadgen" does not exist` | Container freshly created | `docker compose down -v && docker compose up -d` |
| `Alembic can't find app module` | Wrong working directory | Must run from `backend/` directory |
| `Alembic can't find modules` | PYTHONPATH missing | Use `PYTHONPATH=.` before every Python command |
| Migration fails | Schema mismatch | `docker compose down -v && docker compose up -d && PYTHONPATH=. .venv/bin/python -m alembic upgrade head` |

### Backend

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `uv: command not found` | uv not installed | `curl -LsSf https://astral.sh/uv/install.sh | sh` |
| `uv sync` fails | Wrong Python version | Ensure Python 3.12+: `uv python pin 3.12` |
| `uv run uvicorn` fails | Dependencies not installed | Run `uv sync` first |
| Port 8000 in use | Another process | `kill -9 $(lsof -ti:8000)` or use different port |

### Groq / AI Agent

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Groq API errors | Missing or invalid GROQ_API_KEY | Check `.env` has correct API key |
| Agent returns fallback message | Groq rate limited (429) | Check token usage logs. Wait for daily reset or get new API key |
| Agent doesn't use tools | Prompt issue | Check orchestrator logs for tool_calls count |
| Agent returns wrong info | System prompt overflow | Check prompt_tokens in logs — may exceed context window |
| `401 Unauthorized` from Groq | Invalid API key | Verify key at console.groq.com |

### WhatsApp

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Webhook returns "ignored" | Signature verification fails | Set `WHATSAPP_APP_SECRET=""` in development |
| Webhook returns 403 | Signature mismatch in production | Check WHATSAPP_APP_SECRET matches Meta portal |
| Messages not sending | Invalid WHATSAPP_TOKEN | Generate new token in Meta Business Suite |
| Webhook not receiving | Meta not configured | Set up webhook URL in Meta Developer Portal |

### Frontend

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `npm install` fails | Old Node.js version | Use Node 20+: `node --version` |
| Frontend can't reach API | Backend not running | Start backend on port 8000 |
| API returns 401 in browser | Token expired/missing | Login again via /auth/login |
| CORS errors | Backend not running | Vite proxy handles CORS in dev — backend must be running |
| Blank page | Build error | Check browser console for errors |
