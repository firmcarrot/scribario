-- Dashboard RPC functions for admin app
-- Step 1: Daily costs, daily analytics, budget alerts

-- Daily cost aggregation for the cost chart (30 days)
CREATE OR REPLACE FUNCTION get_daily_costs_30d()
RETURNS TABLE(day date, total_cost numeric, event_count bigint)
LANGUAGE sql STABLE
AS $$
  SELECT
    d.day,
    COALESCE(SUM(ue.cost_usd), 0) AS total_cost,
    COUNT(ue.id) AS event_count
  FROM generate_series(
    (now() - interval '30 days')::date,
    now()::date,
    '1 day'
  ) AS d(day)
  LEFT JOIN usage_events ue
    ON ue.created_at::date = d.day
  GROUP BY d.day
  ORDER BY d.day;
$$;

-- Daily analytics aggregation for time-series charts (30 days)
CREATE OR REPLACE FUNCTION get_daily_analytics_30d()
RETURNS TABLE(
  day date,
  requests bigint,
  approvals bigint,
  rejections bigint,
  regenerations bigint,
  distinct_tenants bigint
)
LANGUAGE sql STABLE
AS $$
  SELECT
    d.day,
    COALESCE(cr.cnt, 0),
    COALESCE(fb_a.cnt, 0),
    COALESCE(fb_r.cnt, 0),
    COALESCE(fb_g.cnt, 0),
    COALESCE(cr.tenants, 0)
  FROM generate_series(
    (now() - interval '30 days')::date,
    now()::date,
    '1 day'
  ) AS d(day)
  LEFT JOIN LATERAL (
    SELECT COUNT(*) AS cnt, COUNT(DISTINCT tenant_id) AS tenants
    FROM content_requests
    WHERE created_at::date = d.day
  ) cr ON true
  LEFT JOIN LATERAL (
    SELECT COUNT(*) AS cnt FROM feedback_events
    WHERE action = 'approve' AND created_at::date = d.day
  ) fb_a ON true
  LEFT JOIN LATERAL (
    SELECT COUNT(*) AS cnt FROM feedback_events
    WHERE action = 'reject' AND created_at::date = d.day
  ) fb_r ON true
  LEFT JOIN LATERAL (
    SELECT COUNT(*) AS cnt FROM feedback_events
    WHERE action = 'regenerate' AND created_at::date = d.day
  ) fb_g ON true
  ORDER BY d.day;
$$;

-- Budget alerts: tenants at 80%+ of their cost limit
CREATE OR REPLACE FUNCTION get_budget_alerts()
RETURNS TABLE(
  tenant_id uuid,
  tenant_name text,
  plan_tier text,
  spend numeric,
  hard_limit numeric,
  pct_used numeric
)
LANGUAGE sql STABLE
AS $$
  SELECT
    t.id,
    t.name,
    t.plan_tier::text,
    COALESCE(s.total, 0),
    COALESCE(t.monthly_cost_hard_limit_usd, 2.0),
    CASE WHEN COALESCE(t.monthly_cost_hard_limit_usd, 2.0) > 0
      THEN ROUND(COALESCE(s.total, 0) / COALESCE(t.monthly_cost_hard_limit_usd, 2.0) * 100, 1)
      ELSE 0
    END
  FROM tenants t
  LEFT JOIN LATERAL (
    SELECT SUM(cost_usd) AS total
    FROM usage_events
    WHERE tenant_id = t.id
      AND created_at >= date_trunc('month', now())
  ) s ON true
  WHERE COALESCE(s.total, 0) / GREATEST(COALESCE(t.monthly_cost_hard_limit_usd, 2.0), 0.01) >= 0.8
  ORDER BY pct_used DESC;
$$;

-- Enable realtime on key tables for live dashboard updates
-- (safe to re-run: ADD TABLE is idempotent if already present)
DO $$
BEGIN
  ALTER PUBLICATION supabase_realtime ADD TABLE job_queue;
EXCEPTION WHEN duplicate_object THEN NULL;
END;
$$;

DO $$
BEGIN
  ALTER PUBLICATION supabase_realtime ADD TABLE usage_events;
EXCEPTION WHEN duplicate_object THEN NULL;
END;
$$;

DO $$
BEGIN
  ALTER PUBLICATION supabase_realtime ADD TABLE tenants;
EXCEPTION WHEN duplicate_object THEN NULL;
END;
$$;
