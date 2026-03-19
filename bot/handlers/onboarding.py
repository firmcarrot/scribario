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

logger = logging.getLogger(__name__)

router = Router(name="onboarding")


async def send_platform_buttons(bot: Bot, chat_id: int) -> None:
    """Send platform connection buttons that route through our OAuth proxy.

    Uses bot.send_message (not callback.message.answer) to avoid
    InaccessibleMessage issues after dialog close.
    """
    from bot.config import get_settings

    settings = get_settings()
    base_url = settings.connect_base_url

    platforms = [
        ("facebook", "\U0001f7e6 Facebook"),
        ("instagram", "\U0001f4f7 Instagram"),
        ("linkedin", "\U0001f4bc LinkedIn"),
        ("youtube", "\u25b6\ufe0f YouTube"),
        ("tiktok", "\U0001f3b5 TikTok"),
        ("twitter", "\U0001d54f X / Twitter"),
        ("pinterest", "\U0001f4cc Pinterest"),
        ("threads", "\U0001f9f5 Threads"),
        ("bluesky", "\U0001f98b Bluesky"),
    ]

    buttons = []
    for platform_id, platform_name in platforms:
        url = f"{base_url}/connect/{platform_id}?chat_id={chat_id}"
        buttons.append([InlineKeyboardButton(text=f"Connect {platform_name}", url=url)])

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
    logger.info("cmd_start: user=%s membership=%s", user.id, membership)

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
        logger.info("cmd_start: launching onboarding dialog for user=%s", user.id)
        await dialog_manager.start(OnboardingSG.welcome, mode=StartMode.RESET_STACK)
        logger.info("cmd_start: dialog started successfully")


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
    """Handle /brand — show current brand profile with edit buttons."""
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

    await _send_brand_profile(message, profile, tenant_id)


async def _send_brand_profile(
    target: Message, profile: object, tenant_id: str,
) -> None:
    """Send formatted brand profile with edit buttons."""
    tone = ", ".join(profile.tone_words) if profile.tone_words else "(not set)"
    audience = profile.audience_description or "(not set)"
    do_items = "\n".join(f"  • {d}" for d in profile.do_list) if profile.do_list else "  (none)"
    dont_items = "\n".join(f"  • {d}" for d in profile.dont_list) if profile.dont_list else "  (none)"

    text = (
        f"<b>Brand Profile: {profile.name}</b>\n\n"
        f"<b>Tone:</b> {tone}\n"
        f"<b>Audience:</b> {audience}\n\n"
        f"<b>Always do:</b>\n{do_items}\n\n"
        f"<b>Never do:</b>\n{dont_items}\n\n"
        "<i>Tap a button below to edit any field.</i>"
    )

    buttons = [
        [
            InlineKeyboardButton(text="✏️ Name", callback_data=f"brand_edit:name:{tenant_id}"),
            InlineKeyboardButton(text="✏️ Tone", callback_data=f"brand_edit:tone:{tenant_id}"),
        ],
        [
            InlineKeyboardButton(text="✏️ Audience", callback_data=f"brand_edit:audience:{tenant_id}"),
        ],
        [
            InlineKeyboardButton(text="✏️ Always Do", callback_data=f"brand_edit:dos:{tenant_id}"),
            InlineKeyboardButton(text="✏️ Never Do", callback_data=f"brand_edit:donts:{tenant_id}"),
        ],
    ]

    await target.answer(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
