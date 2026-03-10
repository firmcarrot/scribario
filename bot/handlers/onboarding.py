"""Onboarding handler — /start command and new user registration."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.db import get_tenant_by_telegram_user

logger = logging.getLogger(__name__)

router = Router(name="onboarding")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start — welcome message and registration check."""
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
        await message.answer(
            f"Welcome to <b>Scribario</b>, {user.first_name}!\n\n"
            "I create and post social media content for your business.\n\n"
            "Just tell me what you want to post, like:\n"
            '<i>"Post about our new ghost pepper sauce launching Friday"</i>\n\n'
            "I'll generate images and captions, send you a preview, "
            "and post to your platforms when you approve.\n\n"
            "To get started, your account needs to be connected to a brand. "
            "Contact the Scribario team to set up your brand profile."
        )
