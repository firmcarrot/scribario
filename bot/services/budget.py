"""Budget enforcement service — pre-flight checks before any API call."""

from __future__ import annotations

import logging

from bot.db import get_supabase_client

logger = logging.getLogger(__name__)


async def check_can_generate(tenant_id: str) -> tuple[bool, str]:
    """Pre-flight check BEFORE any API call. Returns (allowed, reason)."""
    client = get_supabase_client()
    result = client.table("tenants").select(
        "plan_tier, subscription_status, trial_posts_used, trial_posts_limit, "
        "monthly_posts_used, monthly_post_limit, monthly_cost_hard_limit_usd, "
        "monthly_posts_reset_at, bonus_posts, current_period_end"
    ).eq("id", tenant_id).single().execute()

    tenant = result.data
    if not tenant:
        return False, "Account not found. Please use /start to set up."

    status = tenant["subscription_status"]
    plan = tenant["plan_tier"]

    # Canceled accounts: allow until current_period_end
    if status == "canceled":
        from datetime import datetime, timezone

        period_end = tenant.get("current_period_end")
        if period_end:
            try:
                if isinstance(period_end, str):
                    end_dt = datetime.fromisoformat(period_end.replace("Z", "+00:00"))
                else:
                    end_dt = period_end
                if datetime.now(timezone.utc) < end_dt:
                    # Still within billing period — check limits below
                    pass
                else:
                    return False, (
                        "Your subscription has expired. "
                        "Use /subscribe to reactivate your plan."
                    )
            except Exception:
                return False, (
                    "Your subscription is inactive. "
                    "Use /subscribe to reactivate."
                )
        else:
            return False, (
                "Your subscription is inactive. "
                "Use /subscribe to reactivate your plan."
            )

    if status == "paused":
        return False, (
            "Your subscription is paused. "
            "Use /billing to resume your plan."
        )

    # Past due — block with payment update prompt
    if status == "past_due":
        return False, (
            "Your payment is past due. Please update your payment method "
            "via /billing to continue creating content."
        )

    # Free trial: check trial post limit
    if plan == "free_trial":
        used = tenant["trial_posts_used"] or 0
        limit = tenant["trial_posts_limit"] or 5
        if used >= limit:
            return False, (
                f"You've used all {limit} free posts! Here's what you created:\n"
                f"• {used} posts generated\n\n"
                "Your content is saved — nothing gets deleted.\n\n"
                "To keep creating: /subscribe"
            )

    # Active/canceled-but-in-period: check monthly post limit + bonus
    if status in ("active", "canceled"):
        # Inline monthly reset fallback (belt & suspenders for invoice.paid webhook)
        _maybe_reset_monthly(tenant, tenant_id, client)

        used = tenant["monthly_posts_used"] or 0
        limit = tenant["monthly_post_limit"] or 5
        bonus = tenant.get("bonus_posts") or 0
        total_available = limit + bonus

        if used >= total_available:
            return False, (
                f"You've reached your limit of {limit} posts this month"
                + (f" (plus {bonus} bonus)" if bonus else "")
                + ".\nNeed more? /topoff or /upgrade"
            )

    # Check monthly cost hard limit
    try:
        spend_result = client.rpc(
            "get_tenant_monthly_spend", {"p_tenant_id": tenant_id}
        ).execute()
        if spend_result.data:
            row = spend_result.data[0] if isinstance(spend_result.data, list) else spend_result.data
            total_cost = float(row.get("total_cost_usd", 0))
            hard_limit = float(tenant["monthly_cost_hard_limit_usd"] or 2.0)
            if total_cost >= hard_limit:
                return False, (
                    "Monthly cost limit reached. This protects your account "
                    "from unexpected charges. Contact support or upgrade: /upgrade"
                )
    except Exception:
        logger.warning("Failed to check monthly spend", exc_info=True)

    return True, ""


async def check_can_generate_video(tenant_id: str) -> tuple[bool, str]:
    """Video-specific check. Free trial gets 1 video."""
    client = get_supabase_client()
    result = client.table("tenants").select(
        "plan_tier, subscription_status, video_credits_remaining, "
        "trial_videos_used, trial_video_limit, bonus_videos, current_period_end"
    ).eq("id", tenant_id).single().execute()

    tenant = result.data
    if not tenant:
        return False, "Account not found."

    plan = tenant["plan_tier"]
    status = tenant["subscription_status"]

    # Free trial: check trial video limit
    if plan == "free_trial":
        used = tenant.get("trial_videos_used") or 0
        limit = tenant.get("trial_video_limit") or 1
        if used >= limit:
            return False, (
                f"You've used your {limit} free video! "
                "Use /subscribe to unlock more video content."
            )
        return True, ""

    # Canceled — check period end
    if status == "canceled":
        from datetime import datetime, timezone

        period_end_str = tenant.get("current_period_end")

        if period_end_str:
            try:
                end_dt = datetime.fromisoformat(period_end_str.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) >= end_dt:
                    return False, "Your subscription has expired. /subscribe to reactivate."
            except Exception:
                return False, "Your subscription is inactive."
        else:
            return False, "Your subscription is inactive. /subscribe to reactivate."

    credits = tenant["video_credits_remaining"] or 0
    bonus = tenant.get("bonus_videos") or 0
    total = credits + bonus

    if total <= 0:
        return False, (
            "You've used all your video credits for this month. "
            "Need more? /topoff or /upgrade"
        )

    return True, ""


