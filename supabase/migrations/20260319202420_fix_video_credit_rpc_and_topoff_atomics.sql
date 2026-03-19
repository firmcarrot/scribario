-- C3 FIX: decrement_video_credit now checks bonus_videos first
-- Must drop first because return type changed from void to text
DROP FUNCTION IF EXISTS decrement_video_credit(uuid);

CREATE FUNCTION decrement_video_credit(p_tenant_id uuid)
RETURNS text AS $$
DECLARE
  v_bonus integer;
BEGIN
  SELECT bonus_videos INTO v_bonus FROM tenants WHERE id = p_tenant_id FOR UPDATE;
  IF v_bonus > 0 THEN
    UPDATE tenants SET bonus_videos = bonus_videos - 1 WHERE id = p_tenant_id;
    RETURN 'bonus';
  ELSE
    UPDATE tenants
    SET video_credits_remaining = GREATEST(video_credits_remaining - 1, 0),
        trial_videos_used = CASE
          WHEN plan_tier = 'free_trial' THEN trial_videos_used + 1
          ELSE trial_videos_used
        END
    WHERE id = p_tenant_id;
    RETURN 'monthly';
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- C1 FIX: Atomic top-off credit application
CREATE OR REPLACE FUNCTION apply_topoff_credits(
  p_tenant_id uuid,
  p_bonus_posts integer DEFAULT 0,
  p_bonus_videos integer DEFAULT 0
)
RETURNS void AS $$
BEGIN
  UPDATE tenants
  SET bonus_posts = bonus_posts + p_bonus_posts,
      bonus_videos = bonus_videos + p_bonus_videos,
      bonus_posts_purchased_this_month = CASE
        WHEN p_bonus_posts > 0 THEN bonus_posts_purchased_this_month + 1
        ELSE bonus_posts_purchased_this_month
      END,
      bonus_videos_purchased_this_month = CASE
        WHEN p_bonus_videos > 0 THEN bonus_videos_purchased_this_month + 1
        ELSE bonus_videos_purchased_this_month
      END
  WHERE id = p_tenant_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- C2 FIX: Check top-off cap atomically
CREATE OR REPLACE FUNCTION check_topoff_cap(
  p_tenant_id uuid,
  p_topoff_type text  -- 'images' or 'videos'
)
RETURNS boolean AS $$
DECLARE
  v_count integer;
BEGIN
  IF p_topoff_type = 'images' THEN
    SELECT bonus_posts_purchased_this_month INTO v_count
    FROM tenants WHERE id = p_tenant_id;
  ELSE
    SELECT bonus_videos_purchased_this_month INTO v_count
    FROM tenants WHERE id = p_tenant_id;
  END IF;
  RETURN COALESCE(v_count, 0) < 3;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- I5: Drop unused increment_post_count (replaced by consume_post_credit)
DROP FUNCTION IF EXISTS increment_post_count(uuid);
