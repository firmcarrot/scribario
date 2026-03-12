ALTER TABLE brand_profiles
  ADD COLUMN IF NOT EXISTS default_image_style text DEFAULT 'photorealistic'
  CHECK (default_image_style IN ('photorealistic', 'cartoon', 'cinematic', 'watercolor'));

ALTER TABLE content_requests
  ADD COLUMN IF NOT EXISTS style_override text
  CHECK (style_override IN ('photorealistic', 'cartoon', 'cinematic', 'watercolor'));
