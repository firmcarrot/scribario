"""Autopilot generate — per-tenant content generation with guardrails.

Checks limits, generates a topic, creates content request, enqueues generation.
Handles failure tracking and auto-pause (DA HIGH-4).
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from bot.config import get_settings
from bot.db import (
    count_tenant_posts_today,
    count_tenant_posts_this_week,
    create_autopilot_run,
    create_autopilot_topic,
    create_content_request,
    enqueue_job,
    get_autopilot_config,
    get_supabase_client,
    get_tenant_monthly_cost,
    log_usage_event,
    pause_autopilot,
    update_autopilot_run,
    update_autopilot_topic_status,
)
from pipeline.cost_utils import compute_anthropic_cost
from pipeline.topic_engine import MODERATION_COST_USD, TOPIC_GEN_COST_USD, generate_topic, moderate_content

logger = logging.getLogger(__name__)

def _get_hard_ceilings() -> tuple[int, float]:
    """Get hard ceiling values from settings (DA HIGH-2: cost runaway protection)."""
    s = get_settings()
    return s.autopilot_max_daily_posts, s.autopilot_max_monthly_cost_usd


async def _get_recent_topics(tenant_id: str, days: int = 14) -> list[str]:
    """Get recent topic strings for dedup."""
    client = get_supabase_client()
    cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
    result = (
        client.table("autopilot_topics")
        .select("topic")
        .eq("tenant_id", tenant_id)
        .gte("created_at", cutoff)
        .execute()
    )
    return [r["topic"] for r in (result.data or [])]


async def _get_brand_profile_dict(tenant_id: str) -> dict:
    """Load brand profile as a plain dict for topic engine."""
    client = get_supabase_client()
    result = (
        client.table("brand_profiles")
        .select("*, tenants(name)")
        .eq("tenant_id", tenant_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        return {"name": "Brand", "tone_words": ["professional"], "audience_description": "general"}
    row = result.data[0]
    tenants_data = row.get("tenants")
    name = tenants_data.get("name", "Brand") if isinstance(tenants_data, dict) else "Brand"
    return {
        "name": name,
        "tone_words": row.get("tone_words", []),
        "audience_description": row.get("audience_description", ""),
        "product_catalog": row.get("product_catalog"),
    }


async def _notify_tenant(tenant_id: str, text: str) -> None:
    """Send a Telegram notification to the tenant owner."""
    try:
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode

        client = get_supabase_client()
        result = (
            client.table("tenant_members")
            .select("telegram_user_id")
            .eq("tenant_id", tenant_id)
            .eq("role", "owner")
            .limit(1)
            .execute()
        )
        if not result.data:
            return

        chat_id = result.data[0]["telegram_user_id"]
        bot = Bot(
            token=get_settings().telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        try:
            await bot.send_message(chat_id=chat_id, text=text)
        finally:
            await bot.session.close()
    except Exception:
        logger.exception("Failed to send tenant notification", extra={"tenant_id": tenant_id})


async def _increment_failures(tenant_id: str) -> None:
    """Increment consecutive_failures. Auto-pause at 3 (DA HIGH-4)."""
    client = get_supabase_client()
    config_result = (
        client.table("autopilot_configs")
        .select("consecutive_failures")
        .eq("tenant_id", tenant_id)
        .limit(1)
        .execute()
    )
    if not config_result.data:
        return

    failures = (config_result.data[0].get("consecutive_failures") or 0) + 1
    update_data: dict = {
        "consecutive_failures": failures,
        "updated_at": datetime.now(UTC).isoformat(),
    }

    if failures >= 3:
        update_data["paused_at"] = datetime.now(UTC).isoformat()
        await _notify_tenant(
            tenant_id,
            "⚠️ <b>Autopilot paused</b> — 3 consecutive failures detected. "
            "Use /resume to restart after investigating.",
        )
        logger.warning("Auto-paused autopilot after 3 failures", extra={"tenant_id": tenant_id})

    client.table("autopilot_configs").update(update_data).eq("tenant_id", tenant_id).execute()


async def _reset_failures(tenant_id: str) -> None:
    """Reset consecutive_failures to 0 on success."""
    client = get_supabase_client()
    (
        client.table("autopilot_configs")
        .update({"consecutive_failures": 0, "updated_at": datetime.now(UTC).isoformat()})
        .eq("tenant_id", tenant_id)
        .execute()
    )


async def handle_autopilot_generate(message: dict) -> None:
    """Generate content for one tenant's autopilot run."""
    tenant_id = message["tenant_id"]

    # 1. Load config — abort if off/paused
    config = await get_autopilot_config(tenant_id)
    if not config:
        logger.warning("No autopilot config found", extra={"tenant_id": tenant_id})
        return

    if config.get("mode") == "off" or config.get("paused_at"):
        logger.info("Autopilot off or paused, skipping", extra={"tenant_id": tenant_id})
        return

    # 2. Check guardrails
    max_daily, max_monthly_cost = _get_hard_ceilings()
    daily_count = await count_tenant_posts_today(tenant_id)
    daily_limit = min(config.get("daily_post_limit", 3), max_daily)
    if daily_count >= daily_limit:
        logger.info("Daily post limit reached", extra={"tenant_id": tenant_id, "count": daily_count})
        return

    weekly_count = await count_tenant_posts_this_week(tenant_id)
    weekly_limit = config.get("weekly_post_limit", 15)
    if weekly_count >= weekly_limit:
        logger.info("Weekly post limit reached", extra={"tenant_id": tenant_id, "count": weekly_count})
        return

    monthly_cost = await get_tenant_monthly_cost(tenant_id)
    cost_cap = min(config.get("monthly_cost_cap_usd", 50.0) or 50.0, max_monthly_cost)
    if monthly_cost >= cost_cap:
        logger.info("Monthly cost cap reached", extra={"tenant_id": tenant_id, "cost": monthly_cost})
        return

    # 3. Generate topic (sequential — one at a time per DA HIGH-2)
    content_mix = config.get("content_mix") or {"promotional": 100}
    brand_profile = await _get_brand_profile_dict(tenant_id)
    recent_topics = await _get_recent_topics(tenant_id)

    run = await create_autopilot_run(tenant_id=tenant_id)

    try:
        topic_result = await generate_topic(
            tenant_id=tenant_id,
            content_mix=content_mix,
            brand_profile=brand_profile,
            recent_topics=recent_topics,
        )

        t_in = topic_result.get("input_tokens") or 0
        t_out = topic_result.get("output_tokens") or 0
        if t_in and t_out:
            topic_cost = compute_anthropic_cost("claude-haiku-4-5-20251001", t_in, t_out)
        else:
            topic_cost = TOPIC_GEN_COST_USD  # fallback

        await log_usage_event(
            tenant_id=tenant_id,
            event_type="autopilot_topic_gen",
            provider="anthropic",
            cost_usd=topic_cost,
            input_tokens=t_in or None,
            output_tokens=t_out or None,
            model="claude-haiku-4-5-20251001",
            metadata={"topic": topic_result["topic"], "category": topic_result["category"]},
        )

        # 4. For Full Autopilot (post-warmup): moderate content (DA HIGH-3)
        is_full_auto = config.get("mode") == "full_autopilot"
        warmup_remaining = config.get("warmup_posts_remaining", 5)

        if is_full_auto and warmup_remaining <= 0:
            mod_result = await moderate_content(topic_result["topic"])

            # Log moderation cost
            mod_in = mod_result.get("input_tokens") or 0
            mod_out = mod_result.get("output_tokens") or 0
            if mod_in and mod_out:
                mod_cost = compute_anthropic_cost("claude-haiku-4-5-20251001", mod_in, mod_out)
            else:
                mod_cost = MODERATION_COST_USD  # fallback
            try:
                await log_usage_event(
                    tenant_id=tenant_id,
                    event_type="content_moderation",
                    provider="anthropic",
                    cost_usd=mod_cost,
                    input_tokens=mod_in or None,
                    output_tokens=mod_out or None,
                    model="claude-haiku-4-5-20251001",
                )
            except Exception:
                logger.exception("Failed to log moderation cost")

            if not mod_result.get("safe", True):
                logger.warning(
                    "Topic failed moderation",
                    extra={"tenant_id": tenant_id, "reason": mod_result.get("reason")},
                )
                await update_autopilot_run(
                    run["id"],
                    error_message=f"Topic failed moderation: {mod_result.get('reason', '')}",
                )
                return

        # 5. Create autopilot_topics row
        use_smart_queue = (
            not is_full_auto
            or warmup_remaining > 0  # Warmup = always Smart Queue (DA HIGH-3)
        )

        auto_approve_at = None
        if use_smart_queue:
            timeout_minutes = config.get("smart_queue_timeout_minutes", 120)
            auto_approve_at = datetime.now(UTC) + timedelta(minutes=timeout_minutes)

        topic_row = await create_autopilot_topic(
            tenant_id=tenant_id,
            topic=topic_result["topic"],
            category=topic_result["category"],
            auto_approve_at=auto_approve_at,
        )

        # 6. Create content_request with source='autopilot'
        platform_targets = config.get("platform_targets") or []
        content_req = await create_content_request(
            tenant_id=tenant_id,
            intent=topic_result["topic"],
            platform_targets=platform_targets if platform_targets else None,
        )

        # Update topic with content_request_id
        client = get_supabase_client()
        client.table("autopilot_topics").update({
            "content_request_id": content_req["id"],
            "status": "generating",
        }).eq("id", topic_row["id"]).execute()

        # 7. Get chat_id for Telegram preview
        member_result = (
            client.table("tenant_members")
            .select("telegram_user_id")
            .eq("tenant_id", tenant_id)
            .eq("role", "owner")
            .limit(1)
            .execute()
        )
        chat_id = member_result.data[0]["telegram_user_id"] if member_result.data else None

        # 8. Enqueue standard generate_content job with autopilot metadata
        await enqueue_job(
            queue_name="content_generation",
            job_type="generate_content",
            payload={
                "request_id": content_req["id"],
                "tenant_id": tenant_id,
                "intent": topic_result["topic"],
                "platform_targets": platform_targets if platform_targets else None,
                "telegram_chat_id": chat_id,
                "source": "autopilot",
                "autopilot_topic_id": topic_row["id"],
                "autopilot_mode": config.get("mode"),
                "auto_approve_at": auto_approve_at.isoformat() if auto_approve_at else None,
                "warmup_posts_remaining": warmup_remaining,
            },
        )

        # Decrement warmup counter if applicable
        if warmup_remaining > 0:
            client.table("autopilot_configs").update({
                "warmup_posts_remaining": warmup_remaining - 1,
                "updated_at": datetime.now(UTC).isoformat(),
            }).eq("tenant_id", tenant_id).execute()

        await update_autopilot_run(
            run["id"],
            topics_generated=1,
            cost_usd=float(topic_cost),
        )

        await _reset_failures(tenant_id)

    except Exception as exc:
        logger.exception("Autopilot generation failed", extra={"tenant_id": tenant_id})
        await _increment_failures(tenant_id)
        await update_autopilot_run(run["id"], error_message=str(exc))
        raise
