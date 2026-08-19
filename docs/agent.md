# AI Agent — Sarah

The AI agent is the core of the WhatsApp lead generation pipeline. It handles inbound messages, extracts lead information, searches properties, schedules meetings, and sends emails through natural conversation. Built on Groq function calling (llama-3.3-70b-versatile), it follows a multi-stage sales process with tool execution.

Powered by raw Groq function calling — no LangChain, no LangGraph. The orchestrator is ~200 lines and gives full control over every aspect of the conversation loop.

## Persona

| Attribute | Detail |
|-----------|--------|
| Name | Sarah |
| Role | Real estate consultant at LeadGen Realty (Dubai) |
| Tone | Warm, professional, friendly |
| Languages | English (primary), understands Hindi/Hinglish naturally |
| Target Audience | Indian buyers and NRIs investing in Dubai real estate |
| Emoji Style | Used sparingly |
| Response Length | 2-5 sentences per message (WhatsApp-appropriate) |

### Knowledge Base

- Dubai real estate expert: neighborhoods, price ranges, investment dynamics
- Indian investor context: tax-free rental income, Golden Visa (AED 2M+ property), capital appreciation, NRI loan options, repatriation of funds
- Currency conversion: 1 AED approx 24 INR, 1 lakh INR approx 440 AED, 1 crore INR approx 44,000 AED
- Popular areas for Indians: Dubai Marina, Downtown, Palm Jumeirah, JVC, Business Bay, Dubai Hills, Arabian Ranches
- Cost awareness: 4% DLD fee + registration fees on top of purchase price
- Rental yields: typically 5-8% depending on area and property type

### Communication Style Rules

- Warm and friendly, never a corporate bot
- 2-5 sentences max per message for WhatsApp
- Uses emojis sparingly
- Mirrors lead energy — excited? match it. Cautious? be reassuring
- Understands Hindi phrases, responds in English but may use Hinglish expressions
- Shows prices in BOTH AED and INR using Indian notation (lakh/crore)

## Conversation Stages

Stage is stored as `conversation_stage` on the Lead record and influences behavior via stage-specific instructions injected into the system prompt.

| Stage | When | Agent's Goal |
|-------|------|-------------|
| `greeting` | New lead | Welcome to LeadGen Realty. Introduce Sarah. Ask what kind of property and preferred area. Keep it casual and inviting. |
| `information_gathering` | After greeting | Collect budget, location, property type, bedrooms one question at a time. Save each with `update_lead_info`. Move to search when budget OR location is known. |
| `property_search` | Requirements collected | Call `search_properties` with criteria. Present 2-3 options with name, location, price (AED + INR), bedrooms. Ask which interests them. |
| `property_presentation` | Lead interested in specific property | Use `get_property_details`. Highlight what makes it special. Answer questions. Suggest a site visit. |
| `scheduling` | Lead wants to visit | Ask for preferred date/time. Call `schedule_meeting`. Confirm details. Mention visit is free and no-obligation. |
| `follow_up` | Returning lead | Be warm. Reference previous preferences. Ask if they've had time to think. Don't restart from scratch. |
| `closed` | Conversation done | Be gracious. Thank them. Let them know they can reach out anytime. |

## Tools (8)

All tool calls in one Groq response are executed in parallel. The orchestrator appends ONE assistant message with all tool_calls, then individual tool role messages for each result.

### 1. `search_properties`

Search available Dubai properties matching lead criteria.

**Parameters (all optional):**
- `property_type`: apartment, villa, townhouse, penthouse, studio
- `location`: Dubai area/community name
- `min_price`: Minimum budget in AED
- `max_price`: Maximum budget in AED
- `bedrooms`: Minimum bedrooms

**Handler logic:**
1. Instantiate PropertyService(session) with fresh session
2. Call service.search_properties with limit=5
3. Format each result as: {title} | {beds}BR | AED {price} ({INR}) | {location}
4. Uses `_format_price_inr()` to convert AED to INR with lakh/crore notation

