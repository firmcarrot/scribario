"""Caption edit dialog — FSM for editing a caption variant inline."""

from __future__ import annotations

import logging

from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.states import CaptionEditSG

logger = logging.getLogger(__name__)


# --- Getters ---


async def get_edit_caption_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Provide current caption text for the edit window."""
    return {
        "current_caption": dialog_manager.start_data.get("current_caption", ""),
    }


# --- Handlers ---


async def on_cancel_edit(callback, button: Button, manager: DialogManager) -> None:
    """User cancelled — close dialog with no changes."""
    if callback.message:
        await callback.message.answer("No changes made.")
    await manager.done()


async def on_new_caption_input(
    message: Message, widget: MessageInput, manager: DialogManager
) -> None:
    """User sent edited caption text — save it and re-send preview."""
    from bot.db import update_draft_caption
    from bot.services.telegram import build_preview_keyboard

    new_caption = (message.text or "").strip()
    if not new_caption:
        await message.answer("Caption cannot be empty. Please send your edited version.")
        return

    draft_id: str = manager.start_data.get("draft_id", "")
    option_idx: int = manager.start_data.get("option_idx", 0)

    try:
        await update_draft_caption(draft_id, option_idx, new_caption)
    except Exception:
        logger.exception("Failed to update draft caption", extra={"draft_id": draft_id})
        await message.answer("Something went wrong saving your edit. Please try again.")
        return

    await message.answer("✅ Caption updated! Re-sending preview...")

    # Re-send the draft preview so user can approve/reject the updated version
    try:
        from bot.db import get_draft

        draft = await get_draft(draft_id)
        if draft:
            caption_variants = draft.get("caption_variants", [])
            image_urls = draft.get("image_urls", [])
            num_options = len(caption_variants)

            from bot.services.telegram import build_multi_option_media_group, build_preview_keyboard

            keyboard = build_preview_keyboard(draft_id, num_options)
            captions = [v.get("text", "") for v in caption_variants]

            if image_urls and captions:
                media_group = build_multi_option_media_group(image_urls, captions)
                # Send first image with keyboard, rest as follow-up group
                if len(media_group) == 1:
                    await message.answer_photo(
                        photo=image_urls[0],
                        caption=f"<b>Option 1 (edited):</b>\n{captions[0]}",
                        parse_mode="HTML",
                        reply_markup=keyboard,
                    )
                else:
                    await message.answer_media_group(media=media_group)
                    await message.answer("Choose an option:", reply_markup=keyboard)
            else:
                # Text-only preview
                preview_text = "\n\n".join(
                    f"<b>Option {i}:</b>\n{cap}" for i, cap in enumerate(captions, 1)
                )
                await message.answer(preview_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        logger.exception("Failed to re-send draft preview after edit", extra={"draft_id": draft_id})
        # Non-fatal — caption was already saved

    await manager.done()


# --- Dialog Definition ---

dialog = Dialog(
    Window(
        Format(
            "Current caption:\n{current_caption}\n\nSend your edited version:"
        ),
        Button(Const("Cancel"), id="cancel_edit", on_click=on_cancel_edit),
        MessageInput(on_new_caption_input),
        state=CaptionEditSG.edit_caption,
        getter=get_edit_caption_data,
    ),
)
