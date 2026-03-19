"""Autopilot weekly digest — sends summary to all autopilot-enabled tenants.

Runs every Sunday at 9am UTC via pg_cron.
"""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import get_settings
from bot.db import get_autopilot_weekly_summary, get_supabase_client

logger = logging.getLogger(__name__)


async def handle_autopilot_digest(message: dict) -> None:
    """Send weekly autopilot digest to all enabled tenants."""
    client = get_supabase_client()

    # Get all tenants with autopilot enabled (not off)
    configs_result = (
        client.table("autopilot_configs")
        .select("tenant_id")
        .neq("mode", "off")
        .execute()
    )
    configs = configs_result.data or []

    if not configs:
        logger.debug("No autopilot-enabled tenants for digest")
        return

    logger.info("Sending weekly digests", extra={"count": len(configs)})

    bot = Bot(
        token=get_settings().telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    try:
        for config in configs:
            tenant_id = config["tenant_id"]
            try:
                summary = await get_autopilot_weekly_summary(tenant_id)

                # Get tenant owner's chat_id
                member_result = (
                    client.table("tenant_members")
                    .select("telegram_user_id")
                    .eq("tenant_id", tenant_id)
                    .eq("role", "owner")
                    .limit(1)
                    .execute()
                )
                if not member_result.data:
                    continue

                chat_id = member_result.data[0]["telegram_user_id"]

                text = (
                    "📋 <b>Weekly Autopilot Report</b>\n\n"
                    f"Posts: {summary['total_topics']} created, "
                    f"{summary['posted']} published, "
                    f"{summary['rejected']} rejected\n"
                    f"Cost: ${summary['cost_usd']:.2f}\n"
                )

                if summary.get("failed", 0) > 0:
                    text += f"⚠️ Failed: {summary['failed']}\n"

                if summary["total_topics"] == 0:
                    text += "\nNo autopilot activity this week."

                await bot.send_message(chat_id=chat_id, text=text)

            except Exception:
                logger.exception(
                    "Failed to send digest to tenant",
                    extra={"tenant_id": tenant_id},
                )
    finally:
        await bot.session.close()
