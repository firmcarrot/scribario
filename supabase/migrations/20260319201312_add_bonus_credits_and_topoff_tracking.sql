-- Add bonus credits columns for top-off purchases
ALTER TABLE tenants
  ADD COLUMN IF NOT EXISTS bonus_posts integer NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS bonus_videos integer NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS bonus_posts_purchased_this_month integer NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS bonus_videos_purchased_this_month integer NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS trial_video_limit integer NOT NULL DEFAULT 1,
  ADD COLUMN IF NOT EXISTS trial_videos_used integer NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS current_period_end timestamptz;

-- Stripe webhook idempotency table
CREATE TABLE IF NOT EXISTS stripe_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id text NOT NULL UNIQUE,
  event_type text NOT NULL,
  processed_at timestamptz NOT NULL DEFAULT now(),
  payload jsonb
);

-- RLS: service role only
ALTER TABLE stripe_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY service_only ON stripe_events FOR ALL USING (auth.role() = 'service_role');

-- Atomic increment RPCs for budget enforcement (prevents race conditions)
CREATE OR REPLACE FUNCTION increment_post_count(p_tenant_id uuid)
RETURNS void AS $$
BEGIN
  UPDATE tenants
  SET monthly_posts_used = monthly_posts_used + 1,
      trial_posts_used = CASE
        WHEN plan_tier = 'free_trial' THEN trial_posts_used + 1
        ELSE trial_posts_used
      END
  WHERE id = p_tenant_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION decrement_video_credit(p_tenant_id uuid)
RETURNS void AS $$
BEGIN
  UPDATE tenants
  SET video_credits_remaining = GREATEST(video_credits_remaining - 1, 0),
      trial_videos_used = CASE
        WHEN plan_tier = 'free_trial' THEN trial_videos_used + 1
        ELSE trial_videos_used
      END
  WHERE id = p_tenant_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Atomic bonus credit consumption (use bonus first, then monthly)
CREATE OR REPLACE FUNCTION consume_post_credit(p_tenant_id uuid)
RETURNS text AS $$
DECLARE
  v_bonus integer;
BEGIN
  SELECT bonus_posts INTO v_bonus FROM tenants WHERE id = p_tenant_id FOR UPDATE;
  IF v_bonus > 0 THEN
    UPDATE tenants SET bonus_posts = bonus_posts - 1 WHERE id = p_tenant_id;
    RETURN 'bonus';
  ELSE
    UPDATE tenants
    SET monthly_posts_used = monthly_posts_used + 1,
        trial_posts_used = CASE
          WHEN plan_tier = 'free_trial' THEN trial_posts_used + 1
          ELSE trial_posts_used
        END
    WHERE id = p_tenant_id;
    RETURN 'monthly';
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Monthly reset function (resets all counters)
CREATE OR REPLACE FUNCTION reset_monthly_posts()
RETURNS void AS $$
BEGIN
  UPDATE tenants
  SET monthly_posts_used = 0,
      bonus_posts_purchased_this_month = 0,
      bonus_videos_purchased_this_month = 0,
      monthly_posts_reset_at = now()
  WHERE subscription_status IN ('active', 'past_due')
    AND (monthly_posts_reset_at IS NULL
         OR monthly_posts_reset_at < date_trunc('month', now()));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
