"""Onboarding handler — /start command and new user registration.

For new users, launches the aiogram_dialog onboarding flow.
For returning users, shows a welcome-back message.
"""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram_dialog import DialogManager, StartMode

from bot.db import get_tenant_by_telegram_user
from bot.dialogs.states import OnboardingSG
from bot.services.postiz import get_oauth_url

logger = logging.getLogger(__name__)

router = Router(name="onboarding")


@router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    """Handle /start — welcome returning users or launch onboarding dialog for new ones."""
    user = message.from_user
    if not user:
        return

    # Check if user already has a tenant
    membership = await get_tenant_by_telegram_user(user.id)

    if membership:
        tenant_name = "your brand"
        tenants_data = membership.get("tenants")
        if isinstance(tenants_data, dict):
            tenant_name = tenants_data.get("name", tenant_name)

        await message.answer(
            f"Welcome back, {user.first_name}! "
            f"You're connected to <b>{tenant_name}</b>.\n\n"
            "Just send me a message about what you'd like to post, like:\n"
            '<i>"Post about our new ghost pepper sauce launching Friday"</i>'
        )
    else:
        # New user — launch the onboarding dialog
        await dialog_manager.start(OnboardingSG.welcome, mode=StartMode.RESET_STACK)


@router.message(Command("connect"))
async def cmd_connect(message: Message) -> None:
    """Handle /connect — show platform buttons, each opens OAuth directly."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer(
            "You're not connected to any brand yet.\nUse /start to set up your account."
        )
        return

    # Platforms currently configured in Postiz
    platforms = [
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("linkedin", "LinkedIn"),
        ("youtube", "YouTube"),
        ("tiktok", "TikTok"),
        ("twitter", "X / Twitter"),
        ("pinterest", "Pinterest"),
        ("threads", "Threads"),
        ("bluesky", "Bluesky"),
    ]

    # Fetch OAuth URLs for each platform concurrently
    import asyncio

    async def fetch_url(platform_id: str, platform_name: str) -> tuple[str, str, str | None]:
        try:
            url = await get_oauth_url(platform_id)
            # Only accept full valid URLs — some platforms return partial strings
            # when their credentials aren't configured yet
            if url and url.startswith("https://") and len(url) > 20:
                return platform_id, platform_name, url
            return platform_id, platform_name, None
        except Exception as e:
            logger.warning(f"OAuth URL unavailable for {platform_id}: {e}")
            return platform_id, platform_name, None

    results = await asyncio.gather(*[fetch_url(pid, pname) for pid, pname in platforms])

    buttons = []
    for _, pname, url in results:
        if url:
            buttons.append([InlineKeyboardButton(text=f"Connect {pname}", url=url)])

    if not buttons:
        await message.answer(
            "Social platform connections aren't configured yet. "
            "Please contact support."
        )
        return

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        "Tap a platform below to connect it to your account.\n\n"
        "Once connected, every post you approve will be published there automatically.",
        reply_markup=markup,
    )