**Returns:** Formatted string of matching properties, or "No properties found matching those criteria."

### 2. `list_all_properties`

List all available properties with no filters. Used when lead asks to see everything.

**Parameters:** None

**Handler logic:**
1. Call PropertyService.list_properties(page=1, page_size=20, status=available)
2. Format results with AED + INR pricing

**Returns:** "Here are all our available properties ({total} total):" + formatted list

### 3. `get_property_details`

Get full details of a specific property by ID.

**Parameters (required):**
- `property_id`: UUID of the property

**Returns:** Multi-line string with title, location, price (AED + INR), bedrooms/bathrooms, area, featured status, description

### 4. `update_lead_info`

Save or update lead information as learned during conversation. All fields are optional. Pass null to clear/remove that constraint.

**Parameters (all optional):**
- `name`: Lead's full name
- `email`: Lead's email
- `budget_min`: Minimum budget in AED (pass null to clear)
- `budget_max`: Maximum budget in AED (pass null to clear)
- `property_type`: Preferred property type
- `bedrooms_min`: Minimum bedrooms (pass null to clear)
- `location`: Preferred area (pass null to clear)
- `notes`: Additional notes

**Handler logic:**
1. Convert to LeadUpdate Pydantic model
2. Call LeadService.update_lead(lead_id, update) with exclude_unset=True so null values actually clear DB columns
3. Log which fields were updated vs cleared

**Returns:** "Updated: budget_max, location | Cleared: property_type"

### 5. `update_lead_stage`

Advance the conversation stage as the lead progresses through the sales pipeline.

**Parameters (required):**
- `stage`: One of: greeting, information_gathering, property_search, property_presentation, scheduling, follow_up, closed

**Handler logic:**
1. Create LeadUpdate with conversation_stage set
2. Call LeadService.update_lead

**Returns:** "Stage updated to: property_presentation"

### 6. `schedule_meeting`

Schedule a property site visit or meeting for an interested lead.

**Parameters:**
- `scheduled_at` (required): ISO 8601 datetime string
- `duration_minutes` (optional, default 30)
- `notes` (optional): Meeting purpose or property to visit

**Handler logic:**
1. Instantiate MeetingService(session)
2. Call service.schedule_meeting(lead_id, scheduled_at, duration, notes)
3. Service parses ISO 8601 string to datetime internally
4. Returns meeting object with scheduled_at, duration, status

**Returns:** "Meeting scheduled! Date: {scheduled_at}, Duration: {duration} min, Status: {status}"

### 7. `send_email`

Send property information or brochure via email to the lead.

**Parameters (all required):**
- `to`: Lead's email address
- `subject`: Email subject line
- `body`: Email body text (text, not HTML currently)

**Handler logic:**
1. Call EmailClient.send_email(to, subject, html_body=body)
2. In dev mode (SMTP not configured), email is logged to console
3. EmailClient.send_email() wraps the synchronous SMTP call in `asyncio.to_thread()` to avoid blocking the event loop

**Returns:** "Email sent to {email} with subject: {subject}"

**Note:** This is a direct email send, not a template. The agent generates the body content dynamically based on the conversation context.

### 8. `transfer_to_human`

Escalate conversation to a human team member. Used when lead asks for complex negotiations, legal questions, or explicitly requests a person.

**Parameters (required):**
- `reason`: Reason for escalation

**Returns:** "{reason}. A member of our team will follow up with you shortly. Thank you for your interest in LeadGen Realty!"

## Tool Execution Architecture

