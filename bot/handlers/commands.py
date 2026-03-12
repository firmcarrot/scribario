"""Bot commands handler — /start is in onboarding.py; other commands here."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.db import get_recent_posts, get_tenant_by_telegram_user

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
