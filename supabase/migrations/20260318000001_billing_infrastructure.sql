-- Phase 1A: Billing Infrastructure on tenants
-- NOTE: Timestamp is placeholder — will be replaced with exact MCP timestamp after apply

-- Subscription state machine
CREATE TYPE subscription_status AS ENUM (
  'free_trial', 'active', 'past_due', 'paused', 'canceled'
);

CREATE TYPE plan_tier AS ENUM ('free_trial', 'starter', 'growth', 'pro');

ALTER TABLE tenants
  ADD COLUMN plan_tier plan_tier NOT NULL DEFAULT 'free_trial',
  ADD COLUMN subscription_status subscription_status NOT NULL DEFAULT 'free_trial',
  ADD COLUMN stripe_customer_id text UNIQUE,
  ADD COLUMN stripe_subscription_id text UNIQUE,
  ADD COLUMN trial_posts_used integer NOT NULL DEFAULT 0,
  ADD COLUMN trial_posts_limit integer NOT NULL DEFAULT 5,
  ADD COLUMN video_credits_remaining integer NOT NULL DEFAULT 0,
  ADD COLUMN monthly_post_limit integer NOT NULL DEFAULT 5,
  ADD COLUMN monthly_posts_used integer NOT NULL DEFAULT 0,
  ADD COLUMN monthly_posts_reset_at timestamptz,
  ADD COLUMN monthly_cost_hard_limit_usd numeric NOT NULL DEFAULT 2.00,
  ADD COLUMN billing_started_at timestamptz,
  ADD COLUMN canceled_at timestamptz;