```
execute_tool(name, args, lead_id, session)
  │
  ├─ match name:
  │
  ├─ "search_properties"     → _search_properties(args, session)
  │   └─ PropertyService(session).search_properties(...)
  │
  ├─ "list_all_properties"   → _list_all_properties(session)
  │   └─ PropertyService(session).list_properties(...)
  │
  ├─ "get_property_details"  → _get_property_details(args, session)
  │   └─ PropertyService(session).get_property(args["property_id"])
  │
  ├─ "update_lead_info"      → _update_lead_info(args, lead_id, session)
  │   └─ LeadService(session).update_lead(lead_id, LeadUpdate(**args))
  │
  ├─ "update_lead_stage"     → _update_lead_stage(args, lead_id, session)
  │   └─ LeadService(session).update_lead(lead_id, LeadUpdate(conversation_stage=...))
  │
  ├─ "schedule_meeting"      → _schedule_meeting(args, lead_id, session)
  │   └─ MeetingService(session).schedule_meeting(lead_id, scheduled_at, duration, notes)
  │
  ├─ "send_email"            → _send_email(args)
  │   └─ EmailClient().send_email(to, subject, html_body)
  │
  ├─ "transfer_to_human"     → _transfer_to_human(args)
  │   └─ Returns formatted escalation message
  │
  └─ unknown                 → Returns "Unknown tool: {name}"
```

Each handler:
1. Instantiates the appropriate service class with the DB session
2. Calls the service method with parsed arguments
3. Returns a human-readable result string
4. Logs execution with structlog (tool name, lead_id, args)
5. Exceptions are caught in the orchestrator and returned as error messages

## Orchestrator Flow (Detailed)

```
process_message(lead_id, message_text, lead, session) -> str

# Phase 1: Load context
history = ConversationRepository.get_history(lead_id, limit=MAX_HISTORY_MESSAGES)

# Phase 2: Build messages array
lead_context = _build_context(lead)
# Returns structured bullet points:
#   - Name: Rahul
#   - Phone: +971...
#   - Email: Not collected yet
#   - Budget: AED 1,500,000 - AED 2,500,000
#   - Property type: apartment
#   - Location: Dubai Marina
#   - Bedrooms: 2
#   - Status: new
#   - Stage: information_gathering

stage_instruction = STAGE_INSTRUCTIONS.get(current_stage, "")

system_prompt = f"{SYSTEM_PROMPT}\n\n## Lead Profile\n{lead_context}\n\n## Current Stage: {stage}\n{stage_instruction}\n\n{GUARDRAILS}"

messages = [
    {"role": "system", "content": system_prompt},
    *history (user + assistant messages, oldest first),
    {"role": "user", "content": message_text},
]

# Phase 3: Main agent loop
for round_num in range(MAX_TOOL_ROUNDS):
    try:
        response = llm_client.chat_completion(
            messages=messages,
            tools=TOOL_DEFINITIONS,    # 8 tool schemas
            temperature=0.6,
            max_tokens=1024,
        )
    except Exception:
        log error
        return fallback message

    content = response.get("content")
    tool_calls = response.get("tool_calls", [])

    if not tool_calls:
        if content and content.strip():
            return content    # FINAL RESPONSE
        # Empty content - nudge
        messages.append({"role": "user", "content": "(Please respond to the lead's message.)"})
        continue

    # Handle tool calls
    # IMPORTANT: Append ONE assistant message with ALL tool_calls
    # This is the correct OpenAI/Groq format for parallel execution
    assistant_msg = {
        "role": "assistant",
        "content": content,
        "tool_calls": [
            {
                "id": tc["id"],
                "type": "function",
                "function": {"name": tc["function"], "arguments": tc["arguments"]},
            }
            for tc in tool_calls
        ],
    }
    messages.append(assistant_msg)

    # Execute each tool and append result
    for tc in tool_calls:
        try:
            args = json.loads(tc["arguments"])
            result = await execute_tool(tc["function"], args, lead_id, session)
        except Exception:
            log error
            result = f"Error executing {tc['function']}. Please try again."

        messages.append({
            "role": "tool",
            "tool_call_id": tc["id"],
            "content": result,
        })

# Phase 4: Exhausted tool rounds - force final response
try:
    response = llm_client.chat_completion(
        messages=messages,
        tools=None,              # No more tools available
        tool_choice="none",
        temperature=0.7,
        max_tokens=1024,
    )
    if response.get("content", "").strip():
        return response["content"]
except Exception:
    log error

# Phase 5: Last resort fallback
lead_name = lead.name or "there"
return f"Thanks for your patience{', ' + lead_name if lead_name else ''}! I've noted everything..."
```

