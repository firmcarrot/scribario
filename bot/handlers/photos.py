"""Photo intake handler — processes photo messages for content generation or reference saving.

Decision logic:
  - Photo + caption/text → generation request (photo used as one-time reference)
  - Photo alone → disambiguation: [Save as Reference] or [Create a Post With This]
  - Album (media_group_id) → debounced: collect all photos, treat as single interaction

Labeling flow (after Save as Reference):
  User taps one of: [Me] [My Partner] [My Product] [Other]
  → photo downloaded, EXIF stripped, stored in private Supabase Storage
  → DB record created with chosen label
  → confirmation sent

Albums (Telegram sends each photo as separate message with same media_group_id):
  → 1.5s debounce buffer collects all photos
  → Treated as single interaction: download all, ask once
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.config import get_settings
from bot.db import (
    MAX_PHOTOS_PER_TENANT,
    count_reference_photos,
    create_content_request,
    create_reference_photo,
    enqueue_job,
    get_reference_photos,
    get_tenant_by_telegram_user,
    soft_delete_reference_photo,
    toggle_reference_photo_default,
)
from bot.services.storage import download_and_store

if TYPE_CHECKING:
    from aiogram import Bot

logger = logging.getLogger(__name__)
router = Router(name="photos")

# Album debounce state: media_group_id → list of (message, file_id, file_unique_id)
_album_buffer: dict[str, list[dict]] = {}
_album_timers: dict[str, asyncio.TimerHandle] = {}
_album_processed: set[str] = set()

# Pending photo cache: short_key → {file_unique_id, storage_path}
# Avoids embedding long paths in callback_data (Telegram 64-byte limit)
_pending_photos: dict[str, dict] = {}

# Pending "Create a Post" photos: user_id → {storage_path, file_unique_id}
# Stored when user taps "Create a Post" so next text message uses the photo
_pending_post_photos: dict[int, dict] = {}

BOT_TOKEN: str = ""  # Set at startup from config


def _get_message(callback: CallbackQuery) -> Message | None:
    """Safely extract Message from callback. Returns None if InaccessibleMessage."""
    if isinstance(callback.message, Message):
        return callback.message
    return None


def _build_disambiguation_keyboard(file_unique_id: str, file_id: str) -> InlineKeyboardMarkup:
    """Inline keyboard: Save as Reference or Create a Post."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💾 Save as Reference",
                callback_data=f"photo_action:save:{file_unique_id}:{file_id}",
            ),
            InlineKeyboardButton(
                text="📸 Create a Post",
                callback_data=f"photo_action:post:{file_unique_id}:{file_id}",
            ),
        ]
    ])


def _store_pending_photo(file_unique_id: str, storage_path: str) -> str:
    """Cache photo data and return a short key safe for callback_data.

    Telegram callback_data is limited to 64 bytes. Storage paths are too long
    to embed directly, so we store them in memory and pass only the short key.
    Key format: first 8 chars of file_unique_id (stable, unique per file).
    """
    key = file_unique_id[:8]
    _pending_photos[key] = {"file_unique_id": file_unique_id, "storage_path": storage_path}
    return key


def _build_label_keyboard(file_unique_id: str, storage_path: str) -> InlineKeyboardMarkup:
    """Inline keyboard for labeling a saved reference photo.

    Uses short cache key instead of embedding storage_path (Telegram 64-byte limit).
    """
    key = _store_pending_photo(file_unique_id, storage_path)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🙋 Me", callback_data=f"photo_label:owner:{key}"),
            InlineKeyboardButton(text="👥 My Partner", callback_data=f"photo_label:partner:{key}"),
        ],
        [
            InlineKeyboardButton(text="📦 My Product", callback_data=f"photo_label:product:{key}"),
            InlineKeyboardButton(text="🏷️ Other", callback_data=f"photo_label:other:{key}"),
        ],
    ])


def _label_display(label: str) -> str:
    return {
        "owner": "you",
        "partner": "your partner",
        "product": "your product",
        "other": "other",
    }.get(label, label)


async def _download_photo(bot: Bot, message: Message) -> tuple[str, str, str]:
    """Download a photo from a message. Returns (download_url, file_unique_id, file_id)."""
    photo = message.photo[-1]  # Largest size
    file = await bot.get_file(photo.file_id)
    token = get_settings().telegram_bot_token
    download_url = f"https://api.telegram.org/file/bot{token}/{file.file_path}"
    return download_url, photo.file_unique_id, photo.file_id


