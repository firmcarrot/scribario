-- Phase 0A: Fix feedback_action enum (add missing values)
ALTER TYPE feedback_action ADD VALUE IF NOT EXISTS 'approve_video';
ALTER TYPE feedback_action ADD VALUE IF NOT EXISTS 'make_video';
ALTER TYPE feedback_action ADD VALUE IF NOT EXISTS 'reject_video';

-- Phase 1A: Add chosen option tracking to feedback_events
ALTER TABLE feedback_events ADD COLUMN IF NOT EXISTS chosen_option_idx int;
ALTER TABLE feedback_events ADD COLUMN IF NOT EXISTS chosen_formula text;

-- Phase 1B: Add edit context to feedback_events
ALTER TABLE feedback_events ADD COLUMN IF NOT EXISTS original_caption text;
ALTER TABLE feedback_events ADD COLUMN IF NOT EXISTS edit_instruction text;

-- Phase 1D: Add all_options for structural diff
ALTER TABLE feedback_events ADD COLUMN IF NOT EXISTS all_options jsonb;

-- Phase 1C: Add formula + draft_id to few_shot_examples
ALTER TABLE few_shot_examples ADD COLUMN IF NOT EXISTS formula text;
ALTER TABLE few_shot_examples ADD COLUMN IF NOT EXISTS draft_id uuid REFERENCES content_drafts(id);

-- Phase 4B: Add tenant_id and draft_id to engagement_metrics
ALTER TABLE engagement_metrics ADD COLUMN IF NOT EXISTS tenant_id uuid REFERENCES tenants(id);
ALTER TABLE engagement_metrics ADD COLUMN IF NOT EXISTS draft_id uuid REFERENCES content_drafts(id);

-- Phase 2B: Create preference_signals table
CREATE TABLE IF NOT EXISTS preference_signals (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    signal_type text NOT NULL,
    feature text NOT NULL,
    value text NOT NULL,
    occurrences int NOT NULL DEFAULT 1,
    total_opportunities int NOT NULL DEFAULT 1,
    confidence float NOT NULL DEFAULT 0.0,
    lesson_text text,
    last_seen_at timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(tenant_id, signal_type, feature, value)
);

-- RLS for preference_signals
ALTER TABLE preference_signals ENABLE ROW LEVEL SECURITY;
CREATE POLICY service_only ON preference_signals FOR ALL USING (auth.role() = 'service_role');

-- Index for fast tenant lookups
CREATE INDEX IF NOT EXISTS idx_preference_signals_tenant ON preference_signals(tenant_id);
CREATE INDEX IF NOT EXISTS idx_preference_signals_confidence ON preference_signals(tenant_id, confidence) WHERE confidence >= 0.5;

-- Index for engagement_metrics tenant lookups
CREATE INDEX IF NOT EXISTS idx_engagement_metrics_tenant ON engagement_metrics(tenant_id);
CREATE INDEX IF NOT EXISTS idx_engagement_metrics_draft ON engagement_metrics(draft_id);
