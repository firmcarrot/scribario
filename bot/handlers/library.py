"""Library handler — /library command + browse/post/delete callbacks."""

from __future__ import annotations

import hashlib
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.db import (
    count_library_items,
    create_posting_job,
    enqueue_job,
    get_library_item,
    get_library_items,
    get_tenant_by_telegram_user,
    update_library_item_status,
)
from bot.services.telegram import build_library_keyboard

logger = logging.getLogger(__name__)

router = Router(name="library")


@router.message(Command("library"))
async def handle_library_command(message: Message) -> None:
    """Show the first saved item from the content library."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer(
            "You need to set up your account first. Send /start to get started."
        )
        return

    tenant_id = membership["tenant_id"]
    total = await count_library_items(tenant_id)

    if total == 0:
        await message.answer(
            "Your content library is empty. When you approve a post, "
            "the other options are automatically saved here for free reuse later."
        )
        return

    items = await get_library_items(tenant_id, offset=0, limit=1)
    if not items:
        await message.answer("Your content library is empty.")
        return

    item = items[0]
    await _send_library_item(message, item, current_offset=0, total_count=total)


async def _send_library_item(
    target: Message,
    item: dict,
    current_offset: int,
    total_count: int,
) -> None:
    """Send a library item as a photo or video with keyboard."""
    caption = item.get("caption", "")
    if len(caption) > 1020:
        caption = caption[:1017] + "..."

    keyboard = build_library_keyboard(
        item_id=item["id"],
        current_offset=current_offset,
        total_count=total_count,
    )

    if item.get("media_type") == "video" and item.get("video_url"):
        await target.answer_video(
            video=item["video_url"],
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    elif item.get("image_url"):
        await target.answer_photo(
            photo=item["image_url"],
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    else:
        await target.answer(
            text=caption,
            reply_markup=keyboard,
        )


@router.callback_query(F.data.startswith("lib_nav:"))
async def handle_lib_nav(callback: CallbackQuery) -> None:
    """Handle library navigation (Next/Previous)."""
    if not callback.data or not callback.from_user:
        return

    offset = max(0, int(callback.data.split(":")[1]))

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Not registered.")
        return

    tenant_id = membership["tenant_id"]
    total = await count_library_items(tenant_id)
    items = await get_library_items(tenant_id, offset=offset, limit=1)

    if not items:
        await callback.answer("No more items.")
        return

    item = items[0]

    # Delete old message and send new one (can't edit media type)
    if callback.message:
        await callback.message.delete()
        await _send_library_item(callback.message, item, current_offset=offset, total_count=total)

    await callback.answer()


@router.callback_query(F.data.startswith("lib_post:"))
async def handle_lib_post(callback: CallbackQuery) -> None:
    """Post a library item to all connected platforms."""
    if not callback.data or not callback.from_user:
        return

    item_id = callback.data.split(":")[1]

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Not registered.")
        return

    tenant_id = membership["tenant_id"]
    item = await get_library_item(item_id, tenant_id=tenant_id)

    if not item:
        await callback.answer("Item not found.")
        return

    if item.get("status") != "saved":
        await callback.answer("Already posted or deleted.")
        return

    caption = item.get("caption", "")
    media_url = item.get("video_url") or item.get("image_url")
    asset_urls = [media_url] if media_url else []
    platform_targets = item.get("platform_targets")

    idempotency_key = hashlib.sha256(f"lib:{item_id}:post".encode()).hexdigest()

    job = await create_posting_job(
        draft_id=item.get("source_draft_id", ""),
        tenant_id=tenant_id,
        platform="all",
        caption=caption,
        asset_urls=asset_urls,
        idempotency_key=idempotency_key,
    )

    await enqueue_job(
        queue_name="posting",
        job_type="post_content",
        payload={
            "job_id": job["id"],
            "draft_id": item.get("source_draft_id", ""),
            "tenant_id": tenant_id,
            "caption": caption,
            "image_urls": asset_urls,
            "media_type": item.get("media_type", "image"),
            "platform_targets": platform_targets,
        },
        idempotency_key=f"lib:{item_id}:post",
    )

    await update_library_item_status(item_id, tenant_id=tenant_id, status="posted")

    await callback.answer("Posting now!")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply("Your saved content is being posted to all connected platforms.")


@router.callback_query(F.data.startswith("lib_delete:"))
async def handle_lib_delete(callback: CallbackQuery) -> None:
    """Delete a library item and show the next one."""
    if not callback.data or not callback.from_user:
        return

    item_id = callback.data.split(":")[1]

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Not registered.")
        return

    tenant_id = membership["tenant_id"]
    item = await get_library_item(item_id, tenant_id=tenant_id)

    if not item:
        await callback.answer("Item not found.")
        return

    await update_library_item_status(item_id, tenant_id=tenant_id, status="deleted")
    await callback.answer("Deleted.")

    # Show next item or empty message
    total = await count_library_items(tenant_id)
    if total == 0:
        if callback.message:
            await callback.message.delete()
            await callback.message.answer("Your content library is now empty.")
        return

    items = await get_library_items(tenant_id, offset=0, limit=1)
    if items and callback.message:
        await callback.message.delete()
        await _send_library_item(callback.message, items[0], current_offset=0, total_count=total)


@router.callback_query(F.data == "lib_noop")
async def handle_lib_noop(callback: CallbackQuery) -> None:
    """Handle the position indicator button (no-op)."""
    await callback.answer()
