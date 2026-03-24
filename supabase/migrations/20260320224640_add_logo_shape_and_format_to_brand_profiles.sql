-- Logo metadata columns for shape-aware prompt hints
ALTER TABLE brand_profiles ADD COLUMN IF NOT EXISTS logo_shape text;
ALTER TABLE brand_profiles ADD COLUMN IF NOT EXISTS logo_format text;

COMMENT ON COLUMN brand_profiles.logo_shape IS 'Logo aspect ratio hint: square, horizontal, or vertical';
COMMENT ON COLUMN brand_profiles.logo_format IS 'Logo file format: png or jpeg';
