# Scribario — Architecture

## System Overview

Scribario is built around a simple invariant: **all business logic lives in the pipeline and worker, never in the bot.** The Telegram bot is a thin UI layer. State transitions are database writes. The worker is a dumb job processor.

**Architecture Diagram:** See [`scribario-architecture.excalidraw`](./scribario-architecture.excalidraw) for the full visual. [Open in Excalidraw](https://excalidraw.com) and import the file, or view the rendered PNG at [`scribario-architecture.png`](./scribario-architecture.png).

### Two-Layer Intelligence

The core differentiator is the AI Intelligence Layer:

1. **Intake Agent** (Claude Haiku, ~$0.001/call) — Classifies whether we have enough to proceed or need to ask the user for photos/clarity. Philosophy: ask as few questions as possible, but as many as necessary for quality output.

2. **Prompt Engine** (Claude Sonnet, ~$0.04/call) — Takes user intent + brand profile + reference photos and outputs a complete `GenerationPlan`: content format, scene-by-scene prompts, reference image assignments, 3 caption options with unique copywriting formulas, voice style, and compositing instructions.

### Two Content Pipelines

The engine routes to one of two pipelines based on intent:

| Pipeline | Output | Cost |
|----------|--------|------|
| **IMAGE POST** | 1-3 static images via Nano Banana 2 | ~$0.16 |
| **SHORT VIDEO** | Single 8s clip (frame + Veo Fast), generated inline with captions | ~$0.50 |

When `generate_video=True`, video generation runs **inline** inside the same `generate_content` job — the user sees ONE unified preview with the video plus 3 caption options. No separate video job is enqueued.

All pipelines converge on: Preview in Telegram → Approve → Auto-Post via Postiz.

> **Long Video (DEPRECATED):** The multi-scene long video pipeline (`pipeline/long_video/`) still exists in the codebase but is disconnected — the `/longvideo` command router has been removed from `bot/main.py` and the `generate_long_video` worker handler has been removed from `worker/main.py`.

---

## Components

### Bot (`bot/`)

The Telegram interface built with aiogram 3.x and aiogram-dialog.

| File | Responsibility |
|---|---|
| `main.py` | Bot entrypoint, dispatcher setup, router registration |
| `config.py` | pydantic-settings — all config from environment variables |
| `db.py` | Supabase client + database helper functions |
| `handlers/intake.py` | Free-text message handler — parses user intent, enqueues job |
| `handlers/approval.py` | Callback query handler — processes Approve / Reject / Regenerate. Exposes `approve_draft()` and `approve_video_draft()` shared functions used by both manual and autopilot flows. |
| `handlers/autopilot.py` | /autopilot, /pause, /resume commands + FSM setup flow (mode → schedule → platforms) |
| `handlers/onboarding.py` | /start and brand setup flow |
| `handlers/photos.py` | Reference photo upload handler |
| `dialogs/onboarding.py` | aiogram-dialog state machine for brand profile setup |
| `services/telegram.py` | Outbound message builders (preview cards, status messages, `build_video_preview_keyboard()`) |
| `services/postiz.py` | Postiz API client |
| `services/postiz_oauth.py` | OAuth flow for connecting social accounts |
| `services/storage.py` | Supabase Storage upload helpers |

**Key design decisions:**
- Bot never calls Claude or Kie.ai directly — it only writes to the database and enqueues jobs
- All approval state is in `content_drafts` — the bot is stateless between messages
- aiogram-dialog handles multi-step flows (onboarding) with explicit state machines

### Prompt Engine (`pipeline/prompt_engine/`)

The AI brain. Turns any user request into a structured `GenerationPlan`.

| File | Responsibility |
|---|---|
| `models.py` | `GenerationPlan`, `ScenePlan`, `FramePrompt`, `AnimationPrompt`, `ContentFormat`, `VeoMode` |
| `engine.py` | `generate_plan()` — single Claude Sonnet call with tool_use structured output |
| `system_prompt.py` | Layered prompt builder: role + format rules + scene rules + ref image strategy + quality rules + brand voice. Includes Layer 11 (learned preferences, edit lessons, formula performance) when data exists |
| `asset_resolver.py` | Load + categorize tenant assets (product photos, people photos, logo) |
| `intake.py` | `check_intake()` — Claude Haiku classifier (proceed / ask_for_asset / ask_for_clarity) |
| `voice_pool.py` | Gender-aware voice selection from tenant's voice pool JSONB |

### Pipeline (`pipeline/`)

The content generation engine. Called by workers, never by the bot directly.

| File | Responsibility |
|---|---|
| `orchestrator.py` | Coordinates the full caption → image → draft flow (image posts) |
| `caption_gen.py` | Claude API client — generates 3 caption + visual prompt options (legacy, still used for `revise_caption()`) |
| `image_gen.py` | Kie.ai Nano Banana 2 client — generates images in parallel |
| `brand_voice.py` | Loads brand profile + few-shot examples (recency-weighted, formula-diverse) + learned preferences + edit lessons from DB |
| `brand_gen.py` | AI-assisted brand profile generation from website scraping |
| `posting.py` | Postiz posting wrapper |
| `topic_engine.py` | Claude Haiku topic generation for autopilot + moderation + keyword dedup |
| `schedule_parser.py` | Natural language schedule → validated cron expression (preset-only, no SQL injection) |

### Learning Engine (`pipeline/learning/`)

The invisible self-improvement system. Extracts learning signals from every user interaction — approvals, edits, and engagement — without any additional user effort. All learning happens backstage.

| File | Responsibility |
|---|---|
| `structural_diff.py` | Pure Python caption feature extraction (word count, emoji, formula, sentence length) + pairwise diff between chosen and rejected options |
| `preference_engine.py` | Accumulates preference signals from approvals and edits. Upserts into `preference_signals` with confidence = occurrences / total_opportunities |
| `edit_analyzer.py` | Fire-and-forget Claude Haiku analysis of edit triples (original → instruction → result). Extracts concrete structural changes (~$0.001/edit) |
| `engagement_scorer.py` | Weighted engagement score: `(likes + comments×3 + shares×5) / views × 1000`, capped at 10.0 |
| `formula_tracker.py` | Aggregates formula performance stats (approval rate, avg engagement, edit rate) from feedback_events + few_shot_examples |

**Key design decisions:**
- Learning is always fire-and-forget — never blocks the user's approval or edit flow
- Edit patterns are high-confidence signals (user actively changed something) — 2 occurrences = hard rule
- Approval patterns are low-confidence (could be coincidence) — 8+ consistent picks = soft nudge
- Engagement data is audience truth — overrides approval patterns
- The Wildcard Rule: always 1 of 3 caption options must break from learned patterns (prevents filter bubble)
- Lessons only, never bad examples — injecting "bad" captions into context primes Claude to mimic them

### Long Video Pipeline (`pipeline/long_video/`) — DEPRECATED

> **Status: DEPRECATED.** The `/longvideo` command and `generate_long_video` worker handler have been removed. These files remain in the codebase but are not reachable from the bot or worker.

Multi-scene video generation. Orchestrates TTS, frame generation, video clip creation, sound effects, and FFmpeg stitching.

| File | Responsibility |
|---|---|
| `orchestrator.py` | `run_pipeline()` — scene-by-scene orchestration with auto-plan generation and legacy fallback |
| `script_gen.py` | Legacy script generation (fallback when Prompt Engine unavailable) |
| `tts.py` | ElevenLabs text-to-speech per scene |
| `frame_gen.py` | Nano Banana 2 start/end frame generation with reference images |
| `clip_gen.py` | Veo 3.1 / Randy GenLens video clip generation |
| `sfx.py` | ElevenLabs sound effect generation |
| `stitcher.py` | FFmpeg compositing — frames + clips + audio + logo overlay |
| `voice_library.py` | ElevenLabs voice management + voice pool integration |

**Generation order:** Captions are generated first because the caption contains the `visual_prompt` that drives the image. For long videos, the Prompt Engine outputs the complete scene plan, then the orchestrator runs TTS → frames → clips → SFX → stitch in sequence.

### Worker (`worker/`)

A long-running async process that polls pgmq queues and dispatches job handlers.

| File | Responsibility |
|---|---|
| `main.py` | Queue poller — polls queues, dispatches handlers, handles errors |
| `jobs/generate_content.py` | Runs the pipeline for a content_request (including inline video when `generate_video=True`), stores draft, sends preview |
| `jobs/generate_caption.py` | Caption-only generation |
| `jobs/generate_image.py` | Image-only generation |
| `jobs/generate_video.py` | Video generation for existing image drafts ("Make Video" button on image previews) |
| `jobs/post_content.py` | Calls Postiz to publish an approved draft |
| `jobs/autopilot_dispatch.py` | Single dispatcher — queries due tenants, fans out per-tenant generation jobs |
| `jobs/autopilot_generate.py` | Per-tenant generation — topic gen, guardrails (daily/weekly/monthly limits), failure tracking |
| `jobs/autopilot_timeout.py` | Smart Queue sweep — auto-approves previews past their timeout deadline |
| `jobs/autopilot_digest.py` | Weekly summary sent to all autopilot-enabled tenants |

Workers run as a systemd service on the VPS. The polling interval and concurrency are configurable via environment variables.

### Supabase (Database + Queues)

Supabase provides Postgres, row-level security, pgmq for queuing, and pg_cron for scheduled jobs.

- **pgmq** handles the job queue with at-least-once delivery and automatic visibility timeouts
- **pg_cron** runs 3 autopilot cron jobs (dispatch every 5min, timeout sweep every 5min, weekly digest Sundays 9am UTC)
- **Supabase Storage** holds generated images
- **Supabase Vault** will hold OAuth tokens (encrypted at rest)

### Postiz

Self-hosted social media publishing engine running in Docker on the VPS. Scribario uses Postiz as a publishing abstraction layer — a single API call to Postiz handles the platform-specific OAuth, rate limiting, and media upload logic for each connected social network.

Postiz is accessed at `https://postiz.scribario.com` (nginx + Let's Encrypt).

---

## Data Flow: Message to Live Post

This is the complete lifecycle of a single user request:

```
1. USER MESSAGE
   User sends: "Post something about our weekend special"
   └─► bot/handlers/intake.py receives the message

2. INTAKE
   ├─► Look up tenant_id from telegram_user_id
   ├─► Insert row into content_requests (status: "pending")
   └─► Enqueue job to pgmq "content_generation" queue

3. WORKER PICKS UP JOB
   worker/main.py polls pgmq (every 5s)
   └─► Dispatches to worker/jobs/generate_content.py

4. PIPELINE RUNS
   pipeline/orchestrator.py:
   ├─► Load brand profile + few-shot examples from DB
   ├─► Call Claude API → generate 3 captions (with visual_prompt per caption)
   ├─► Call Kie.ai in parallel → generate 3 images from visual_prompts
   └─► If generate_video=True:
       ├─► Generate video prompt from scene plan
       ├─► Generate scene image (1 frame via Nano Banana 2)
       └─► Generate 8s video clip via Veo Fast

5. DRAFT STORED
   ├─► Upload images (and video if present) to Supabase Storage
   ├─► Insert into content_drafts (status: "preview_sent")
   └─► Update content_requests (status: "preview_sent")

6. PREVIEW SENT
   worker/jobs/generate_content.py:
   ├─► IMAGE POST: Send 3 inline keyboards
   │   [Approve #1] [Approve #2] [Approve #3] [Reject All] [Regenerate]
   └─► SHORT VIDEO: Send video + 3 caption options via build_video_preview_keyboard()
       [Caption #1] [Caption #2] [Caption #3] [Reject All] [Regenerate]

7. USER APPROVES
   Image post: User taps "Approve #2"
   Video post: User taps caption option → approve_video:{draft_id}:{option_number}
   └─► bot/handlers/approval.py receives callback_query

8. APPROVAL PROCESSED
   ├─► Update content_drafts (status: "approved", approved_option: N)
   └─► Enqueue job to pgmq "posting" queue

9. POSTING JOB RUNS
   worker/jobs/post_content.py:
   ├─► Load approved draft from DB
   ├─► Download image from Supabase Storage
   └─► POST to Postiz API (image + caption + platform targets)

10. POSTIZ PUBLISHES
    Postiz handles platform-specific OAuth, rate limiting, and media upload:
    ├─► Facebook: Graph API post with media
    ├─► Instagram: Graph API media publish
    ├─► LinkedIn: Share API
    ├─► X (Twitter): v2 Tweet API
    ├─► TikTok: Content Posting API
    ├─► YouTube: Data API v3
    ├─► Bluesky: AT Protocol
    ├─► Pinterest: Pins API
    └─► Threads: Threads API

11. CONFIRMATION
    ├─► Update posting_jobs (status: "posted")
    ├─► Update content_drafts (status: "posted")
    └─► Send Telegram confirmation message to user
```

---

## Database Schema

All tables include `tenant_id uuid NOT NULL` with RLS policies enforcing tenant isolation.

### Core Tables

**`tenants`** — One row per business customer
```
id uuid PK
name text
plan text  -- 'free_beta', 'starter', 'growth', 'pro'
created_at timestamptz
```

**`telegram_users`** — Telegram accounts linked to tenants
```
id uuid PK
tenant_id uuid FK
telegram_user_id bigint UNIQUE
username text
linked_at timestamptz
```

**`brand_profiles`** — Brand voice configuration per tenant
```
id uuid PK
tenant_id uuid FK UNIQUE
brand_name text
tone text[]            -- e.g. ['bold', 'witty', 'warm']
target_audience text
dos text[]             -- things to always do
donts text[]           -- things to never do
product_catalog jsonb  -- products/services
signature_phrases text[]
logo_storage_path text -- Supabase Storage path for brand logo
voice_pool jsonb       -- [{voice_id, gender, style_label}] — gender-aware rotation
```

**`few_shot_examples`** — Past posts used for brand voice training
```
id uuid PK
tenant_id uuid FK
platform text
caption text
visual_description text
performance_score float  -- for ranking examples
```

**`content_requests`** — Every post request from a user
```
id uuid PK
tenant_id uuid FK
telegram_user_id bigint
intent text            -- raw user message
platform_targets text[]
status text            -- pending → generating → preview_sent → done
generate_video boolean DEFAULT false  -- when true, video is generated inline with captions
video_aspect_ratio text               -- e.g. '9:16', '16:9', '1:1' (preserved on regenerate)
created_at timestamptz
```

**`content_drafts`** — Generated options for a request
```
id uuid PK
request_id uuid FK
tenant_id uuid FK
options jsonb          -- array of {caption, image_url, visual_prompt}
approved_option int    -- which option the user picked (1-3)
status text            -- preview_sent → approved → posting → posted
```

**`posting_jobs`** — One row per platform per posting attempt
```
id uuid PK
draft_id uuid FK
tenant_id uuid FK
platform text
status text            -- queued → posting → posted → failed
postiz_post_id text    -- returned by Postiz on success
posted_at timestamptz
```

**`reference_photos`** — User-uploaded creative reference images
```
id uuid PK
tenant_id uuid FK
storage_path text      -- Supabase Storage path
label text             -- 'product', 'owner', 'partner', 'other'
uploaded_at timestamptz
```

### Autopilot Tables

**`autopilot_configs`** — One row per tenant — autopilot mode, schedule, limits
```
id uuid PK
tenant_id uuid FK UNIQUE
mode autopilot_mode    -- 'off', 'full_autopilot', 'smart_queue'
schedule_cron text     -- validated cron expression (UTC)
schedule_description text  -- human-readable ("Mon/Wed/Fri at 10:00 AM")
timezone text          -- IANA timezone for schedule display
platform_targets text[]
smart_queue_timeout_minutes int  -- default 120
daily_post_limit int   -- default 3 (hard ceiling: 10)
weekly_post_limit int  -- default 15
monthly_cost_cap_usd numeric  -- default 50 (hard ceiling: 100)
content_mix jsonb      -- {"promotional": 40, "educational": 30, ...}
consecutive_failures int  -- auto-pause at 3
paused_at timestamptz  -- NULL when active
next_run_at timestamptz  -- dispatcher checks this
warmup_posts_remaining int  -- first 5 = Smart Queue regardless
```

**`autopilot_topics`** — Generated topics and their lifecycle
```
id uuid PK
tenant_id uuid FK
topic text
category text          -- matches content_mix keys
status topic_status    -- queued → generating → previewing → posted/rejected/failed
content_request_id uuid FK  -- linked content_request
draft_id uuid FK       -- linked content_draft
auto_approve_at timestamptz  -- Smart Queue deadline
```

**`autopilot_runs`** — Run history for auditing
```
id uuid PK
tenant_id uuid FK
triggered_at timestamptz
topics_generated int
posts_created int
posts_failed int
cost_usd numeric
```

### Learning Tables

**`preference_signals`** — Accumulated learning from user behavior
```
id uuid PK
tenant_id uuid FK
signal_type text        -- 'approval_structural', 'edit_pattern', 'engagement'
feature text            -- 'word_count', 'formula', 'emoji', etc.
value text              -- 'short', 'hook_story_offer', 'no_emoji'
occurrences int         -- times this preference was observed
total_opportunities int -- times it could have been observed
confidence float        -- occurrences / total_opportunities
lesson_text text        -- Haiku-generated lesson (edit patterns only)
last_seen_at timestamptz
```

**`feedback_events`** (extended columns)
```
chosen_option_idx int       -- which option was picked (0-indexed)
chosen_formula text         -- formula of the chosen option
original_caption text       -- caption before edit
edit_instruction text       -- user's edit instruction
all_options jsonb           -- all 3 caption variant dicts (for structural diff)
```

**`few_shot_examples`** (extended columns)
```
formula text                -- copywriting formula used
draft_id uuid FK            -- links to content_drafts for engagement tracking
```

**`engagement_metrics`** (extended columns)
```
tenant_id uuid FK           -- for tenant-scoped queries
draft_id uuid FK            -- links to content_drafts
```

---

## Autopilot Architecture

Autopilot uses a **single dispatcher pattern** instead of per-tenant pg_cron jobs (which don't scale and are vulnerable to SQL injection).

```
pg_cron (every 5 min)
 └─► INSERT 'autopilot_dispatch' job into job_queue
      └─► Worker picks up dispatch job
           └─► Query autopilot_configs WHERE next_run_at <= now() AND not paused
                └─► For each due tenant: INSERT 'autopilot_generate' job
                     └─► Worker picks up per-tenant job
                          ├─► Check guardrails (daily/weekly limits, cost cap)
                          ├─► Claude Haiku generates topic (deduped against last 14 days)
                          ├─► Full Autopilot: Haiku moderation pass
                          ├─► Create content_request + enqueue generate_content
                          └─► Smart Queue: set auto_approve_at = now + timeout

pg_cron (every 5 min)
 └─► INSERT 'autopilot_timeout' job
      └─► Query topics WHERE status='previewing' AND auto_approve_at <= now()
           └─► Atomic conditional update (claim topic)
                └─► Call approve_draft() → enqueue posting
                     └─► Notify tenant: "Autopilot auto-posted: ..."
```

**Safety guardrails:**
- Daily post limit (default 3, hard ceiling 10)
- Weekly post limit (default 15)
- Monthly cost cap (default $50, hard ceiling $100)
- Auto-pause after 3 consecutive failures + Telegram notification
- Warmup period: first 5 posts always use Smart Queue (even in Full Autopilot mode)
- Full Autopilot: Claude Haiku moderation pass rejects potentially offensive content
- Atomic conditional updates prevent race conditions between user actions and timeout sweep

---

## Learning Architecture

The Invisible Learning Engine operates on three signal types, each with different confidence thresholds:

```
APPROVAL SIGNAL (low confidence — needs 8+ observations)
  User picks Option 2
  └─► Structural Diff: compare features of all 3 options
       ├─► Chosen: short, punchy_one_liner, no emoji
       └─► Rejected: long, hook_story_offer, has emoji
            └─► Upsert preference_signals: word_count=short (1/1)
                 After 8+ consistent picks → soft nudge in prompt

EDIT SIGNAL (high confidence — needs 2-3 observations)
  User edits: "make it shorter, remove exclamation marks"
  └─► Claude Haiku analyzes the triple (original → instruction → result)
       └─► Extracts: {"feature": "exclamation", "value": "none"}
            └─► Upsert preference_signals at confidence 0.5 (first edit)
                 After 2nd consistent edit → confidence 0.75 → hard rule

ENGAGEMENT SIGNAL (audience truth — needs 5+ posts)
  Platform API returns: 47 likes, 12 comments, 3 shares, 890 views
  └─► Compute engagement score: (47 + 12×3 + 3×5) / 890 × 1000 = 100.2 → 10.0
       └─► Update few_shot_examples.engagement_score
            └─► Overrides approval patterns if audience disagrees
```

Learned preferences are injected into the system prompt as **Layer 11**:
- **Hard rules** (from edits): "Keep captions under 60 words", "No exclamation marks"
- **Soft preferences** (from approvals): "You tend to pick question hooks (8 of 11 times)"
- **Formula performance** (from stats): ranked formulas with approval rate + engagement score
- **Wildcard enforcement**: Option 3 always uses a formula NOT in the top 2

Few-shot example selection uses recency decay with floor (`max(score × 0.95^days, score × 0.3)`) and formula diversity (max 2 examples per formula).

---

## Queue System (pgmq)

Scribario uses [pgmq](https://github.com/tembo-io/pgmq) — a Postgres-native message queue — instead of Redis or RabbitMQ. This keeps the infrastructure footprint small (everything in Supabase) while providing durable, at-least-once job delivery.

**Queues:**

| Queue | Producer | Consumer | Job Type |
|---|---|---|---|
| `content_generation` | `intake.py` | `generate_content.py` | Run pipeline (image or inline video), store draft, send preview |
| `content_generation` | pg_cron (5min) | `autopilot_dispatch.py` | Query due tenants, enqueue per-tenant generation |
| `content_generation` | `autopilot_dispatch.py` | `autopilot_generate.py` | Generate topic + enqueue content pipeline for one tenant |
| `content_generation` | pg_cron (5min) | `autopilot_timeout.py` | Auto-approve Smart Queue previews past deadline |
| `content_generation` | pg_cron (Sun 9am) | `autopilot_digest.py` | Send weekly summary to autopilot tenants |
| `posting` | `approval.py` | `post_content.py` | Post approved draft via Postiz |

**Visibility timeout:** Jobs become visible again after 30s if not explicitly deleted, providing automatic retry on worker crash.

**Idempotency:** Every job carries an `idempotency_key = hash(request_id + job_type)` to prevent double-processing on retry.

---

## API Integrations

### Anthropic Claude API
- **Intake Agent** (Haiku): Intent classification — proceed / ask for photo / ask for clarity (~$0.001/call)
- **Prompt Engine** (Sonnet): Structured `GenerationPlan` output via tool_use (~$0.04/call)
- **Caption generation** (Sonnet): 3 caption options with 5 copywriting formulas (Hook-Story-Offer, PAS, Punchy One-Liner, Story-Lesson, List/Value Drop)
- **Brand profile generation**: AI-assisted from website scraping

### Kie.ai Nano Banana 2
- Used for: Image generation from visual prompts, video start/end frame generation
- Pattern: Parallel async requests (3 images simultaneously, ~25s total)
- Reference images: Up to 14 per scene (10 object fidelity + 4 character consistency)

### Google Veo 3.1
- Used for: Video clip generation (8s clips from start/end frames)
- Modes: TEXT_2_VIDEO, FIRST_AND_LAST_FRAMES_2_VIDEO, REFERENCE_2_VIDEO
- Cost: ~$0.40/clip

### ElevenLabs
- **TTS**: Scene voiceover generation with gender-aware voice pool rotation
- **SFX**: Sound effect generation from scene descriptions
- Voice pool stored in `brand_profiles.voice_pool` JSONB — new voices auto-appended after creation

### Postiz API
- Used for: Social media publishing — Facebook, Instagram, LinkedIn, Bluesky (more coming)
- Pattern: REST API — upload media, create post, attach to social account
- Auth: API key + org ID in headers
- Self-hosted at `https://postiz.scribario.com`

### Telegram Bot API
- Used for: Receiving messages, sending previews with inline keyboards, confirmation messages
- Library: aiogram 3.x with long-polling
- Pattern: Callback queries for approve/reject/regenerate actions

---

## Multi-Tenancy Model

Every table carries `tenant_id uuid NOT NULL`. Row-level security (RLS) is enabled on all tables.

**Service role key** (used by workers) bypasses RLS but workers always include an explicit `.eq("tenant_id", tenant_id)` clause on every query — defense in depth against data leakage.

**User-facing Supabase queries** use the anon key with RLS enforced — users can only see their own tenant's data.

OAuth tokens for social accounts are stored in Supabase Vault (encrypted) and referenced by ID only in the `posting_jobs` table.

---

## Infrastructure

- **VPS:** Hostinger (31.97.13.213)
  - `systemd: scribario-bot.service` — Python bot (aiogram 3.x)
  - `systemd: scribario-worker.service` — Python worker (pgmq poller)
  - `Docker: Postiz` — Social publishing engine (postiz.scribario.com)
  - `Docker: Redis 7` — FSM storage for bot state (survives restarts)
  - `nginx + Let's Encrypt` — SSL termination
- **Supabase** (managed) — Postgres + Storage + pgmq + pg_cron
- **Domain:** scribario.com → VPS

---

## Cost Per Content Type

### Image Post (3 images + captions)

| Component | Cost |
|-----------|------|
| Intake Agent (Haiku) | $0.002 |
| Prompt Engine (Sonnet) | $0.04 |
| Nano Banana 2 images (3 @ $0.04) | $0.12 |
| **Total** | **~$0.16** |

### Short Video (single 8s clip, inline with captions)

| Component | Cost |
|-----------|------|
| Intake Agent (Haiku) | $0.002 |
| Prompt Engine (Sonnet) | $0.04 |
| Video prompt generation | $0.02 |
| Nano Banana 2 scene image (1 @ $0.04) | $0.04 |
| Veo Fast via Kie.ai | $0.40 |
| **Total** | **~$0.50** |

### Autopilot Post (topic + image post, auto-generated)

| Component | Cost |
|-----------|------|
| Topic generation (Haiku) | $0.0003 |
| Moderation check (Haiku, Full Autopilot only) | $0.0001 |
| Prompt Engine (Sonnet) | $0.04 |
| Nano Banana 2 images (3 @ $0.04) | $0.12 |
| **Total** | **~$0.16** |

*Autopilot adds ~$0.0004 per post for topic generation + moderation. The bulk of the cost is the same image pipeline as manual posts.*

### Learning (per interaction, invisible)

| Component | Cost |
|-----------|------|
| Structural diff (approval) | $0 (pure Python) |
| Edit analysis (Haiku) | $0.001 |
| Preference accumulation | $0 (DB upsert) |
| **Total per approval** | **$0** |
| **Total per edit** | **~$0.001** |

### Long Video (4 scenes, ~30s) — DEPRECATED

| Component | Cost |
|-----------|------|
| Intake Agent (Haiku) | $0.002 |
| Prompt Engine (Sonnet) | $0.04 |
| ElevenLabs TTS (4 scenes) | $0.07 |
| ElevenLabs SFX (4 scenes) | $0.09 |
| Nano Banana 2 frames (8 @ $0.04) | $0.32 |
| Veo 3 Fast via Kie.ai (4 clips @ $0.40) | $1.60 |
| FFmpeg | Free |
| **Total** | **~$2.18** |

*Prices verified against live source pages 2026-03-13. See [COST-ANALYSIS.md](COST-ANALYSIS.md) for full breakdown with citations.*
