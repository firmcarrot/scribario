-- Fix RLS: Remove broken telegram_user_id policy, add service-role-only policies
-- The bot and worker use service_role key which bypasses RLS.
-- These policies explicitly document that non-service-role access is blocked
-- until we add proper JWT-based auth in Phase 4.

DROP POLICY IF EXISTS tenant_member_access ON tenants;

CREATE POLICY service_only ON tenants FOR ALL USING (false);
CREATE POLICY service_only ON tenant_members FOR ALL USING (false);
CREATE POLICY service_only ON brand_profiles FOR ALL USING (false);
CREATE POLICY service_only ON few_shot_examples FOR ALL USING (false);
CREATE POLICY service_only ON platform_connections FOR ALL USING (false);
CREATE POLICY service_only ON content_requests FOR ALL USING (false);
CREATE POLICY service_only ON content_drafts FOR ALL USING (false);
CREATE POLICY service_only ON approval_requests FOR ALL USING (false);
CREATE POLICY service_only ON posting_jobs FOR ALL USING (false);
CREATE POLICY service_only ON posting_results FOR ALL USING (false);
CREATE POLICY service_only ON engagement_metrics FOR ALL USING (false);
CREATE POLICY service_only ON feedback_events FOR ALL USING (false);
CREATE POLICY service_only ON usage_events FOR ALL USING (false);
CREATE POLICY service_only ON job_queue FOR ALL USING (false);
