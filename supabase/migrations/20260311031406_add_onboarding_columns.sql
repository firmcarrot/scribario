-- Add onboarding support columns
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS website_url text;

ALTER TABLE tenant_members ADD COLUMN IF NOT EXISTS onboarding_status text NOT NULL DEFAULT 'pending';

ALTER TABLE brand_profiles ADD COLUMN IF NOT EXISTS scraped_data jsonb;

-- Index for looking up tenants in onboarding
CREATE INDEX IF NOT EXISTS idx_tenant_members_onboarding_status ON tenant_members(onboarding_status);

-- Update existing Mondo Shrimp member to complete
UPDATE tenant_members SET onboarding_status = 'complete' WHERE tenant_id = '52590da5-bc80-4161-ac13-62e9bcd75424';

-- RLS policy for new columns (same deny-all pattern)
-- Already covered by existing service_only policies on these tables
