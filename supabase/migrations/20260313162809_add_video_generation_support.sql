-- Create videos storage bucket
INSERT INTO storage.buckets (id, name, public) VALUES ('videos', 'videos', false);

-- RLS policy for videos bucket: only service role (bypasses RLS) can access
CREATE POLICY "Service role only on videos"
  ON storage.objects FOR ALL
  USING (false)
  WITH CHECK (false);
