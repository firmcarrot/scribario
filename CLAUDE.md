# Scribario — Project Rules

## What This Is
AI-powered social media content creation + auto-posting via Telegram bot.
Business owners text → AI generates image/video + copy → preview → approve → auto-post.

## Stack
- **Bot:** Python 3.11+, aiogram 3.x, aiogram_dialog
- **FSM Storage:** Redis 7 (`redis://localhost:6379/0`) — required for caption edit state to survive restarts
- **Pipeline/Worker:** Python, httpx, anthropic SDK
- **Database:** Supabase Postgres + pgmq + pg_cron
- **Posting:** Postiz (self-hosted Docker)
- **Image Gen:** Kie.ai (Nano Banana 2), Gemini fallback
- **Video Gen:** Veo 3.1 Fast via Kie.ai (inline in generate_content job)
- **LLM:** Claude API (captions, brand voice, video prompts)

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
  learning/             # Invisible AI learning engine
    structural_diff.py  # Caption feature extraction + pairwise diff
    preference_engine.py # Preference signal accumulation
    edit_analyzer.py    # Haiku edit triple analysis
    formula_tracker.py  # Formula performance stats
    engagement_scorer.py # Engagement score computation
worker/               # Background job worker
  jobs/               # Job handlers (generate, post, etc.)
scripts/              # Server scripts
  connect_server.py   # ASGI webhooks server (Stripe, Meta)
  meta_data_deletion.py # Meta signed_request parsing
supabase/             # Supabase config + migrations
tests/                # Pytest test suite
web/                  # Next.js marketing website (scribario.com)
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
- **Inline video gen:** When generate_video=True, video is generated INSIDE generate_content job (not a separate job). Falls back to image-only on Veo failure.
- **Invisible learning:** All learning is fire-and-forget -- never blocks user flow. Edit signals high-confidence (2x = hard rule), approval signals low-confidence (8x = soft nudge). Wildcard rule: always 1 of 3 options breaks from patterns.
- **Layer 11:** Learned preferences injected into system prompt. Hard rules from edits, soft nudges from approvals, formula performance stats.
- **Long video deprecated:** `/longvideo` router and `generate_long_video` handler disconnected. Files still exist but are not wired.

## Video Pipeline (March 2026)
- Video requests detected by keywords: "video", "reel", "clip", "animate", "motion"
- Vertical (9:16) for: "reel", "story", "tiktok", "shorts"
- `content_requests` stores `generate_video` + `video_aspect_ratio`
- Preview shows: video + 3 caption options with `approve_video:{draft_id}:{option}` buttons
- "Make Video" button on image previews still works via separate `generate_video` job
- Regenerate preserves video flag from original request

## Stripe Billing (March 2026)
- 3 tiers: Starter $29/mo, Growth $59/mo, Pro $99/mo + annual 20% off
- Webhooks on connect_server.py: checkout, invoice, subscription lifecycle
- Bot commands: /subscribe, /billing, /usage, /topoff, /upgrade
- Per-tenant billing cycles, bonus credits persist until used
- Test mode active — live swap pending

## Feedback System (March 2026)
- `/feedback` → [Bug | Idea] → describe → ticket created → admin notified
- `/ticket SC-00001` → check status, or `/ticket` for recent list
- `support_tickets` table with auto-generated ticket numbers (SC-00001+)
- Admin alert sent to Ron's chat (plain text, no buttons)

## Connect Server (March 2026)
- ASGI app at `scripts/connect_server.py`, port 8100
- Hosted on VPS behind nginx at `connect.scribario.com`
- Routes: Stripe webhooks, Meta data deletion callback (`POST /meta/data-deletion`)
- Meta callback: HMAC-SHA256 signed_request verification, logs to `data_deletion_requests` table

## Legal Entity
- **Company:** DarkArc Technologies LLC (Wyoming, EIN 41-5082561)
- **Domain:** darkarctech.com
- Scribario is a product/brand of DarkArc Technologies LLC
- Public site references "DarkArc Technologies LLC" in legal pages + footer only
- **DO NOT expose tech stack on public-facing pages** — use generic descriptions (AI text engine, AI image engine, etc.)

## Deployment
- **Website:** Vercel (auto-deploys from `main`)
- **Bot + Worker:** VPS at 31.97.13.213 (Hostinger), systemd services
- **Connect server:** Same VPS, `scribario-connect.service`
- **No git on VPS** — deploy via `scp` + `systemctl restart`
- **Postiz:** Docker on VPS at `postiz.scribario.com`

## Git
- Branch: `main`
- No pushing without Ron's explicit "push" or "create PR"
- Commit messages: feat/fix/chore prefix
