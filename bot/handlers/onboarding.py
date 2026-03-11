"""Onboarding handler — /start command and new user registration.

For new users, launches the aiogram_dialog onboarding flow.
For returning users, shows a welcome-back message.
"""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from bot.db import get_tenant_by_telegram_user
from bot.dialogs.states import OnboardingSG

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
