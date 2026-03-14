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
        "It'll appear as a watermark on your generated content."
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
        # Get Telegram file URL (same pattern as photos.py:_download_photo)
        file = await message.bot.get_file(photo.file_id)
        token = get_settings().telegram_bot_token
        download_url = f"https://api.telegram.org/file/bot{token}/{file.file_path}"

        storage_path = await download_and_store(
            download_url=download_url,
            tenant_id=tenant_id,
            file_unique_id=f"logo_{photo.file_unique_id}",
        )

        await _update_logo_path(tenant_id, storage_path)

        await message.answer("Your logo has been saved! It'll be used in your content.")
        logger.info("Logo saved", extra={"tenant_id": tenant_id, "path": storage_path})

    except Exception:
        logger.exception("Failed to save logo", extra={"tenant_id": tenant_id})
        await message.answer("Something went wrong saving your logo. Please try again.")
