-- Autopilot mode enum
CREATE TYPE autopilot_mode AS ENUM ('off', 'full_autopilot', 'smart_queue');

-- Topic status enum
CREATE TYPE topic_status AS ENUM ('queued', 'generating', 'previewing', 'posted', 'rejected', 'expired', 'failed');

-- Autopilot configuration per tenant (1:1)
CREATE TABLE autopilot_configs (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  mode autopilot_mode NOT NULL DEFAULT 'off',
  schedule_cron text,
  schedule_description text,
  timezone text NOT NULL DEFAULT 'America/New_York',
  platform_targets text[] DEFAULT '{}',
  smart_queue_timeout_minutes int NOT NULL DEFAULT 120,
  daily_post_limit int NOT NULL DEFAULT 3,
  weekly_post_limit int NOT NULL DEFAULT 15,
  monthly_cost_cap_usd numeric(8,2) NOT NULL DEFAULT 50.00,
  content_mix jsonb DEFAULT '{"promotional": 40, "educational": 30, "entertaining": 20, "behind_the_scenes": 10}',
  consecutive_failures int NOT NULL DEFAULT 0,
  paused_at timestamptz,
  next_run_at timestamptz,
  warmup_posts_remaining int NOT NULL DEFAULT 5,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(tenant_id)
);

-- Autopilot topics (generated content topics)
CREATE TABLE autopilot_topics (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  topic text NOT NULL,
  category text NOT NULL DEFAULT 'promotional',
  source text NOT NULL DEFAULT 'ai_generated',
  content_request_id uuid REFERENCES content_requests(id),
  draft_id uuid REFERENCES content_drafts(id),
  status topic_status NOT NULL DEFAULT 'queued',
  scheduled_for timestamptz,
  auto_approve_at timestamptz,
  telegram_preview_message_id bigint,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Autopilot run history
CREATE TABLE autopilot_runs (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  triggered_at timestamptz DEFAULT now(),
  topics_generated int DEFAULT 0,
  posts_created int DEFAULT 0,
  posts_failed int DEFAULT 0,
  cost_usd numeric(8,4) DEFAULT 0,
  error_message text,
  completed_at timestamptz
);

-- Indexes for dispatcher queries
CREATE INDEX idx_autopilot_configs_dispatch ON autopilot_configs (next_run_at) WHERE mode != 'off' AND paused_at IS NULL;
CREATE INDEX idx_autopilot_topics_tenant ON autopilot_topics (tenant_id, status);
CREATE INDEX idx_autopilot_topics_timeout ON autopilot_topics (auto_approve_at) WHERE status = 'previewing';
CREATE INDEX idx_autopilot_runs_tenant ON autopilot_runs (tenant_id, triggered_at DESC);

-- RLS (service-only, same pattern as content_library)
ALTER TABLE autopilot_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE autopilot_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE autopilot_runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY service_only ON autopilot_configs FOR ALL USING (false);
CREATE POLICY service_only ON autopilot_topics FOR ALL USING (false);
CREATE POLICY service_only ON autopilot_runs FOR ALL USING (false);
