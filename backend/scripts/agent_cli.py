"""
Agent CLI — simulates the WhatsApp webhook flow exactly.

Usage:
    cd backend
    .venv/bin/python scripts/agent_cli.py

Flow (matches whatsapp.py webhook exactly):
    1. Select/create lead (get_or_create_by_phone)
    2. Store user message (add_message)
    3. Call process_message (orchestrator)
    4. Store assistant reply (add_message)
    5. Show updated lead state
"""

import asyncio

from app.agent.orchestrator import process_message
from app.core.database import close_db, get_session, init_db
from app.core.logging import setup_logging
from app.repositories.conversation_repo import ConversationRepository
from app.services.lead_service import LeadService


def _fmt(val):
    if val is None:
        return "—"
    return str(val)


def _show_lead(lead):
    print(f"  Name:        {_fmt(lead.name)}")
    print(f"  Phone:       {lead.whatsapp_phone}")
    print(f"  Status:      {lead.status}")
    print(f"  Stage:       {lead.conversation_stage}")
    print(f"  Company:     {_fmt(lead.company)}")
    print(f"  Team size:   {_fmt(lead.team_size)}")
    print(f"  Interest:    {_fmt(lead.product_interest)}")
    print(f"  Budget:      {_fmt(f'{lead.budget_min:,.0f}') if lead.budget_min else '—'} – {_fmt(f'{lead.budget_max:,.0f}') if lead.budget_max else '—'}")
    print(f"  Email:       {_fmt(lead.email)}")
    print(f"  Notes:       {_fmt(lead.notes)}")


async def _amain():
    setup_logging()  # honour LOG_LEVEL like the API does
    await init_db()

    current_lead = None

    print()
    print("=" * 56)
    print("  Sales Agent CLI — WhatsApp Simulator")
    print("=" * 56)
    print("  Type 'help' for commands.")
    print()

    async with get_session() as session:
        lead_service = LeadService(session)

        while True:
            try:
                raw = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not raw:
                continue

            parts = raw.split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            # ── help ──────────────────────────────────────────
            if cmd == "help":
                print("  list                          — show all leads")
                print("  select <phone>                — select a lead by phone")
                print("  new <phone> [name]            — create a new lead")
                print("  say <message>                 — send message to agent (matches WhatsApp flow)")
                print("  history                       — show conversation for current lead")
                print("  state                         — show current lead data")
                print("  help                          — this message")
                print("  quit                          — exit")

            # ── list ──────────────────────────────────────────
            elif cmd == "list":
                data, total = await lead_service.list_leads(1, 50)
                if not data:
                    print("  No leads found.")
                else:
                    for idx, lead_row in enumerate(data, 1):
                        marker = " ◀" if current_lead and lead_row.id == current_lead.id else ""
                        print(f"  [{idx}] {lead_row.name or 'Unnamed'} | {lead_row.whatsapp_phone} | {lead_row.status} | stage: {lead_row.conversation_stage}{marker}")
                print(f"  Total: {total}")

            # ── select <phone> ────────────────────────────────
            elif cmd == "select":
                if not args:
                    print("  Usage: select <phone>")
                    continue
                phone = args.split()[0]
                lead = await lead_service.get_or_create_by_phone(phone)
                current_lead = lead
                print(f"  Selected: {lead.name or 'Unnamed'} ({lead.whatsapp_phone})")
                _show_lead(lead)

            # ── new <phone> [name] ────────────────────────────
            elif cmd == "new":
                parts_new = args.split(maxsplit=1)
                phone = parts_new[0]
                name = parts_new[1] if len(parts_new) > 1 else None
                lead = await lead_service.create_lead(phone=phone, name=name, source="manual")
                current_lead = lead
                print(f"  Created: {lead.name or 'Unnamed'} ({lead.whatsapp_phone})")

            # ── state ─────────────────────────────────────────
            elif cmd == "state":
                if not current_lead:
                    print("  No lead selected. Use 'new' or 'select' first.")
                    continue
                lead = await lead_service.get_lead(current_lead.id)
                if not lead:
                    print("  Lead not found.")
                    current_lead = None
                    continue
                current_lead = lead
                print(f"  Lead: {lead.id}")
                _show_lead(lead)

            # ── say <message> ─────────────────────────────────
            elif cmd == "say":
                if not current_lead:
                    print("  No lead selected. Use 'new' or 'select' first.")
                    continue
                if not args:
                    print("  Usage: say <message>")
                    continue

                message = args

                # Refresh lead
                lead = await lead_service.get_lead(current_lead.id)
                if not lead:
                    print("  Lead not found.")
                    current_lead = None
                    continue
                current_lead = lead

                print(f"  You ({lead.whatsapp_phone}): {message}")
                print()

                # ── Matches whatsapp.py webhook flow ───────────
                repo = ConversationRepository(session)

                # Step 1: Store user message (whatsapp.py:83-89)
                await repo.add_message({
                    "lead_id": lead.id,
                    "role": "user",
                    "content": message,
                    "message_type": "text",
                })

                # Step 2: Process via AI agent (whatsapp.py:93-98)
                try:
                    reply = await process_message(
                        lead_id=str(lead.id),
                        message_text=message,
                        lead=lead,
                        session=session,
                    )
                except Exception:
                    reply = (
                        "Thank you for your message! One of our team members "
                        "will get back to you shortly."
                    )

                # Step 3: Store assistant reply (whatsapp.py:113-118)
                await repo.add_message({
                    "lead_id": lead.id,
                    "role": "assistant",
                    "content": reply,
                    "message_type": "text",
                })
                # ── End of webhook flow ─────────────────────────

                print(f"  Agent: {reply}")
                print()

                # Show updated lead state
                lead = await lead_service.get_lead(lead.id)
                if lead:
                    current_lead = lead
                    print(f"  ├─ stage: {lead.conversation_stage}")
                    print(f"  ├─ status: {lead.status}")
                    if lead.company or lead.team_size:
                        print(f"  ├─ {_fmt(lead.company)} | {_fmt(lead.team_size)} seats | {_fmt(lead.product_interest)}")
                    if lead.budget_min or lead.budget_max:
                        print(f"  └─ budget: {_fmt(f'{lead.budget_min:,.0f}') if lead.budget_min else '?'} – {_fmt(f'{lead.budget_max:,.0f}') if lead.budget_max else '?'}")
                    print()

            # ── history ────────────────────────────────────────
            elif cmd == "history":
                if not current_lead:
                    print("  No lead selected.")
                    continue
                repo = ConversationRepository(session)
                msgs = await repo.get_history(current_lead.id, 50)
                if not msgs:
                    print("  No messages yet.")
                else:
                    for m in msgs:
                        role = "You" if m.role == "user" else "Agent"
                        c = m.content or ""
                        print(f"  [{role}] {c[:150]}")
                print(f"  Total: {len(msgs)} messages")

            elif cmd in ("quit", "exit", "q"):
                break

            else:
                print(f"  Unknown command: {cmd}. Type 'help'.")

    await close_db()


def main():
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
