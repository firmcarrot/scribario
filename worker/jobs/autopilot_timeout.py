"""Autopilot timeout sweep — auto-approve Smart Queue topics past their deadline.

Runs every 5 minutes via pg_cron. Uses atomic conditional updates (DA CRIT-2)
to prevent race conditions with manual user actions.
"""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import get_settings
from bot.db import (
    get_draft,
    get_expired_smart_queue_topics,
    get_supabase_client,
    update_autopilot_topic_status,
)
from bot.handlers.approval import approve_draft, approve_video_draft

logger = logging.getLogger(__name__)


async def _send_auto_post_notification(tenant_id: str, caption_preview: str) -> None:
    """Notify tenant that autopilot auto-posted content."""
    try:
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
        preview = caption_preview[:100] + "..." if len(caption_preview) > 100 else caption_preview

        bot = Bot(
            token=get_settings().telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=f"✅ <b>Autopilot auto-posted:</b>\n{preview}",
            )
        finally:
            await bot.session.close()
    except Exception:
        logger.exception("Failed to send auto-post notification", extra={"tenant_id": tenant_id})


async def handle_autopilot_timeout(message: dict) -> None:
    """Process expired Smart Queue topics — auto-approve if not rejected."""
    expired = await get_expired_smart_queue_topics()

    if not expired:
        logger.debug("No expired Smart Queue topics")
        return

    logger.info("Processing expired Smart Queue topics", extra={"count": len(expired)})

    for topic in expired:
        topic_id = topic["id"]
        draft_id = topic.get("draft_id")
        tenant_id = topic["tenant_id"]

        if not draft_id:
            logger.warning("Expired topic has no draft_id", extra={"topic_id": topic_id})
            await update_autopilot_topic_status(topic_id, "failed", expected_status="previewing")
            continue

        # Atomic conditional update (DA CRIT-2): claim the topic for auto-approval
        # Use intermediate status to avoid marking "posted" before approval succeeds
        claimed = await update_autopilot_topic_status(
            topic_id, "generating", expected_status="previewing"
        )

        if not claimed:
            # User already rejected or handled — skip
            logger.info("Topic already handled, skipping", extra={"topic_id": topic_id})
            continue

        # Auto-approve the draft
        try:
            draft = await get_draft(draft_id)
            if not draft:
                logger.warning("Draft not found for auto-approve", extra={"draft_id": draft_id})
                await update_autopilot_topic_status(topic_id, "failed", expected_status="generating")
                continue

            caption_preview = ""
            variants = draft.get("caption_variants", [])
            if variants:
                caption_preview = variants[0].get("text", "")

            if draft.get("video_url"):
                await approve_video_draft(draft_id, option_idx=0, tenant_id=tenant_id)
            else:
                await approve_draft(draft_id, option_idx=0, tenant_id=tenant_id)

            # Only mark "posted" after successful approval
            await update_autopilot_topic_status(topic_id, "posted", expected_status="generating")
            await _send_auto_post_notification(tenant_id, caption_preview)

            logger.info("Auto-approved expired topic", extra={"topic_id": topic_id, "draft_id": draft_id})

        except Exception:
            logger.exception("Failed to auto-approve topic", extra={"topic_id": topic_id})
            await update_autopilot_topic_status(topic_id, "failed", expected_status="generating")
