ALTER TABLE brand_profiles
  ADD COLUMN IF NOT EXISTS voice_pool JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN brand_profiles.voice_pool IS
  'Array of {voice_id, gender, style_label} for voice rotation across videos';
