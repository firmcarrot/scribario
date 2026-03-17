-- Deny-all policy for defense-in-depth (service role bypasses RLS)
CREATE POLICY service_only ON content_library FOR ALL USING (false);