@router.message(F.photo)
async def handle_photo_message(message: Message, bot: Bot) -> None:
    """Route photo messages: with caption → generate; alone → disambiguate."""
    user = message.from_user
    if not user:
        return

    # Check tenant
    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer(
            "You're not connected to any brand yet.\n"
            "Use /start to set up your account."
        )
        return

    # Guard: incomplete onboarding
    if membership.get("onboarding_status") != "complete":
        await message.answer(
            "Looks like you haven't finished setting up yet. "
            "Use /start to complete your profile."
        )
        return

    # Album handling — debounce multi-photo messages
    if message.media_group_id:
        await _handle_album_photo(message, bot, membership)
        return

    # Single photo
    photo = message.photo[-1] if message.photo else None
    if not photo:
        return

    caption = message.caption or message.text or ""

    if caption.strip():
        # Photo + text → treat as generation request with this photo as reference
        await _handle_photo_with_intent(message, bot, membership, caption.strip())
    else:
        # Photo alone → ask what to do
        await message.answer(
            "Got a photo! What would you like to do with it?",
            reply_markup=_build_disambiguation_keyboard(
                file_unique_id=photo.file_unique_id,
                file_id=photo.file_id,
            ),
        )


async def _handle_photo_with_intent(
    message: Message,
    bot: Bot,
    membership: dict,
    intent: str,
) -> None:
    """Photo + intent text → download photo, store as temp ref, enqueue generation."""
    from bot.handlers.intake import parse_platform_targets

    tenant_id = membership["tenant_id"]
    message.photo[-1]

    # Download and store
    try:
        download_url, file_unique_id, _file_id = await _download_photo(bot, message)
        storage_path = await download_and_store(
            download_url=download_url,
            tenant_id=tenant_id,
            file_unique_id=file_unique_id,
        )
    except Exception as e:
        logger.error("Failed to store photo", extra={"error": str(e)})
        await message.answer(
            "I couldn't save your photo. Please try again or send it separately."
        )
        return

    # Detect platform mentions in caption (None = all connected)
    platform_targets = parse_platform_targets(intent)

    # Create content request with photo reference
    request = await create_content_request(
        tenant_id=tenant_id,
        intent=intent,
        platform_targets=platform_targets,
    )
    request_id = request["id"]

    await enqueue_job(
        queue_name="content_generation",
        job_type="generate_content",
        payload={
            "request_id": request_id,
            "tenant_id": tenant_id,
            "intent": intent,
            "platform_targets": platform_targets,
            "telegram_chat_id": message.chat.id,
            "new_photo_storage_paths": [storage_path],
        },
        idempotency_key=f"{request_id}:generate_content",
    )

    await message.answer(
        f"Got it! Generating content for:\n\n"
        f"<i>{intent}</i>\n\n"
        "I'll use your photo as a reference. This takes about 30-60 seconds — I'll send you a preview.",
        parse_mode="HTML",
    )


async def _handle_album_photo(message: Message, bot: Bot, membership: dict) -> None:
    """Buffer album photos and process after 1.5s debounce."""
    group_id = message.media_group_id
    if group_id in _album_processed:
        return

    photo = message.photo[-1] if message.photo else None
    if not photo:
        return

    if group_id not in _album_buffer:
        _album_buffer[group_id] = []

    _album_buffer[group_id].append({
        "message": message,
        "file_id": photo.file_id,
        "file_unique_id": photo.file_unique_id,
        "caption": message.caption or "",
        "membership": membership,
    })

    # Cancel existing timer and reset
    if group_id in _album_timers:
        _album_timers[group_id].cancel()

    loop = asyncio.get_running_loop()
    handle = loop.call_later(
        1.5,
        lambda gid=group_id: asyncio.ensure_future(_process_album(gid, bot)),
    )
    _album_timers[group_id] = handle


