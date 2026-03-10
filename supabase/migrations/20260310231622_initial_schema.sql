-- Scribario initial schema
-- Multi-tenant social media content creation + auto-posting platform

-- ============================================================
-- ENUMS (state machines)
-- ============================================================

CREATE TYPE content_source AS ENUM ('manual', 'scheduled', 'campaign');
CREATE TYPE content_request_status AS ENUM ('pending', 'generating', 'preview_ready', 'sent_to_telegram', 'expired');
CREATE TYPE content_draft_status AS ENUM ('generating', 'generated', 'previewing', 'approved', 'rejected', 'edit_requested', 'expired');
CREATE TYPE posting_job_status AS ENUM ('queued', 'posting', 'posted', 'failed');
CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected', 'expired');
CREATE TYPE feedback_action AS ENUM ('approve', 'reject', 'edit', 'regenerate');
CREATE TYPE member_role AS ENUM ('owner', 'admin', 'member');

-- ============================================================
-- CORE TABLES
-- ============================================================

-- Multi-tenancy foundation
CREATE TABLE tenants (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    slug text UNIQUE NOT NULL,
    auto_approve_after interval DEFAULT '24 hours',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE tenant_members (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    telegram_user_id bigint NOT NULL,
    role member_role NOT NULL DEFAULT 'member',
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, telegram_user_id)
);

-- Reverse lookup: telegram user → tenant
CREATE INDEX idx_tenant_members_telegram ON tenant_members(telegram_user_id);

-- ============================================================
-- BRAND IDENTITY
-- ============================================================

CREATE TABLE brand_profiles (
    tenant_id uuid PRIMARY KEY REFERENCES tenants(id) ON DELETE CASCADE,
    tone_words text[] NOT NULL DEFAULT '{}',
    audience_description text NOT NULL DEFAULT '',
    do_list text[] NOT NULL DEFAULT '{}',
    dont_list text[] NOT NULL DEFAULT '{}',
    product_catalog jsonb DEFAULT '{}',
    compliance_notes text NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE few_shot_examples (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    platform text NOT NULL,
    content_type text NOT NULL,
    caption text NOT NULL,
    image_url text,
    engagement_score numeric,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_few_shot_tenant_platform ON few_shot_examples(tenant_id, platform);

CREATE TABLE platform_connections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    platform text NOT NULL,
    oauth_token_vault_ref text, -- references Supabase Vault
    username text,
    is_active boolean NOT NULL DEFAULT true,
    connected_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, platform)
);

-- ============================================================
-- CONTENT PIPELINE
-- ============================================================

CREATE TABLE content_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source content_source NOT NULL DEFAULT 'manual',
    intent text NOT NULL,
    platform_targets text[] NOT NULL DEFAULT '{instagram}',
    due_at timestamptz,
    status content_request_status NOT NULL DEFAULT 'pending',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_content_requests_tenant ON content_requests(tenant_id, created_at DESC);
CREATE INDEX idx_content_requests_status ON content_requests(status) WHERE status NOT IN ('expired');

CREATE TABLE content_drafts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id uuid NOT NULL REFERENCES content_requests(id) ON DELETE CASCADE,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    caption_variants jsonb NOT NULL DEFAULT '[]',
    image_urls text[] NOT NULL DEFAULT '{}',
    video_url text,
    voiceover_url text,
    platform_versions jsonb DEFAULT '{}',
    status content_draft_status NOT NULL DEFAULT 'generating',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_content_drafts_request ON content_drafts(request_id);
CREATE INDEX idx_content_drafts_tenant ON content_drafts(tenant_id, created_at DESC);

CREATE TABLE approval_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id uuid NOT NULL REFERENCES content_drafts(id) ON DELETE CASCADE,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    telegram_message_id bigint,
    telegram_chat_id bigint,
    callback_data text,
    status approval_status NOT NULL DEFAULT 'pending',
    responded_at timestamptz,
    feedback_tags text[] DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_approval_draft ON approval_requests(draft_id);

-- ============================================================
-- POSTING
-- ============================================================

