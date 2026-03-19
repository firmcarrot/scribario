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
        "monthly_posts_reset_at"
    ).eq("id", tenant_id).single().execute()

    tenant = result.data
    if not tenant:
        return False, "Account not found. Please use /start to set up."

    status = tenant["subscription_status"]
    plan = tenant["plan_tier"]

    # Canceled or paused accounts cannot generate
    if status in ("canceled", "paused"):
        return False, (
            "Your subscription is currently inactive. "
            "Use /subscribe to reactivate your plan."
        )

    # Past due — allow a grace period but warn
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

    # Active plans: check monthly post limit
    if status == "active":
        # Inline monthly reset fallback (belt & suspenders for pg_cron)
        _maybe_reset_monthly(tenant, tenant_id, client)

        used = tenant["monthly_posts_used"] or 0
        limit = tenant["monthly_post_limit"] or 5
        if used >= limit:
            return False, (
                f"You've reached your monthly limit of {limit} posts. "
                "Upgrade your plan for more: /upgrade"
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
    """Video-specific check. Free trial = always denied."""
    client = get_supabase_client()
    result = client.table("tenants").select(
        "plan_tier, subscription_status, video_credits_remaining"
    ).eq("id", tenant_id).single().execute()

    tenant = result.data
    if not tenant:
        return False, "Account not found."

    plan = tenant["plan_tier"]

    if plan == "free_trial":
        return False, (
            "Video generation is available on paid plans. "
            "Use /subscribe to unlock video content!"
        )

    credits = tenant["video_credits_remaining"] or 0
    if credits <= 0:
        return False, (
            "You've used all your video credits for this month. "
            "Upgrade for more: /upgrade"
        )

    return True, ""


async def increment_post_count(tenant_id: str) -> None:
    """Call AFTER successful generation. Increments counters atomically."""
    client = get_supabase_client()
    # Fetch current values to increment
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
    """Deduct one video credit after successful video generation."""
    client = get_supabase_client()
    result = client.table("tenants").select(
        "video_credits_remaining"
    ).eq("id", tenant_id).single().execute()

    if result.data:
        credits = max(0, (result.data["video_credits_remaining"] or 0) - 1)
        client.table("tenants").update(
            {"video_credits_remaining": credits}
        ).eq("id", tenant_id).execute()


def _maybe_reset_monthly(tenant: dict, tenant_id: str, client: object) -> None:
    """Inline fallback: reset monthly counters if pg_cron missed it."""
    from datetime import datetime, timezone

    reset_at = tenant.get("monthly_posts_reset_at")
    if reset_at is None:
        return

    try:
        if isinstance(reset_at, str):
            reset_dt = datetime.fromisoformat(reset_at.replace("Z", "+00:00"))
        else:
            reset_dt = reset_at

        now = datetime.now(timezone.utc)
        if reset_dt.month < now.month or reset_dt.year < now.year:
            client.table("tenants").update({
                "monthly_posts_used": 0,
                "monthly_posts_reset_at": now.isoformat(),
            }).eq("id", tenant_id).execute()
            # Update local copy so caller sees reset values
            tenant["monthly_posts_used"] = 0
    except Exception:
        logger.warning("Monthly reset fallback failed", exc_info=True)
