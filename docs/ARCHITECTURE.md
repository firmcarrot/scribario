# Scribario — Architecture

## System Overview

Scribario is built around a simple invariant: **all business logic lives in the pipeline and worker, never in the bot.** The Telegram bot is a thin UI layer. State transitions are database writes. The worker is a dumb job processor.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SCRIBARIO SYSTEM                               │
│                                                                          │
│  ┌──────────────┐     ┌───────────────────────────────────────────────┐ │
│  │   TELEGRAM   │     │                  SUPABASE                     │ │
│  │              │     │                                               │ │
│  │  @Scribario  │ ──► │  ┌────────────┐   ┌────────────────────────┐ │ │
│  │  Bot (user   │     │  │  Postgres  │   │        pgmq            │ │ │
│  │  interface)  │ ◄── │  │  (state +  │   │  content_generation    │ │ │
│  │              │     │  │   data)    │   │  posting               │ │ │
│  └──────────────┘     │  └─────┬──────┘   └──────────┬─────────────┘ │ │
│                        │        │                      │               │ │
│                        └────────┼──────────────────────┼───────────────┘ │
│                                 │                      │                  │
│                        ┌────────┼──────────────────────┼─────────────┐   │
│                        │        ▼                      ▼             │   │
│                        │   ┌──────────┐         ┌──────────┐         │   │
│                        │   │ PIPELINE │         │  WORKER  │         │   │
│                        │   │          │         │  (async  │         │   │
│                        │   │ caption  │         │  pgmq    │         │   │
│                        │   │ image    │         │  poller) │         │   │
│                        │   │ brand    │         │          │         │   │
│                        │   └────┬─────┘         └────┬─────┘         │   │
│                        │        │                    │                │   │
│                        └────────┼────────────────────┼────────────────┘   │
│                                 │                    │                    │
│              ┌──────────────────┼────────────────────┼──────────────────┐ │
│              │   EXTERNAL APIs  │                    │                  │ │
│              │                  ▼                    ▼                  │ │
│              │  ┌────────────┐  ┌──────────┐  ┌──────────────────────┐ │ │
│              │  │ Claude API │  │  Kie.ai  │  │       Postiz         │ │ │
│              │  │ (captions) │  │  (images)│  │  (social publishing) │ │ │
│              │  └────────────┘  └──────────┘  └──────────────────────┘ │ │
│              └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

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
| `services/telegram.py` | Outbound message builders (preview cards, status messages) |
| `services/postiz.py` | Postiz API client |
| `services/postiz_oauth.py` | OAuth flow for connecting social accounts |
| `services/storage.py` | Supabase Storage upload helpers |

**Key design decisions:**
- Bot never calls Claude or Kie.ai directly — it only writes to the database and enqueues jobs
- All approval state is in `content_drafts` — the bot is stateless between messages
- aiogram-dialog handles multi-step flows (onboarding) with explicit state machines

### Pipeline (`pipeline/`)

The content generation engine. Called by workers, never by the bot directly.

| File | Responsibility |
|---|---|
| `orchestrator.py` | Coordinates the full caption → image → draft flow |
| `caption_gen.py` | Claude API client — generates 3 caption + visual prompt options |
| `image_gen.py` | Kie.ai Nano Banana 2 client — generates images in parallel |
| `brand_voice.py` | Loads brand profile + few-shot examples from DB |
| `brand_gen.py` | AI-assisted brand profile generation from website scraping |
| `posting.py` | Postiz posting wrapper |
| `scraper.py` | Website content scraper for brand setup |
| `social_scraper.py` | Social media content scraper |

**Generation order:** Captions are generated first because the caption contains the `visual_prompt` that drives the image. This produces better brand alignment than image-first generation.

### Worker (`worker/`)

A long-running async process that polls pgmq queues and dispatches job handlers.

| File | Responsibility |
|---|---|
| `main.py` | Queue poller — polls both queues, dispatches handlers, handles errors |
| `jobs/generate_content.py` | Runs the pipeline for a content_request, stores draft, sends preview |
| `jobs/generate_caption.py` | Caption-only generation |
| `jobs/generate_image.py` | Image-only generation |
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
   └─► Call Kie.ai in parallel → generate 3 images from visual_prompts

5. DRAFT STORED
   ├─► Upload 3 images to Supabase Storage
   ├─► Insert into content_drafts (status: "preview_sent")
   └─► Update content_requests (status: "preview_sent")

6. PREVIEW SENT
   worker/jobs/generate_content.py:
   └─► Call Telegram API → send message with 3 inline keyboards
       [Approve #1] [Approve #2] [Approve #3] [Reject All] [Regenerate]

7. USER APPROVES
   User taps "Approve #2"
   └─► bot/handlers/approval.py receives callback_query

8. APPROVAL PROCESSED
   ├─► Update content_drafts (status: "approved", approved_option: 2)
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
uploaded_at timestamptz
```

---

## Queue System (pgmq)

Scribario uses [pgmq](https://github.com/tembo-io/pgmq) — a Postgres-native message queue — instead of Redis or RabbitMQ. This keeps the infrastructure footprint small (everything in Supabase) while providing durable, at-least-once job delivery.

**Queues:**

| Queue | Producer | Consumer | Job Type |
|---|---|---|---|
| `content_generation` | `intake.py` | `generate_content.py` | Run pipeline, store draft, send preview |
| `posting` | `approval.py` | `post_content.py` | Post approved draft via Postiz |

**Visibility timeout:** Jobs become visible again after 30s if not explicitly deleted, providing automatic retry on worker crash.

**Idempotency:** Every job carries an `idempotency_key = hash(request_id + job_type)` to prevent double-processing on retry.

---

## API Integrations

### Anthropic Claude API
- Used for: Caption generation (3 options per request), brand profile generation, intent parsing
- Model: Claude claude-sonnet-4-6 (configurable)
- Pattern: Structured outputs with explicit JSON schema for caption + visual_prompt

### Kie.ai Nano Banana 2
- Used for: Image generation from visual prompts
- Pattern: Parallel async requests (3 images generated simultaneously, ~25s total)
- Provider abstraction: `ImageGenerationService` wraps the API — swap providers without touching the pipeline

### Postiz API
- Used for: Social media publishing — Facebook, Instagram, LinkedIn, X (Twitter), TikTok, YouTube, Bluesky, Pinterest, Threads
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

```
┌──────────────────────────────────────────┐
│           Hostinger VPS                  │
│           (31.97.13.213)                 │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  systemd: scribario-bot.service    │  │
│  │  python -m bot.main                │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  systemd: scribario-worker.service │  │
│  │  python -m worker.main             │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  Docker: Postiz                    │  │
│  │  nginx → postiz.scribario.com      │  │
│  │  Let's Encrypt SSL                 │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
            │              │
            ▼              ▼
     Supabase         Telegram API
     (managed)
```