CREATE TABLE posting_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id uuid NOT NULL REFERENCES content_drafts(id) ON DELETE CASCADE,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    platform text NOT NULL,
    asset_urls text[] NOT NULL DEFAULT '{}',
    caption text NOT NULL,
    scheduled_for timestamptz,
    status posting_job_status NOT NULL DEFAULT 'queued',
    idempotency_key text UNIQUE NOT NULL,
    retry_count int NOT NULL DEFAULT 0,
    max_retries int NOT NULL DEFAULT 3,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_posting_jobs_status ON posting_jobs(status) WHERE status IN ('queued', 'posting');
CREATE INDEX idx_posting_jobs_tenant ON posting_jobs(tenant_id);

CREATE TABLE posting_results (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id uuid NOT NULL REFERENCES posting_jobs(id) ON DELETE CASCADE,
    platform text NOT NULL,
    platform_post_id text,
    platform_url text,
    success boolean NOT NULL,
    error_message text,
    posted_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_posting_results_job ON posting_results(job_id);

-- ============================================================
-- ANALYTICS & FEEDBACK
-- ============================================================

CREATE TABLE engagement_metrics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    result_id uuid NOT NULL REFERENCES posting_results(id) ON DELETE CASCADE,
    platform text NOT NULL,
    likes int DEFAULT 0,
    comments int DEFAULT 0,
    shares int DEFAULT 0,
    views int DEFAULT 0,
    fetched_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE feedback_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id uuid NOT NULL REFERENCES content_drafts(id) ON DELETE CASCADE,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    action feedback_action NOT NULL,
    reason_tags text[] DEFAULT '{}',
    edited_caption text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_feedback_tenant ON feedback_events(tenant_id, created_at DESC);

-- ============================================================
-- COST TRACKING
-- ============================================================

CREATE TABLE usage_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    event_type text NOT NULL,  -- 'image_generation', 'caption_generation', 'posting'
    provider text NOT NULL,    -- 'kie_ai', 'anthropic', 'postiz'
    cost_usd numeric NOT NULL DEFAULT 0,
    metadata jsonb DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_usage_tenant ON usage_events(tenant_id, created_at DESC);
CREATE INDEX idx_usage_type ON usage_events(event_type, created_at DESC);

-- ============================================================
-- JOB QUEUE (pgmq fallback — used if pgmq extension unavailable)
-- ============================================================

CREATE TABLE job_queue (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    queue_name text NOT NULL DEFAULT 'default',
    job_type text NOT NULL,
    payload jsonb NOT NULL,
    status text NOT NULL DEFAULT 'queued',  -- queued, processing, completed, failed, dead
    idempotency_key text UNIQUE,
    retry_count int NOT NULL DEFAULT 0,
    max_retries int NOT NULL DEFAULT 3,
    locked_at timestamptz,
    locked_by text,
    completed_at timestamptz,
    failed_at timestamptz,
    error_message text,
    created_at timestamptz NOT NULL DEFAULT now(),
    scheduled_for timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_job_queue_poll ON job_queue(queue_name, status, scheduled_for)
    WHERE status = 'queued';
CREATE INDEX idx_job_queue_locked ON job_queue(status, locked_at)
    WHERE status = 'processing';

-- ============================================================
-- RLS POLICIES
-- ============================================================

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE few_shot_examples ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE engagement_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_queue ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS, so these policies are for anon/authenticated access.
-- For MVP, the bot uses service_role key with explicit tenant_id filtering.
-- These policies will be tightened when we add user-facing dashboard (Phase 4).

-- Allow service role full access (implicit — service_role bypasses RLS)
-- Allow authenticated users to see their own tenant data
CREATE POLICY tenant_member_access ON tenants
    FOR SELECT USING (
        id IN (SELECT tenant_id FROM tenant_members WHERE telegram_user_id = (current_setting('app.telegram_user_id', true))::bigint)
    );

-- ============================================================
-- UPDATED_AT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER brand_profiles_updated_at
    BEFORE UPDATE ON brand_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
