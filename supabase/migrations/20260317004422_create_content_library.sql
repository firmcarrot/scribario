-- Content Library: stores unchosen caption+media options for free reuse
CREATE TABLE content_library (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_draft_id uuid NOT NULL REFERENCES content_drafts(id) ON DELETE CASCADE,
    caption text NOT NULL,
    image_url text,
    video_url text,
    media_type text NOT NULL CHECK (media_type IN ('image', 'video')),
    platform_targets text[],
    saved_at timestamptz NOT NULL DEFAULT now(),
    posted_at timestamptz,
    status text NOT NULL DEFAULT 'saved' CHECK (status IN ('saved', 'posted', 'deleted')),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Index for browsing: tenant's saved items newest first
CREATE INDEX idx_content_library_browse ON content_library (tenant_id, status, saved_at DESC);

-- Index for dedup checks by source draft
CREATE INDEX idx_content_library_source ON content_library (source_draft_id);

-- RLS enabled: service role bypasses, but defense-in-depth
-- No user-facing RLS policies needed — bot uses service role key exclusively
-- Tenant isolation enforced in application code via .eq("tenant_id", tenant_id)
ALTER TABLE content_library ENABLE ROW LEVEL SECURITY;
