ALTER TABLE content_requests ADD COLUMN IF NOT EXISTS generate_video boolean DEFAULT false;
ALTER TABLE content_requests ADD COLUMN IF NOT EXISTS video_aspect_ratio text;
