-- Long-form video pipeline tables

CREATE TABLE video_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    request_id UUID REFERENCES content_requests(id),
    status TEXT NOT NULL DEFAULT 'scripting',
    intent TEXT NOT NULL,
    script JSONB,
    voice_id TEXT,
    aspect_ratio TEXT DEFAULT '16:9',
    total_cost_usd NUMERIC(8,4) DEFAULT 0,
    final_video_url TEXT,
    final_duration_seconds NUMERIC(6,2),
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE video_scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES video_projects(id) ON DELETE CASCADE,
    scene_index INT NOT NULL,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    scene_type TEXT NOT NULL,
    voiceover_text TEXT,
    voiceover_audio_url TEXT,
    voiceover_duration_seconds NUMERIC(6,2),
    start_frame_url TEXT,
    end_frame_url TEXT,
    video_clip_url TEXT,
    clip_duration_seconds NUMERIC(6,2),
    sfx_url TEXT,
    sfx_description TEXT,
    video_prompt TEXT,
    status TEXT DEFAULT 'pending',
    cost_usd NUMERIC(8,4) DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(project_id, scene_index)
);

-- Indexes
CREATE INDEX idx_video_projects_tenant_id ON video_projects(tenant_id);
CREATE INDEX idx_video_projects_status ON video_projects(status);
CREATE INDEX idx_video_scenes_project_id ON video_scenes(project_id);

-- RLS
ALTER TABLE video_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_scenes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant_isolation_video_projects" ON video_projects
    FOR ALL USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY "tenant_isolation_video_scenes" ON video_scenes
    FOR ALL USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- Service role bypass
CREATE POLICY "service_role_video_projects" ON video_projects
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_video_scenes" ON video_scenes
    FOR ALL TO service_role USING (true) WITH CHECK (true);
