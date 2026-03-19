-- Phase 1E: Dashboard SQL Views / RPC Functions

-- RPC: get tenant monthly spend (used by bot budget checks + dashboard)
CREATE OR REPLACE FUNCTION get_tenant_monthly_spend(p_tenant_id uuid)
RETURNS TABLE(total_cost_usd numeric, event_count bigint) AS $$
  SELECT COALESCE(SUM(cost_usd), 0), COUNT(*)
  FROM usage_events
  WHERE tenant_id = p_tenant_id
    AND created_at >= date_trunc('month', now());
$$ LANGUAGE sql STABLE;

-- RPC: monthly cost reset (called by pg_cron on 1st of each month)
CREATE OR REPLACE FUNCTION reset_monthly_posts()
RETURNS void AS $$
BEGIN
  UPDATE tenants
  SET monthly_posts_used = 0,
      monthly_posts_reset_at = now()
  WHERE subscription_status IN ('active', 'free_trial');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