async def increment_post_count(tenant_id: str) -> None:
    """Call AFTER successful generation. Uses atomic RPC."""
    client = get_supabase_client()
    try:
        # Use atomic RPC that handles bonus vs monthly logic
        client.rpc("consume_post_credit", {"p_tenant_id": tenant_id}).execute()
    except Exception:
        logger.warning("consume_post_credit RPC failed, falling back", exc_info=True)
        # Fallback to direct update
        result = client.table("tenants").select(
            "plan_tier, trial_posts_used, monthly_posts_used"
        ).eq("id", tenant_id).single().execute()

        tenant = result.data
        if not tenant:
            return

        updates: dict = {
            "monthly_posts_used": (tenant["monthly_posts_used"] or 0) + 1,
        }
        if tenant["plan_tier"] == "free_trial":
            updates["trial_posts_used"] = (tenant["trial_posts_used"] or 0) + 1

        client.table("tenants").update(updates).eq("id", tenant_id).execute()


async def decrement_video_credit(tenant_id: str) -> None:
    """Deduct one video credit after successful video generation. Uses atomic RPC."""
    client = get_supabase_client()
    try:
        client.rpc("decrement_video_credit", {"p_tenant_id": tenant_id}).execute()
    except Exception:
        logger.warning("decrement_video_credit RPC failed, falling back", exc_info=True)
        result = client.table("tenants").select(
            "plan_tier, video_credits_remaining, bonus_videos"
        ).eq("id", tenant_id).single().execute()

        if not result.data:
            return

        t = result.data
        bonus = t.get("bonus_videos") or 0
        credits = t["video_credits_remaining"] or 0

        if bonus > 0:
            client.table("tenants").update(
                {"bonus_videos": bonus - 1}
            ).eq("id", tenant_id).execute()
        elif credits > 0:
            client.table("tenants").update(
                {"video_credits_remaining": credits - 1}
            ).eq("id", tenant_id).execute()


async def get_usage_warning(tenant_id: str) -> str | None:
    """Check if user is at 80%+ usage. Returns warning message or None."""
    client = get_supabase_client()
    result = client.table("tenants").select(
        "plan_tier, monthly_posts_used, monthly_post_limit, "
        "trial_posts_used, trial_posts_limit, bonus_posts, "
        "video_credits_remaining, bonus_videos"
    ).eq("id", tenant_id).single().execute()

    if not result.data:
        return None

    t = result.data
    plan = t["plan_tier"]

    if plan == "free_trial":
        used = t["trial_posts_used"] or 0
        limit = t["trial_posts_limit"] or 5
        if limit > 0 and used / limit >= 0.8 and used < limit:
            remaining = limit - used
            return (
                f"\n\n<i>Heads up — you have {remaining} free post(s) left. "
                f"/subscribe to keep creating!</i>"
            )
    else:
        used = t["monthly_posts_used"] or 0
        limit = t["monthly_post_limit"] or 0
        bonus = t.get("bonus_posts") or 0
        total = limit + bonus
        if total > 0 and used / total >= 0.8 and used < total:
            remaining = total - used
            return (
                f"\n\n<i>Heads up — {remaining} post(s) left this month. "
                f"/topoff for more or /upgrade for a bigger plan!</i>"
            )

        videos = (t["video_credits_remaining"] or 0) + (t.get("bonus_videos") or 0)
        if videos == 1:
            return "\n\n<i>Last video credit! /topoff for more.</i>"

    return None


def _maybe_reset_monthly(tenant: dict, tenant_id: str, client: object) -> None:
    """Inline fallback: reset monthly counters if invoice.paid webhook missed it.

    Uses current_period_end to determine if the billing cycle rolled over.
    Each tenant resets on THEIR billing anniversary, not a calendar date.
    """
    from datetime import datetime, timezone

    period_end = tenant.get("current_period_end")
    if period_end is None:
        return

    try:
        if isinstance(period_end, str):
            end_dt = datetime.fromisoformat(period_end.replace("Z", "+00:00"))
        else:
            end_dt = period_end

        now = datetime.now(timezone.utc)
        if now >= end_dt:
            # Billing period has ended but webhook hasn't reset counters yet
            # Resolve video credits from tier limits
            tier = tenant.get("plan_tier", "")
            tier_video_credits = {
                "starter": 5, "growth": 15, "pro": 40,
            }.get(tier, 0)

            update_data = {
                "monthly_posts_used": 0,
                "bonus_posts_purchased_this_month": 0,
                "bonus_videos_purchased_this_month": 0,
                "monthly_posts_reset_at": now.isoformat(),
            }
            if tier_video_credits > 0:
                update_data["video_credits_remaining"] = tier_video_credits

            client.table("tenants").update(update_data).eq(
                "id", tenant_id
            ).execute()
            # Update local copy so caller sees reset values
            tenant["monthly_posts_used"] = 0
            if tier_video_credits > 0:
                tenant["video_credits_remaining"] = tier_video_credits
    except Exception:
        logger.warning("Monthly reset fallback failed", exc_info=True)
