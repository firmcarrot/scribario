"""Logo upload handler — /logo command + photo capture flow."""

from __future__ import annotations

import logging
import time

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import get_settings
from bot.db import get_tenant_by_telegram_user
from bot.services.storage import download_and_store

logger = logging.getLogger(__name__)

router = Router(name="logo")

# Tracks users who have issued /logo and are waiting to send a photo.
# {telegram_user_id: (tenant_id, timestamp)}
# Entries expire after PENDING_TTL_SECONDS.
_pending_logo_uploads: dict[int, tuple[str, float]] = {}
PENDING_TTL_SECONDS = 300  # 5 minutes

# Allowed MIME types for document uploads (logo files)
_ALLOWED_LOGO_MIMES = {"image/png", "image/jpeg", "image/webp", "image/svg+xml"}


def _get_pending(user_id: int) -> str | None:
    """Get tenant_id for a pending logo upload, respecting TTL."""
    entry = _pending_logo_uploads.get(user_id)
    if entry is None:
        return None
    tenant_id, timestamp = entry
    if time.monotonic() - timestamp > PENDING_TTL_SECONDS:
        _pending_logo_uploads.pop(user_id, None)
        return None
    return tenant_id


def _set_pending(user_id: int, tenant_id: str) -> None:
    """Register a pending logo upload with timestamp."""
    _pending_logo_uploads[user_id] = (tenant_id, time.monotonic())


async def _update_logo_path(
    tenant_id: str,
    storage_path: str,
    width: int | None = None,
    height: int | None = None,
    format_hint: str | None = None,
) -> None:
    """Update brand_profiles logo fields for a tenant."""
    from bot.db import get_supabase_client

    data: dict = {"logo_storage_path": storage_path}
    if width and height:
        # Store aspect hint: "square", "horizontal", or "vertical"
        ratio = width / height
        if ratio > 1.3:
            data["logo_shape"] = "horizontal"
        elif ratio < 0.77:
            data["logo_shape"] = "vertical"
        else:
            data["logo_shape"] = "square"
    if format_hint:
        data["logo_format"] = format_hint

    client = get_supabase_client()
    client.table("brand_profiles").update(data).eq("tenant_id", tenant_id).execute()


async def save_logo_from_telegram(
    bot: Bot,
    file_id: str,
    file_unique_id: str,
    tenant_id: str,
) -> str:
    """Download a Telegram photo/document and save as tenant logo.

    Shared utility used by both /logo command and onboarding flow.
    Preserves PNG transparency for logos.

    Args:
        bot: Existing aiogram Bot instance (avoids creating a new session).
        file_id: Telegram file ID.
        file_unique_id: Telegram file unique ID.
        tenant_id: Tenant UUID.

    Returns:
        The storage path of the saved logo.
    """
    file = await bot.get_file(file_id)
    token = bot.token
    download_url = f"https://api.telegram.org/file/bot{token}/{file.file_path}"

    storage_path = await download_and_store(
        download_url=download_url,
        tenant_id=tenant_id,
        file_unique_id=f"logo_{file_unique_id}",
        preserve_alpha=True,
    )

    # Extract dimensions for shape metadata
    width: int | None = None
    height: int | None = None
    format_hint: str | None = None
    try:
        import io
        from PIL import Image
        from bot.services.storage import get_signed_url
        import httpx

        signed = get_signed_url(storage_path)
        async with httpx.AsyncClient(timeout=10.0) as http:
            resp = await http.get(signed)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content))
                width, height = img.size
                format_hint = "png" if storage_path.endswith(".png") else "jpeg"
    except Exception:
        logger.debug("Could not extract logo dimensions", exc_info=True)

    await _update_logo_path(tenant_id, storage_path, width, height, format_hint)
    logger.info("Logo saved", extra={"tenant_id": tenant_id, "path": storage_path})
    return storage_path


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
    _set_pending(user.id, tenant_id)

    await message.answer(
        "Send me your logo as a photo and I'll save it.\n"
        "It'll be creatively integrated into your generated images — "
        "think latte art, laptop stickers, signs in the background."
    )


@router.message(F.photo)
async def handle_logo_photo(message: Message) -> None:
    """Capture a logo photo from a user who ran /logo."""
    user = message.from_user
    if not user:
        return

    tenant_id = _get_pending(user.id)
    if not tenant_id:
        return

    _pending_logo_uploads.pop(user.id, None)

    # Get largest photo (last in array)
    photo = message.photo[-1]

    try:
        await save_logo_from_telegram(
            bot=message.bot,
            file_id=photo.file_id,
            file_unique_id=photo.file_unique_id,
            tenant_id=tenant_id,
        )
        await message.answer(
            "Your logo has been saved! It'll be creatively woven into your content."
        )

    except ValueError as e:
        logger.warning("Logo upload rejected", extra={"tenant_id": tenant_id, "reason": str(e)})
        await message.answer(f"Couldn't save that file: {e}\nPlease send a valid image (PNG or JPEG, under 10MB).")
    except Exception:
        logger.exception("Failed to save logo", extra={"tenant_id": tenant_id})
        await message.answer("Something went wrong saving your logo. Please try again.")
