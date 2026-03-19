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
    # Split into two messages to stay under Telegram's 4096-char limit
    part1 = (
        "<b>Scribario — Complete Guide</b>\n\n"
        "Scribario turns a text message into a polished social media "
        "post — image, caption, and all — published automatically.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>📝 Creating Posts</b>\n"
        "Just type what you want to post in plain English:\n"
        '<i>"Post about our weekend shrimp special"</i>\n'
        '<i>"We just hit 500 orders — celebrate it"</i>\n'
        '<i>"Hiring a part-time kitchen assistant"</i>\n\n'
        "I'll generate 3 unique caption + image options in ~30 seconds. "
        "Pick the one you like.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>📅 Scheduling</b>\n"
        "Include a date/time and I'll queue it:\n"
        '<i>"Post this Friday at 9am"</i>\n'
        '<i>"Schedule for tomorrow at noon"</i>\n'
        "Uses your timezone (set with /timezone).\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>🎨 Style Control</b>\n"
        "Add style words to guide the image:\n"
        '<i>"Make it cinematic and moody"</i>\n'
        '<i>"Watercolor style, bright colors"</i>\n'
        "Styles: photorealistic, cinematic, cartoon, watercolor, "
        "illustrated, flat design, overhead, lifestyle\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>🎯 Platform Targeting</b>\n"
        "By default, posts go to all connected platforms. Narrow it:\n"
        '<i>"Post to Instagram only"</i>\n'
        '<i>"Facebook and LinkedIn"</i>\n\n'
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>🎬 Video Content</b>\n"
        "Include a video keyword and I'll create a short clip:\n"
        '<i>"Make a video reel about our new menu"</i>\n'
        '<i>"Animate something fun for National Donut Day"</i>\n'
        'Keywords: video, reel, clip, animate\n'
        '"Reel", "story", "tiktok", "shorts" → vertical (9:16)\n'
        "Video takes 1-3 minutes.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>📸 Reference Photos</b>\n"
        "Send a photo and the AI uses it as creative direction — "
        "matching style, lighting, and composition. Manage your photos "
        "with /photos.\n"
    )

    part2 = (
        "<b>✅ Preview Actions</b>\n"
        "When you see your 3 options:\n"
        "  <b>Approve #1/2/3</b> — publish that option immediately\n"
        "  <b>Edit</b> — revise the caption, then re-preview\n"
        "  <b>New Image</b> — keep the caption, regenerate just the photo\n"
        "  <b>Make Video</b> — turn an image preview into a video\n"
        "  <b>Reject All</b> — discard everything, nothing posts\n"
        "  <b>Regenerate</b> — get 3 completely new options\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>🤖 Autopilot</b>\n"
        "/autopilot — set up AI-powered auto-posting on a schedule\n"
        "Two modes:\n"
        "  <b>Smart Queue</b> — preview first, auto-posts in 2 hours\n"
        "  <b>Full Autopilot</b> — generates and posts, no approval\n"
        "/pause — stop autopilot immediately\n"
        "/resume — restart your schedule\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>💳 Billing</b>\n"
        "/subscribe — choose Starter ($29), Growth ($59), or Pro ($99)\n"
        "/upgrade — move to a higher plan (prorated)\n"
        "/topoff — buy extra credits when you need more\n"
        "/usage — see how many posts and videos you have left\n"
        "/billing — manage payment, view invoices, cancel\n\n"
        "Credits reset on your billing anniversary each month. "
        "Bonus credits from top-offs never expire.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>⚙️ Setup & Info</b>\n"
        "/start — begin onboarding + brand setup\n"
        "/connect — link Facebook, Instagram, and more\n"
        "/brand — view and edit your brand voice (name, tone, audience, dos/donts)\n"
        "/logo — upload or change your brand logo\n"
        "/photos — manage reference photos\n"
        "/library — browse unchosen options (post for free)\n"
        "/history — view your last 10 posted items\n"
        "/status — check recent request status\n"
        "/timezone — set your local timezone\n"
        "/help — this guide\n"
    )

    await message.answer(part1, parse_mode="HTML")
    await message.answer(part2, parse_mode="HTML")


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