## System Prompt Architecture

The full system prompt sent to Groq each round is assembled from 4 parts:

### Part 1: System Prompt (core identity)

Contains Sarah's core identity, communication rules, knowledge base, and workflow instructions. Key sections:

- **Who you are**: Sarah, real estate consultant at LeadGen Realty
- **How you communicate**: Warm, 2-5 sentences, emojis sparingly, Hinglish understanding
- **Your knowledge**: Dubai market, Indian investor context, currency conversion, popular areas, costs
- **Your workflow**: 6-step process from greet to close
- **Tool usage rules**: Always use tools, never invent data, convert INR to AED, batch updates

### Part 2: Lead Profile (dynamic context)

Built fresh from the database each call via `_build_context()`. Shows the model what it knows and what's missing:

```
Lead Profile
- Name: Rahul Sharma
- Phone: +971501234567
- Email: Not collected yet
- Budget: AED 1,500,000 - AED 2,500,000
- Property type: apartment
- Location: Dubai Marina
- Bedrooms: 2
- Lead status: new
- Conversation stage: information_gathering
```

### Part 3: Stage Instruction (behavior guidance)

Injected based on the current `conversation_stage`. Example for follow_up:

```
This is a returning lead. Be warm and natural. Check if they've had time to think,
if they have questions, or want to see new options. Don't restart from scratch --
reference their previous preferences from the Lead Profile above.
```

### Part 4: Guardrails (safety rules)

Always appended after the stage instruction. Key rules:

- No hallucinated pricing or property data
- No personal contact information sharing
- No promises of specific investment returns
- Indian numbering: 1 lakh = 1,00,000, 1 crore = 1,00,00,000
- If client mentions lakh/crore without currency, assume INR
- Always show prices in BOTH AED and INR
- If "no budget" / "budget is not an issue": clear budget with null values
- If preferences change: update via update_lead_info FIRST, then re-search
- Correct obvious typos: dubar -> Dubai, marinna -> Marina, palm -> Palm Jumeirah
- If no search results: acknowledge, suggest alternatives, don't repeat same search
- If illegal/inappropriate content: politely end the conversation
- If asked for legal advice: recommend a lawyer but share general knowledge

## Token Budget

| Component | Tokens | Notes |
|-----------|--------|-------|
| System prompt | ~800 | Condensed version of Sarah persona + rules |
| Lead profile | ~100 | Dynamic context from DB |
| Stage instruction | ~50 | Stage-specific behavior guidance |
| Guardrails | ~100 | Safety rules |
| Tool definitions (8 x ~50) | ~400 | JSON schemas for function calling |
| Conversation history (10 x ~40) | ~400 | Average message length 40 tokens |
| User message | ~50 | Current incoming message |
| **Total prompt per call** | **~1900** | |
| Model response | ~200 | Average response (max 1024) |
| **Total per call** | **~2100** | |

### Daily Budget

Groq free tier: 100,000 tokens per day for llama-3.3-70b-versatile.

A typical 2-call exchange (call + tool round + final): ~4,200 tokens
A worst-case 10-round exchange: ~23,100 tokens

This means ~24 normal exchanges or ~4 long ones before hitting the daily limit.

Token usage is logged per call:
```
llm_completion provider=groq model=llama-3.3-70b-versatile prompt_tokens=1900
  completion_tokens=200 tool_calls=2 has_content=true finish_reason=tool_calls
```

## Session Staleness (Fixed)

After each tool round that modifies the lead (via `update_lead_info`, `update_lead_stage`, or `schedule_meeting`), the orchestrator:
1. Reloads the lead from the database with fresh data
2. Rebuilds `messages[0]["content"]` with updated Lead Profile and Current Stage

