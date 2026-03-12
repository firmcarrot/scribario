"""Caption edit flow — plain FSM, no aiogram_dialog dependency."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.db import get_draft, get_tenant_by_telegram_user, update_draft_caption

logger = logging.getLogger(__name__)

router = Router(name="caption_edit")


class CaptionEditState(StatesGroup):
    waiting_for_caption = State()


# ---------------------------------------------------------------------------
# Entry point — "edit:{draft_id}:{option_number}" callback
# ---------------------------------------------------------------------------


@router.callback_query(F.data.startswith("edit:"))
async def handle_edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    """User tapped ✏️ Edit — prompt for new caption text."""
    if not callback.data:
        return

    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Invalid edit request.")
        return

    draft_id = parts[1]
    try:
        option_number = int(parts[2])
    except ValueError:
        await callback.answer("Invalid option number.")
        return

    option_idx = option_number - 1  # 0-indexed

    # Auth check
    user = callback.from_user
    if not user:
        await callback.answer("Unknown user.")
        return

    membership = await get_tenant_by_telegram_user(user.id)
    draft = await get_draft(draft_id)
    if not draft or not membership or membership["tenant_id"] != draft["tenant_id"]:
        await callback.answer("You don't have access to this content.")
        return

    # Get current caption
    caption_variants = draft.get("caption_variants") or []
    if option_idx < len(caption_variants):
        current_caption = caption_variants[option_idx].get("text", "")
    elif caption_variants:
        current_caption = caption_variants[0].get("text", "")
        option_idx = 0
    else:
        current_caption = ""

    # Store context in FSM state
    await state.set_state(CaptionEditState.waiting_for_caption)
    await state.update_data(draft_id=draft_id, option_idx=option_idx)

    await callback.answer()

    if not callback.message:
        return

    # Send prompt showing current caption
    preview = current_caption[:300] + "..." if len(current_caption) > 300 else current_caption
    await callback.message.answer(
        f"<b>Option {option_number} — current caption:</b>\n\n"
        f"{preview}\n\n"
        f"<i>Type your new version and send it. Or send /cancel to keep the original.</i>",
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# /cancel while in edit state
# ---------------------------------------------------------------------------


@router.message(CaptionEditState.waiting_for_caption, F.text == "/cancel")
async def handle_edit_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("No changes made.")


# ---------------------------------------------------------------------------
# Receive the new caption text
# ---------------------------------------------------------------------------


@router.message(CaptionEditState.waiting_for_caption, F.text)
async def handle_new_caption(message: Message, state: FSMContext) -> None:
    """User sent their edited caption — save and re-send preview."""
    new_caption = (message.text or "").strip()
    if not new_caption:
        await message.answer("Caption can't be empty. Try again, or send /cancel.")
        return

    data = await state.get_data()
    draft_id: str = data.get("draft_id", "")
    option_idx: int = data.get("option_idx", 0)

    await state.clear()

    try:
        await update_draft_caption(draft_id, option_idx, new_caption)
    except Exception:
        logger.exception("Failed to update draft caption", extra={"draft_id": draft_id})
        await message.answer("Something went wrong saving your edit. Please try again.")
        return

    # Show the edited option with a single Approve button — just post it
    try:
        draft = await get_draft(draft_id)
        if not draft:
            await message.answer("✅ Caption saved.")
            return

        image_urls = draft.get("image_urls") or []
        image_url = image_urls[option_idx] if option_idx < len(image_urls) else None

        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="✅ Post it",
                callback_data=f"approve:{draft_id}:{option_idx + 1}",
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data=f"reject:{draft_id}",
            ),
        ]])

        caption_text = f"<b>Your edited caption:</b>\n\n{new_caption}"
        if len(caption_text) > 1020:
            caption_text = caption_text[:1017] + "..."

        if image_url:
            await message.answer_photo(
                photo=image_url,
                caption=caption_text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        else:
            await message.answer(caption_text, parse_mode="HTML", reply_markup=keyboard)

    except Exception:
        logger.exception("Failed to send post-edit preview", extra={"draft_id": draft_id})
        await message.answer("✅ Caption saved. Use the original approval buttons to post.")