async def _process_album(group_id: str, bot: Bot) -> None:
    """Process a complete album after debounce window."""
    if group_id in _album_processed:
        return
    _album_processed.add(group_id)

    photos = _album_buffer.pop(group_id, [])
    _album_timers.pop(group_id, None)

    if not photos:
        return

    first = photos[0]
    message: Message = first["message"]
    membership: dict = first["membership"]
    # Caption is on the first photo in the group
    caption = next((p["caption"] for p in photos if p["caption"]), "")

    if caption.strip():
        # Album + caption → generation with all photos as references
        await _handle_album_with_intent(photos, bot, membership, caption.strip())
    else:
        # Album alone → disambiguation for the batch
        count = len(photos)
        first_photo_unique = photos[0]["file_unique_id"]
        first_photo_file_id = photos[0]["file_id"]
        await message.answer(
            f"Got {count} photo{'s' if count > 1 else ''}! What would you like to do?",
            reply_markup=_build_disambiguation_keyboard(
                file_unique_id=first_photo_unique,
                file_id=first_photo_file_id,
            ),
        )


async def _handle_album_with_intent(
    photos: list[dict],
    bot: Bot,
    membership: dict,
    intent: str,
) -> None:
    """Album + intent → download all photos, store, enqueue generation."""
    from bot.handlers.intake import parse_platform_targets

    tenant_id = membership["tenant_id"]
    message: Message = photos[0]["message"]

    storage_paths: list[str] = []
    for photo_data in photos:
        try:
            msg: Message = photo_data["message"]
            photo = msg.photo[-1]
            file = await bot.get_file(photo.file_id)
            token = get_settings().telegram_bot_token
            download_url = f"https://api.telegram.org/file/bot{token}/{file.file_path}"
            path = await download_and_store(
                download_url=download_url,
                tenant_id=tenant_id,
                file_unique_id=photo_data["file_unique_id"],
            )
            storage_paths.append(path)
        except Exception as e:
            logger.warning("Failed to store album photo", extra={"error": str(e)})

    if not storage_paths:
        await message.answer("I couldn't save your photos. Please try again.")
        return

    # Detect platform mentions in caption (None = all connected)
    platform_targets = parse_platform_targets(intent)

    request = await create_content_request(
        tenant_id=tenant_id,
        intent=intent,
        platform_targets=platform_targets,
    )
    request_id = request["id"]

    await enqueue_job(
        queue_name="content_generation",
        job_type="generate_content",
        payload={
            "request_id": request_id,
            "tenant_id": tenant_id,
            "intent": intent,
            "platform_targets": platform_targets,
            "telegram_chat_id": message.chat.id,
            "new_photo_storage_paths": storage_paths,
        },
        idempotency_key=f"{request_id}:generate_content",
    )

    count = len(storage_paths)
    await message.answer(
        f"Got it! Using {count} photo{'s' if count > 1 else ''} for:\n\n"
        f"<i>{intent}</i>\n\n"
        f"Generating your content — about 30-60 seconds.",
        parse_mode="HTML",
    )


# --- Callback handlers ---

