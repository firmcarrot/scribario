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
| `handlers/approval.py` | Callback query handler — processes Approve / Reject / Regenerate |
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
| `system_prompt.py` | Layered prompt builder: role + format rules + scene rules + ref image strategy + quality rules + brand voice |
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
| `brand_voice.py` | Loads brand profile + few-shot examples from DB |
| `brand_gen.py` | AI-assisted brand profile generation from website scraping |
| `posting.py` | Postiz posting wrapper |

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

Workers run as a systemd service on the VPS. The polling interval and concurrency are configurable via environment variables.

### Supabase (Database + Queues)

Supabase provides Postgres, row-level security, pgmq for queuing, and pg_cron for scheduled jobs.

- **pgmq** handles the job queue with at-least-once delivery and automatic visibility timeouts
- **pg_cron** will handle scheduled posting in Phase 2
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

---

## Queue System (pgmq)

Scribario uses [pgmq](https://github.com/tembo-io/pgmq) — a Postgres-native message queue — instead of Redis or RabbitMQ. This keeps the infrastructure footprint small (everything in Supabase) while providing durable, at-least-once job delivery.

**Queues:**

| Queue | Producer | Consumer | Job Type |
|---|---|---|---|
| `content_generation` | `intake.py` | `generate_content.py` | Run pipeline (image or inline video), store draft, send preview |
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
