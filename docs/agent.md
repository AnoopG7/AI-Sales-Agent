# AI Sales Agent

The agent is the core of the WhatsApp pipeline. It answers inbound messages, qualifies the lead, recommends plans from the product catalog, books demo calls, sends follow-up emails, and hands off to a human when needed. It runs on Groq function calling (`openai/gpt-oss-120b`) or a local Ollama model through the same OpenAI-compatible client.

There is no LangChain or LangGraph: the orchestrator is a small, explicit loop (`backend/app/agent/orchestrator.py`), which keeps every step of the conversation inspectable.

## Persona

The persona is configured through environment variables, so the same agent can sell for any company:

| Setting | Default | Purpose |
|---------|---------|---------|
| `AGENT_NAME` | `Ava` | Name the agent introduces itself with |
| `COMPANY_NAME` | `Acme Cloud` | Company the agent represents |
| `DEFAULT_CURRENCY` | `USD` | Currency the catalog is priced in |

Style rules (from `backend/app/agent/prompts.py`):

- Warm, concise and professional, like a helpful account executive on WhatsApp
- 2-5 sentences per message, emojis used sparingly
- Replies in the lead's language when it can, English by default
- Never invents prices, features or plans: all catalog data comes from tools
- Never quotes discounts or custom pricing; hands those to a human instead

## Conversation Stages

The stage is stored as `conversation_stage` on the lead. Each stage injects its own instruction into the system prompt.

| Stage | When | Agent's goal |
|-------|------|-------------|
| `greeting` | New lead | Welcome them, introduce itself, ask what brought them here |
| `qualification` | After greeting | Learn company, team size, use case, budget and timeline, one question at a time, saving each with `update_lead_info` |
| `discovery` | Requirements known | Search the catalog and present the top 1-3 fits with price, billing period, seat range and the most relevant feature |
| `proposal` | Interested in a specific plan | Use `get_product_details`, explain how it fits their use case, suggest a demo |
| `demo_scheduling` | Wants a demo | Ask for date, time and timezone, book with `schedule_meeting`, confirm |
| `follow_up` | Returning lead | Reference what they said before; offer a different plan or a demo |
| `closed` | Conversation done | Thank them and leave the door open |

## Tools (9)

All tool calls in one model response are executed in order, and the orchestrator appends one assistant message containing every `tool_call` followed by one `tool` message per result (the format OpenAI-compatible APIs require for parallel tool calls).

| # | Tool | Parameters | What it does |
|---|------|-----------|--------------|
| 1 | `search_products` | `category`, `keyword`, `min_price`, `max_price`, `team_size` (all optional) | Filters active products. `team_size` matches plans whose seat range fits the team (`min_seats <= team_size <= max_seats`, or no cap). Featured plans rank first, then cheapest. Returns up to 5. |
| 2 | `list_all_products` | none | Lists up to 20 active products |
| 3 | `get_product_details` | `product_id` | Full details: price, billing period, seats, features, description |
| 4 | `convert_currency` | `amount`, `from_currency`, `to_currency` | Live rate from exchangerate.host, with approximate USD-based fallback rates if the API is down |
| 5 | `update_lead_info` | `name`, `email`, `company`, `team_size`, `product_interest`, `budget_min`, `budget_max`, `notes` | Saves what the agent learned. Passing `null` clears a field (uses `exclude_unset`) |
| 6 | `update_lead_stage` | `stage` | Moves the lead to one of the 7 stages |
| 7 | `schedule_meeting` | `scheduled_at` (ISO 8601), `duration_minutes`, `notes` | Creates a meeting record for the demo call |
| 8 | `send_email` | `to`, `subject`, `body` | Sends a plan summary or meeting details over SMTP (logged to console in development) |
| 9 | `transfer_to_human` | `reason` | Returns a handoff message for custom pricing, contracts, security reviews or explicit requests |

Example tool output (`search_products` with `category=crm, team_size=25`):

```
Found 1 matching products:
- CRM Growth | crm | USD 39.00/seat/mo | 5-100 seats | ID: 1b0e244d-...
```

## Orchestrator Flow

```
process_message(lead_id, message_text, lead, session) -> str

1. Load the last MAX_HISTORY_MESSAGES (10) messages for the lead
2. Build messages: [system prompt, *history, user message]
     system prompt = persona + lead profile + current stage instruction + guardrails
3. Loop up to MAX_TOOL_ROUNDS (10):
     - call the LLM with the 9 tool schemas (retry up to 3x on 429 with backoff)
     - no tool calls + text      -> return the text
     - no tool calls + empty     -> nudge the model and continue
     - tool calls                -> append one assistant message with all tool_calls,
                                    execute each tool, append one tool message per result
     - if a lead-modifying tool ran (update_lead_info, update_lead_stage, schedule_meeting):
         reload the lead and rebuild messages[0] so the next round sees fresh data
4. Rounds exhausted -> one final call with tools disabled to force a text reply
5. Still nothing    -> fixed fallback message
```

### Why the system prompt is rebuilt mid-loop

Without the rebuild, the model keeps seeing the lead profile from the start of the turn. After it saves `team_size=25` and then searches, it could still believe the team size is unknown and ask again. Reloading the lead after any state-changing tool keeps the model's view consistent with the database within a single turn.

### Why the loop is capped

`MAX_TOOL_ROUNDS = 10` and `MAX_HISTORY_MESSAGES = 10` bound the worst-case token cost of one inbound message, which matters on free-tier rate limits. The final tools-disabled call guarantees the lead always gets a reply.

## System Prompt Assembly

`render_system_prompt()` in `prompts.py` builds the prompt from four parts:

1. **Persona and workflow**: who the agent is, how it talks, the 6-step sales workflow and tool rules
2. **Lead profile**: built from the database by `_build_context()`, showing what is known and what is missing:

```
- Name: Jordan Lee
- Phone: 14155550132
- Email: Not collected yet
- Budget: Up to USD 1,500
- Company: Brightline
- Team size (seats): 25
- Product interest: forecasting
- Lead status: new
- Conversation stage: discovery
```

3. **Stage instruction**: the behavior for the current stage (table above)
4. **Guardrails**: don't repeat failed searches, don't share staff contact details, ask for the currency when a budget has none, treat team size as seats

## Agent CLI

`scripts/agent_cli.py` runs the same code path as the WhatsApp webhook against the real database, which makes it the fastest way to test prompt changes.

```
cd backend
PYTHONPATH=. .venv/bin/python scripts/agent_cli.py
```

| Command | Example | Description |
|---------|---------|-------------|
| `list` | `list` | Show all leads |
| `select <n>` | `select 1` | Select a lead by list number |
| `new <phone>` | `new +14155550132` | Create a lead |
| `say <msg>` | `say We're a 25-person sales team looking for a CRM` | Send a message as the selected lead |
| `history` | `history` | Show the conversation |
| `state` | `state` | Show every field on the lead |
| `help` / `quit` | | |

## LLM Client

`backend/app/integrations/llm_client.py` wraps `openai.AsyncOpenAI` for both providers:

- `LLM_PROVIDER=groq` uses `https://api.groq.com/openai/v1` with `GROQ_MODEL`
- `LLM_PROVIDER=ollama` uses `http://localhost:11434/v1` with `OLLAMA_MODEL`

It is created lazily on first use, omits `tools` when none are passed (used for the final forced reply), and logs prompt and completion tokens on every call for budget monitoring.
