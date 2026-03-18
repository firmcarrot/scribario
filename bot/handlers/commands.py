"""Bot commands handler — /start is in onboarding.py; other commands here."""

from __future__ import annotations

import logging
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.db import get_recent_posts, get_supabase_client, get_tenant_by_telegram_user

router = Router(name="commands")

logger = logging.getLogger(__name__)


def _format_date(date_str: str) -> str:
    """Format an ISO date string to a short human-readable date."""
    if not date_str:
        return "unknown date"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return date_str[:10] if len(date_str) >= 10 else date_str


@router.message(Command("history"))
async def handle_history(message: Message) -> None:
    """Show recent posted content for the user's tenant."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer(
            "You're not set up yet! Send me a message to get started."
        )
        return

    tenant_id = membership["tenant_id"]
    posts = await get_recent_posts(tenant_id, limit=10)

    if not posts:
        await message.answer(
            "No posts yet! Send me a message to create your first post."
        )
        return

    lines: list[str] = ["📋 <b>Recent Posts</b>\n"]
    for i, post in enumerate(posts, 1):
        date_str = _format_date(post.get("posted_at", ""))
        platforms = post.get("platforms") or []
        platform_str = ", ".join(p.title() for p in platforms) if platforms else "Unknown"
        caption = post.get("caption_preview", "")

        lines.append(f'{i}. [{date_str}] → {platform_str}')
        if caption:
            lines.append(f'   "{caption}"')
        lines.append("")

    await message.answer("\n".join(lines).strip(), parse_mode="HTML")


@router.message(Command("timezone"))
async def handle_timezone(message: Message) -> None:
    """Show or update the user's timezone."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer("You're not set up yet! Use /start first.")
        return

    tenant_id = membership["tenant_id"]
    tenant_data = membership.get("tenants") or {}
    current_tz = tenant_data.get("timezone", "UTC") if isinstance(tenant_data, dict) else "UTC"

    # Check if user provided a new timezone
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) > 1:
        from bot.dialogs.onboarding import _resolve_timezone

        new_tz = _resolve_timezone(parts[1])
        if not new_tz:
            await message.answer(
                f"I didn't recognize that timezone. Your current timezone is <b>{current_tz}</b>.\n\n"
                "Try: Eastern, Central, Mountain, Pacific, UTC, GMT, Tokyo, Sydney, India\n"
                "Or an IANA name like America/New_York",
                parse_mode="HTML",
            )
            return

        try:
            client = get_supabase_client()
            client.table("tenants").update({"timezone": new_tz}).eq("id", tenant_id).execute()
        except Exception:
            logger.exception("Failed to update timezone for tenant %s", tenant_id)
            await message.answer("Something went wrong updating your timezone. Please try again.")
            return

        await message.answer(
            f"Timezone updated to <b>{new_tz}</b>.\n"
            "All scheduled posts will now use this timezone.",
            parse_mode="HTML",
        )
        return

    await message.answer(
        f"Your timezone is currently <b>{current_tz}</b>.\n\n"
        "To change it, type:\n"
        "<code>/timezone Eastern</code>\n"
        "<code>/timezone America/Los_Angeles</code>\n"
        "<code>/timezone UTC</code>",
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Show a comprehensive guide to all Scribario features."""
    await message.answer(
        "<b>Scribario — Quick Guide</b>\n\n"
        ""
        "<b>Creating Posts</b>\n"
        "Just type what you want to post:\n"
        '<i>"Post about our weekend special"</i>\n'
        '<i>"Announce we just hit 500 orders"</i>\n\n'
        ""
        "<b>Scheduling</b>\n"
        "Include a time and I'll queue it:\n"
        '<i>"Post this Friday at 3pm"</i>\n'
        '<i>"Schedule for tomorrow at noon"</i>\n\n'
        ""
        "<b>Style Control</b>\n"
        "Add style words to guide the image:\n"
        '<i>"Make it cinematic and moody"</i>\n'
        '<i>"Watercolor style, bright colors"</i>\n'
        "Styles: photorealistic, cinematic, cartoon, watercolor\n\n"
        ""
        "<b>Platform Targeting</b>\n"
        "Specify where to post:\n"
        '<i>"Post to Instagram only"</i>\n'
        '<i>"Facebook and Instagram"</i>\n\n'
        ""
        "<b>Video Content</b>\n"
        "Include video keywords:\n"
        '<i>"Make a video reel about our new menu"</i>\n'
        '<i>"Animate something for National Donut Day"</i>\n'
        "Keywords: video, reel, clip, animate\n\n"
        ""
        "<b>Reference Photos</b>\n"
        "Send a photo to use as creative direction.\n"
        "The AI will match the style, lighting, and composition.\n\n"
        ""
        "<b>After Preview</b>\n"
        "When you see your 3 options, you can:\n"
        "  Approve — post immediately\n"
        "  Edit — revise the caption\n"
        "  New Image — regenerate just the image\n"
        "  Reject All — discard everything\n"
        "  Regenerate — get 3 brand new options\n\n"
        ""
        "<b>Commands</b>\n"
        "/autopilot — set up automatic posting\n"
        "/history — see your last 10 posts\n"
        "/timezone — view or change your timezone\n"
        "/connect — add social platform accounts\n"
        "/brand — view your brand profile\n"
        "/help — show this guide\n",
        parse_mode="HTML",
    )


@router.message(Command("status"))
async def handle_status(message: Message) -> None:
    """Show the status of recent content requests."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer("You're not set up yet! Use /start first.")
        return

    tenant_id = membership["tenant_id"]

    try:
        client = get_supabase_client()
        result = (
            client.table("content_requests")
            .select("id, intent, status, created_at")
            .eq("tenant_id", tenant_id)
            .order("created_at", desc=True)
            .limit(5)
            .execute()
        )
    except Exception:
        logger.exception("Failed to fetch content request status")
        await message.answer("Something went wrong. Please try again.")
        return

    if not result.data:
        await message.answer("No content requests yet! Send me a message to create your first post.")
        return

    status_icons = {
        "pending": "⏳",
        "generating": "⚙️",
        "preview_ready": "👀",
        "approved": "✅",
        "posted": "📤",
        "rejected": "❌",
        "failed": "💥",
    }

    lines: list[str] = ["<b>Recent Requests</b>\n"]
    for req in result.data:
        icon = status_icons.get(req.get("status", ""), "❓")
        intent = (req.get("intent") or "")[:60]
        if len(req.get("intent", "")) > 60:
            intent += "..."
        date = _format_date(req.get("created_at", ""))
        status = req.get("status", "unknown")
        lines.append(f'{icon} <b>{status}</b> — {intent}')
        lines.append(f'   {date}')
        lines.append("")

    await message.answer("\n".join(lines).strip(), parse_mode="HTML")
