# Scribario — Project Rules

## What This Is
AI-powered social media content creation + auto-posting via Telegram bot.
Business owners text → AI generates image + copy → preview → approve → auto-post.

## Stack
- **Bot:** Python 3.11+, aiogram 3.x, aiogram_dialog
- **FSM Storage:** Redis 7 (`redis://localhost:6379/0`) — required for caption edit state to survive restarts
- **Pipeline/Worker:** Python, httpx, anthropic SDK
- **Edge Functions:** Deno/TypeScript (Supabase)
- **Database:** Supabase Postgres + pgmq + pg_cron
- **Posting:** Postiz (self-hosted Docker)
- **Image Gen:** Kie.ai (Nano Banana 2), Gemini fallback
- **LLM:** Claude API (captions, brand voice)

## Directory Structure
```
bot/                  # Telegram bot (aiogram)
  handlers/           # Message + callback handlers
  dialogs/            # aiogram_dialog state machines
  services/           # Telegram message builders
pipeline/             # Content generation pipeline
  orchestrator.py     # Request → generate → preview → post
  image_gen.py        # Provider-abstracted image generation
  caption_gen.py      # Claude API caption generation
  posting.py          # Postiz posting wrapper
  brand_voice.py      # Brand profile + few-shot loader
worker/               # Background job worker
  jobs/               # Job handlers (generate, post, etc.)
supabase/             # Supabase config + migrations
tests/                # Pytest test suite
```

## Coding Standards (Python)
- **Linting:** ruff (select: E, F, I, N, W, UP, B, SIM, RUF)
- **Testing:** pytest + pytest-asyncio (asyncio_mode = "auto")
- **Type checking:** mypy --strict
- **Line length:** 100 chars
- **Imports:** isort via ruff, absolute imports preferred
- **Logging:** structlog (JSON structured logs)
- **Config:** pydantic-settings for env var loading
- **Async:** Use async/await everywhere (aiogram is async-first)

## TDD (THE IRON LAW)
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.
1. Write test FIRST → 2. Watch fail → 3. Minimal code → 4. Watch pass → 5. Refactor

## NO PATCHWORK. NO WORKAROUNDS. NO FRANKENSTEIN CODE. (NON-NEGOTIABLE)
- If the right fix requires installing a dependency → install it.
- If the right fix requires a DB migration → write it.
- If the right fix requires refactoring existing code → refactor it.
- NEVER encode state in message text, hidden fields, or other hacks to avoid proper storage.
- NEVER use MemoryStorage in production — it loses all state on restart. Use Redis.
- When a known issue exists (DA finding, TODO, etc.) → fix it properly or flag it clearly. Never paper over it.
- "Quick workaround" is not a valid option. If you can't do it right, stop and say so.

## Supabase
- **Project:** Scribario (ID: `iptivnzimbpoepwdlwri`)
- **URL:** https://iptivnzimbpoepwdlwri.supabase.co
- **Org:** Speed2Leads (`pyywqixyadkuylrnexmq`)
- **Region:** us-east-1
- **Extensions:** pgmq, pg_cron, pg_net
- **Migrations:** `supabase/migrations/` — timestamp from MCP, never invented
- **Edge Functions:** Deno, <400s, 256MB. Heavy work → enqueue to pgmq → worker handles it
- **RLS:** tenant_id on every table, RLS policies enforced
- **Vault:** OAuth tokens stored encrypted, never in plain columns

## Seed Data
- **Mondo Shrimp tenant:** `52590da5-bc80-4161-ac13-62e9bcd75424`
- Brand profile seeded with tone, audience, do/dont lists, product catalog
- 5 few-shot examples seeded (4 Instagram, 1 Facebook)

## Security Rules
- tenant_id on EVERY row + RLS policies
- OAuth tokens in Supabase Vault only
- Workers use service role key with explicit tenant_id filtering
- No BYOK — we manage all API keys, baked into subscription pricing

## Key Patterns
- **State machine in DB:** All state transitions are database writes. Bot is just UI.
- **Idempotency:** Every job has idempotency_key = hash(request_id + job_type)
- **Provider abstraction:** Thin wrappers around all external APIs (swap without pipeline changes)
- **Fail loud:** Never return fake data or silently succeed on failure

## Git
- Branch: `main`
- No pushing without Ron's explicit "push" or "create PR"
- Commit messages: feat/fix/chore prefix
