"""Onboarding handler — /start command, /connect, /brand, and new user registration.

For new users, launches the aiogram_dialog onboarding flow.
For returning users, shows a welcome-back message.
"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram_dialog import DialogManager, StartMode

from bot.db import get_tenant_by_telegram_user
from bot.dialogs.states import OnboardingSG
from bot.services.postiz import get_oauth_url

logger = logging.getLogger(__name__)

router = Router(name="onboarding")


async def send_platform_buttons(bot: Bot, chat_id: int) -> None:
    """Send OAuth platform connection buttons to a chat.

    Uses bot.send_message (not callback.message.answer) to avoid
    InaccessibleMessage issues after dialog close.
    """
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

    async def fetch_url(platform_id: str, platform_name: str) -> tuple[str, str, str | None]:
        try:
            url = await get_oauth_url(platform_id)
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
        await bot.send_message(
            chat_id,
            "Social platform connections aren't configured yet. "
            "Please contact support.",
        )
        return

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_message(
        chat_id,
        "Tap a platform below to connect it to your account.\n\n"
        "Once connected, every post you approve will be published there automatically.",
        reply_markup=markup,
    )


@router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    """Handle /start — welcome returning users or launch onboarding dialog for new ones."""
    user = message.from_user
    if not user:
        return

    # Check if user already has a tenant
    membership = await get_tenant_by_telegram_user(user.id)

    if membership:
        # Check if onboarding is incomplete — relaunch dialog from welcome
        if membership.get("onboarding_status") != "complete":
            await dialog_manager.start(OnboardingSG.welcome, mode=StartMode.RESET_STACK)
            return

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

    await send_platform_buttons(message.bot, message.chat.id)


@router.message(Command("brand"))
async def cmd_brand(message: Message) -> None:
    """Handle /brand — show current brand profile (editing coming soon)."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer(
            "You're not connected to any brand yet.\nUse /start to set up your account."
        )
        return

    if membership.get("onboarding_status") != "complete":
        await message.answer(
            "You haven't finished setting up yet. Use /start to complete your profile."
        )
        return

    tenant_id = membership["tenant_id"]

    from pipeline.brand_voice import load_brand_profile

    profile = await load_brand_profile(tenant_id)
    if not profile:
        await message.answer(
            "No brand profile found. Use /start to set one up."
        )
        return

    tone = ", ".join(profile.tone_words) if profile.tone_words else "(not set)"
    do_items = "\n".join(f"  - {d}" for d in profile.do_list) if profile.do_list else "  (none)"
    dont_items = "\n".join(f"  - {d}" for d in profile.dont_list) if profile.dont_list else "  (none)"

    await message.answer(
        f"<b>Brand Profile: {profile.name}</b>\n\n"
        f"<b>Tone:</b> {tone}\n"
        f"<b>Audience:</b> {profile.audience_description}\n\n"
        f"<b>Do:</b>\n{do_items}\n\n"
        f"<b>Don't:</b>\n{dont_items}\n\n"
        "<i>Brand profile editing coming soon. For now, use /start to redo onboarding.</i>",
        parse_mode="HTML",
    )
