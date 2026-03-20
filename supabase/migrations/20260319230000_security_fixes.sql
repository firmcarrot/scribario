-- C3: Atomic keyword rotation — no more read-then-write race condition
CREATE OR REPLACE FUNCTION increment_keyword_usage(keyword_id uuid)
RETURNS void
LANGUAGE sql
AS $$
  UPDATE seo_keywords
  SET rotation_status = 'in_use',
      last_used_at = now(),
      times_used = times_used + 1
  WHERE id = keyword_id;
$$;

-- C4: Lock down admin RPCs — service_role only
REVOKE EXECUTE ON FUNCTION get_daily_costs_30d() FROM anon, authenticated;
REVOKE EXECUTE ON FUNCTION get_daily_analytics_30d() FROM anon, authenticated;
REVOKE EXECUTE ON FUNCTION get_budget_alerts() FROM anon, authenticated;
REVOKE EXECUTE ON FUNCTION increment_keyword_usage(uuid) FROM anon, authenticated;

REVOKE EXECUTE ON FUNCTION get_daily_costs_30d() FROM public;
REVOKE EXECUTE ON FUNCTION get_daily_analytics_30d() FROM public;
REVOKE EXECUTE ON FUNCTION get_budget_alerts() FROM public;
REVOKE EXECUTE ON FUNCTION increment_keyword_usage(uuid) FROM public;

GRANT EXECUTE ON FUNCTION get_daily_costs_30d() TO service_role;
GRANT EXECUTE ON FUNCTION get_daily_analytics_30d() TO service_role;
GRANT EXECUTE ON FUNCTION get_budget_alerts() TO service_role;
GRANT EXECUTE ON FUNCTION increment_keyword_usage(uuid) TO service_role;
