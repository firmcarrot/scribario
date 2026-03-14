-- Create storage bucket for long-form videos
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'long-videos',
    'long-videos',
    false,
    52428800,  -- 50MB limit
    ARRAY['video/mp4']
)
ON CONFLICT (id) DO NOTHING;

-- RLS: service role can do anything
CREATE POLICY "service_role_long_videos" ON storage.objects
    FOR ALL TO service_role
    USING (bucket_id = 'long-videos')
    WITH CHECK (bucket_id = 'long-videos');
