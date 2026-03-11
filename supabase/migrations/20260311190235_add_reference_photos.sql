-- Photo label enum
CREATE TYPE photo_label AS ENUM ('owner', 'partner', 'product', 'other');

-- Reference photos table
CREATE TABLE reference_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    uploaded_by BIGINT NOT NULL,
    label photo_label NOT NULL DEFAULT 'other',
    storage_path TEXT NOT NULL,
    file_unique_id TEXT NOT NULL,
    file_size_bytes INTEGER,
    mime_type TEXT,
    is_default BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ,
    UNIQUE (tenant_id, file_unique_id)
);

-- Index for fast default photo lookups
CREATE INDEX idx_ref_photos_tenant_defaults
    ON reference_photos (tenant_id, created_at DESC)
    WHERE is_default = true AND deleted_at IS NULL;

-- Index for all active photos by tenant
CREATE INDEX idx_ref_photos_tenant_active
    ON reference_photos (tenant_id, created_at DESC)
    WHERE deleted_at IS NULL;

-- RLS
ALTER TABLE reference_photos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_full_access" ON reference_photos
    USING (true)
    WITH CHECK (true);
