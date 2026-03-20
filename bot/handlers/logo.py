"""Logo upload handler — /logo command + photo capture flow."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import get_settings
from bot.db import get_tenant_by_telegram_user
from bot.services.storage import download_and_store

logger = logging.getLogger(__name__)

router = Router(name="logo")

# Tracks users who have issued /logo and are waiting to send a photo.
# {telegram_user_id: tenant_id}
# NOTE: In-memory — same pattern as _pending_post_photos in photos.py.
# Acceptable because the window is small (user sends photo within seconds).
_pending_logo_uploads: dict[int, str] = {}


async def _update_logo_path(tenant_id: str, storage_path: str) -> None:
    """Update brand_profiles.logo_storage_path for a tenant."""
    from bot.db import get_supabase_client

    client = get_supabase_client()
    client.table("brand_profiles").update(
        {"logo_storage_path": storage_path}
    ).eq("tenant_id", tenant_id).execute()


async def save_logo_from_telegram(
    bot_token: str,
    file_id: str,
    file_unique_id: str,
    tenant_id: str,
) -> str:
    """Download a Telegram photo/document and save as tenant logo.

    Shared utility used by both /logo command and onboarding flow.

    Returns:
        The storage path of the saved logo.
    """
    from aiogram import Bot

    bot = Bot(token=bot_token)
    try:
        file = await bot.get_file(file_id)
        download_url = f"https://api.telegram.org/file/bot{bot_token}/{file.file_path}"

        storage_path = await download_and_store(
            download_url=download_url,
            tenant_id=tenant_id,
            file_unique_id=f"logo_{file_unique_id}",
        )

        await _update_logo_path(tenant_id, storage_path)
        logger.info("Logo saved", extra={"tenant_id": tenant_id, "path": storage_path})
        return storage_path
    finally:
        await bot.session.close()


@router.message(Command("logo"))
async def cmd_logo(message: Message) -> None:
    """Handle /logo command — prompt user to send their logo image."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer(
            "You're not connected to any brand yet.\n"
            "Use /start to set up your account."
        )
        return

    tenant_id = membership["tenant_id"]
    _pending_logo_uploads[user.id] = tenant_id

    await message.answer(
        "Send me your logo as a photo and I'll save it.\n"
        "It'll be creatively integrated into your generated images — "
        "think latte art, laptop stickers, signs in the background."
    )


@router.message(F.photo)
async def handle_logo_photo(message: Message) -> None:
    """Capture a logo photo from a user who ran /logo."""
    user = message.from_user
    if not user or user.id not in _pending_logo_uploads:
        return

    tenant_id = _pending_logo_uploads.pop(user.id)

    # Get largest photo (last in array)
    photo = message.photo[-1]

    try:
        await save_logo_from_telegram(
            bot_token=get_settings().telegram_bot_token,
            file_id=photo.file_id,
            file_unique_id=photo.file_unique_id,
            tenant_id=tenant_id,
        )
        await message.answer(
            "Your logo has been saved! It'll be creatively woven into your content."
        )

    except Exception:
        logger.exception("Failed to save logo", extra={"tenant_id": tenant_id})
        await message.answer("Something went wrong saving your logo. Please try again.")