@router.callback_query(F.data.startswith("photo_action:save:"))
async def handle_save_reference_callback(callback: CallbackQuery, bot: Bot) -> None:
    """User tapped 'Save as Reference' — download photo and ask for label."""
    if not callback.data:
        return
    msg = _get_message(callback)
    if not msg:
        return

    parts = callback.data.split(":", 3)
    # photo_action:save:{file_unique_id}:{file_id}
    if len(parts) < 4:
        await callback.answer("Something went wrong. Please try again.")
        return

    file_unique_id = parts[2]
    file_id = parts[3]

    user = callback.from_user
    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await callback.answer("Account not found. Use /start to set up.")
        return

    tenant_id = membership["tenant_id"]

    # Check limit BEFORE downloading
    count = await count_reference_photos(tenant_id)
    if count >= MAX_PHOTOS_PER_TENANT:
        await msg.edit_text(
            f"You've reached the limit of {MAX_PHOTOS_PER_TENANT} saved reference photos.\n"
            f"Use /photos to delete some before adding new ones."
        )
        await callback.answer()
        return

    # Download and store
    try:
        file = await bot.get_file(file_id)
        token = get_settings().telegram_bot_token
        download_url = f"https://api.telegram.org/file/bot{token}/{file.file_path}"
        storage_path = await download_and_store(
            download_url=download_url,
            tenant_id=tenant_id,
            file_unique_id=file_unique_id,
        )
    except Exception as e:
        logger.error("Failed to store reference photo", extra={"error": str(e)})
        await msg.edit_text("I couldn't save that photo. Please try sending it again.")
        await callback.answer()
        return

    # Ask for label
    await msg.edit_text(
        "Photo saved! What is this a photo of?",
        reply_markup=_build_label_keyboard(
            file_unique_id=file_unique_id,
            storage_path=storage_path,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("photo_action:post:"))
async def handle_post_with_photo_callback(callback: CallbackQuery, bot: Bot) -> None:
    """User tapped 'Create a Post' — download photo, stash for next message, ask for intent."""
    msg = _get_message(callback)
    if not msg:
        return

    if not callback.data:
        return

    parts = callback.data.split(":", 3)
    # photo_action:post:{file_unique_id}:{file_id}
    if len(parts) < 4:
        await callback.answer("Something went wrong.")
        return

    file_unique_id = parts[2]
    file_id = parts[3]
    user = callback.from_user

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await callback.answer("Account not found. Use /start to set up.")
        return

    tenant_id = membership["tenant_id"]

    # Download and store the photo now so it's ready when user sends text
    try:
        file = await bot.get_file(file_id)
        token = get_settings().telegram_bot_token
        download_url = f"https://api.telegram.org/file/bot{token}/{file.file_path}"
        storage_path = await download_and_store(
            download_url=download_url,
            tenant_id=tenant_id,
            file_unique_id=file_unique_id,
        )
        # Stash for the user's next text message
        _pending_post_photos[user.id] = {
            "storage_path": storage_path,
            "file_unique_id": file_unique_id,
        }
    except Exception as e:
        logger.error("Failed to store post photo", extra={"error": str(e)})
        # Continue anyway — user can still describe the post, just without the photo
        logger.warning("Continuing without photo for user %s", user.id)

    await msg.edit_text(
        "What should I create? Describe the post:\n\n"
        "<i>Example: Put me eating Mondo Shrimp over an exploding volcano — dangerously good</i>",
        parse_mode="HTML",
        reply_markup=None,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("photo_label:"))
async def handle_label_callback(callback: CallbackQuery) -> None:
    """User tapped a label button — save reference photo with chosen label."""
    if not callback.data:
        return
    msg = _get_message(callback)
    if not msg:
        return

    # Format: photo_label:{label}:{short_key}
    parts = callback.data.split(":", 2)
    if len(parts) < 3:
        await callback.answer("Something went wrong.")
        return

    label = parts[1]
    short_key = parts[2]

    pending = _pending_photos.get(short_key)
    if not pending:
        await callback.answer("Session expired. Please send the photo again.")
        await msg.edit_text("This label prompt has expired. Please send your photo again.")
        return

    file_unique_id = pending["file_unique_id"]
    storage_path = pending["storage_path"]

    user = callback.from_user
    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await callback.answer("Account not found.")
        return

    tenant_id = membership["tenant_id"]

    # Check limit again (race condition guard)
    count = await count_reference_photos(tenant_id)
    if count >= MAX_PHOTOS_PER_TENANT:
        await msg.edit_text(
            f"You've reached the limit of {MAX_PHOTOS_PER_TENANT} saved photos.\n"
            f"Use /photos to manage your saved photos."
        )
        await callback.answer()
        return

    # Save to DB
    await create_reference_photo(
        tenant_id=tenant_id,
        uploaded_by=user.id,
        label=label,
        storage_path=storage_path,
        file_unique_id=file_unique_id,
        is_default=True,
    )
    # Clean up pending cache entry
    _pending_photos.pop(short_key, None)

    label_name = _label_display(label)
    await msg.edit_text(
        f"✅ Saved as <b>{label_name}</b>! I'll use this photo in future content.\n\n"
        "Send another photo or type what you'd like to post about.",
        parse_mode="HTML",
    )
    await callback.answer("Saved!")


# --- /photos command ---

PHOTOS_PER_PAGE = 5


@router.message(Command("photos"))
async def handle_photos_command(message: Message) -> None:
    """List saved reference photos with management options."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer("Use /start to set up your account first.")
        return

    tenant_id = membership["tenant_id"]
    photos = await get_reference_photos(tenant_id)

    if not photos:
        await message.answer(
            "You have no saved reference photos yet.\n\n"
            "Send me a photo and tap <b>Save as Reference</b> to add one!",
            parse_mode="HTML",
        )
        return

    await _send_photos_page(message, photos, page=0)


def _build_photos_page(photos: list[dict], page: int = 0) -> tuple[str, InlineKeyboardMarkup | None]:
    """Build text and keyboard for a paginated list of reference photos."""
    total = len(photos)
    start = page * PHOTOS_PER_PAGE
    end = min(start + PHOTOS_PER_PAGE, total)
    page_photos = photos[start:end]

    label_emoji = {"owner": "🙋", "partner": "👥", "product": "📦", "other": "🏷️"}

    lines = [f"📷 <b>Your reference photos</b> ({total} total)\n"]
    buttons: list[list[InlineKeyboardButton]] = []

    for i, photo in enumerate(page_photos):
        idx = start + i + 1
        label = photo.get("label", "other")
        is_default = photo.get("is_default", False)
        emoji = label_emoji.get(label, "🏷️")
        default_marker = " ✓" if is_default else ""
        lines.append(f"{idx}. {emoji} <b>{label.capitalize()}</b>{default_marker}")

        photo_id = photo["id"]
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑 Delete #{idx}",
                callback_data=f"photo_mgmt:delete:{photo_id}",
            ),
            InlineKeyboardButton(
                text=f"{'⭐ Unset' if is_default else '⭐ Set'} Default #{idx}",
                callback_data=f"photo_mgmt:toggle:{photo_id}:{0 if is_default else 1}",
            ),
        ])

    # Pagination
    nav_row: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(
            text="◀ Prev", callback_data=f"photo_mgmt:page:{page - 1}"
        ))
    if end < total:
        nav_row.append(InlineKeyboardButton(
            text="Next ▶", callback_data=f"photo_mgmt:page:{page + 1}"
        ))
    if nav_row:
        buttons.append(nav_row)

    markup = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    return "\n".join(lines), markup


async def _send_photos_page(message: Message, photos: list[dict], page: int = 0) -> None:
    """Send a new message with paginated reference photos list."""
    text, markup = _build_photos_page(photos, page)
    await message.answer(text, parse_mode="HTML", reply_markup=markup)


async def _edit_photos_page(message: Message, photos: list[dict], page: int = 0) -> None:
    """Edit existing message with paginated reference photos list (used in callbacks)."""
    text, markup = _build_photos_page(photos, page)
    await message.edit_text(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data.startswith("photo_mgmt:delete:"))
async def handle_delete_photo(callback: CallbackQuery) -> None:
    """Soft-delete a reference photo."""
    if not callback.data:
        return
    msg = _get_message(callback)
    if not msg:
        return

    photo_id = callback.data.split(":", 2)[2]
    user = callback.from_user
    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await callback.answer("Account not found.")
        return

    await soft_delete_reference_photo(photo_id=photo_id, tenant_id=membership["tenant_id"])
    await callback.answer("Photo deleted.")

    # Refresh the list — edit in place, no second message
    photos = await get_reference_photos(membership["tenant_id"])
    if photos:
        await _edit_photos_page(msg, photos, page=0)
    else:
        await msg.edit_text(
            "Photo deleted. You have no more saved reference photos.\n\n"
            "Send me a photo to add one!",
            reply_markup=None,
        )


@router.callback_query(F.data.startswith("photo_mgmt:toggle:"))
async def handle_toggle_default(callback: CallbackQuery) -> None:
    """Toggle is_default on a reference photo."""
    if not callback.data:
        return
    msg = _get_message(callback)
    if not msg:
        return

    parts = callback.data.split(":")
    # photo_mgmt:toggle:{photo_id}:{0 or 1}
    if len(parts) < 4:
        await callback.answer("Something went wrong.")
        return

    photo_id = parts[2]
    is_default = parts[3] == "1"
    user = callback.from_user
    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await callback.answer("Account not found.")
        return

    await toggle_reference_photo_default(
        photo_id=photo_id,
        tenant_id=membership["tenant_id"],
        is_default=is_default,
    )

    status = "set as default" if is_default else "removed from defaults"
    await callback.answer(f"Photo {status}.")

    # Refresh the list — edit in place
    photos = await get_reference_photos(membership["tenant_id"])
    if photos:
        await _edit_photos_page(msg, photos, page=0)


@router.callback_query(F.data.startswith("photo_mgmt:page:"))
async def handle_photos_page(callback: CallbackQuery) -> None:
    """Navigate to a photos page."""
    if not callback.data:
        return
    msg = _get_message(callback)
    if not msg:
        return

    page = int(callback.data.split(":")[2])
    user = callback.from_user
    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await callback.answer("Account not found.")
        return

    photos = await get_reference_photos(membership["tenant_id"])
    await callback.answer()
    await _edit_photos_page(msg, photos, page=page)