This ensures the model always sees current lead data in every round, even within a multi-tool exchange. The fix is in [`orchestrator.py`](../backend/app/agent/orchestrator.py) at the end of the tool execution loop.

## Agent CLI

The `scripts/agent_cli.py` script simulates the WhatsApp webhook flow exactly — same code path, same database operations.

### Running

```
cd backend
PYTHONPATH=. .venv/bin/python scripts/agent_cli.py
```

### Commands

| Command | Example | Description |
|---------|---------|-------------|
| `list` | `list` | Show all leads with ID, phone, name, status |
| `select <n>` | `select 1` | Select lead by list number |
| `new <phone>` | `new +971501234567` | Create new lead with phone number |
| `say <msg>` | `say Hi, looking for 2BR in Marina` | Send message as selected lead |
| `history` | `history` | Show conversation history |
| `state` | `state` | Show full lead state (all DB fields) |
| `help` | `help` | Show all commands |
| `quit` | `quit` | Exit CLI |

### Example Session

```
> new +971551234567
Created lead: +971551234567 (ID: abc-123)

> say hi
You: hi
Bot: Hello! Welcome to LeadGen Realty! I'm Sarah, and I'd be happy
     to help you find your ideal property in Dubai. Are you looking to
     buy, invest, or rent? Any particular area in mind? 🏠

Lead State:
- Name: Not provided yet
- Status: new
- Stage: greeting
- Budget: Not specified yet

> say looking for 2BR apartment in Marina under 3M AED
You: looking for 2BR apartment in Marina under 3M AED
Bot: Great choices! Let me search for available 2BR apartments in Dubai
     Marina within your budget.

[search_properties called with: location=Dubai Marina, max_price=3000000,
 property_type=apartment, bedrooms=2]

Bot: Here are some options:
     - 2BR Luxury Apartment in Dubai Marina | 2BR | AED 2,500,000
       (approx 6 crore INR) | Dubai Marina
     - Modern 2BR with Panoramic Marina View | 2BR | AED 2,800,000
       (approx 6.7 crore INR) | Dubai Marina
     Would you like more details on any of these?

Lead State:
- Name: Not provided yet
- Status: new
- Stage: property_search
- Budget: Up to AED 3,000,000
- Property type: apartment
- Location: Dubai Marina
- Bedrooms: 2

> state
Lead: +971551234567
Name: Not provided yet
Email: Not collected yet
Budget: Up to AED 3,000,000
Property type: apartment
Location: Dubai Marina
Bedrooms: 2
Status: new
Stage: property_search
```

## LLM Client Details

Uses the OpenAI SDK (`openai.AsyncOpenAI`) for both Groq (hosted) and Ollama (local) via the same OpenAI-compatible API.

### Implementation

```python
class LLMClient:
    def __init__(self):
        settings = get_settings()
        if settings.LLM_PROVIDER == "ollama":
            self.client = AsyncOpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
            )
            self.model = settings.OLLAMA_MODEL  # qwen3:8b
        else:
            self.client = AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY,
            )
            self.model = settings.GROQ_MODEL  # llama-3.3-70b-versatile

    async def chat_completion(self, messages, tools=None, tool_choice=None,
                              temperature=0.7, max_tokens=1024):
        # Build request with conditional tools
        # Call OpenAI SDK
        # Parse response into {content, tool_calls, role, finish_reason}
        # Log: model, prompt_tokens, completion_tokens, tool_calls count, finish_reason
        # Return parsed dict
```

### Key Behaviors

- **Lazy init**: Client is created on first use, not at module import. Avoids calling get_settings() during import time.
- **Conditional tools**: If tools is None, they're omitted from the request. Used for the final fallback call after exhausting tool rounds.
- **Token logging**: Every call logs prompt_tokens and completion_tokens separately for budget monitoring.
- **Auto tool_choice**: Default is "auto". Supports "none" for the final no-tools round.
- **Error handling**: RateLimitError triggers 3 retries with exponential backoff (1s, 3s) in the orchestrator before falling through to fallback.
