"""Caption edit flow — AI-assisted revision via plain FSM."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.db import (
    create_feedback_event,
    get_draft,
    get_tenant_by_telegram_user,
    log_usage_event,
    update_draft_caption,
)
from bot.dialogs.states import CaptionEditSG
from pipeline.brand_voice import load_brand_profile, load_few_shot_examples
from pipeline.caption_gen import revise_caption

logger = logging.getLogger(__name__)

router = Router(name="caption_edit")


# ---------------------------------------------------------------------------
# Entry point — "edit:{draft_id}:{option_number}" callback
# ---------------------------------------------------------------------------


@router.callback_query(F.data.startswith("edit:"))
async def handle_edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    """User tapped ✏️ Edit — show current caption and ask what to change."""
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
    await state.set_state(CaptionEditSG.waiting_for_edit_instruction)
    await state.update_data(draft_id=draft_id, option_idx=option_idx)

    await callback.answer()

    if not callback.message:
        return

    await callback.message.answer(current_caption)
    await callback.message.answer(
        f"<b>✏️ Option {option_number} — what should I change?</b>\n\n"
        'Tell me what to fix, e.g. <i>"make it shorter"</i>, <i>"add emojis"</i>, '
        '<i>"stronger CTA"</i>\n\n'
        "<i>Send /cancel to keep the original.</i>",
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# /cancel while waiting for edit instruction
# ---------------------------------------------------------------------------


@router.message(CaptionEditSG.waiting_for_edit_instruction, F.text == "/cancel")
async def handle_edit_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("No changes made.")


# ---------------------------------------------------------------------------
# Receive the edit instruction — call Claude, re-preview
# ---------------------------------------------------------------------------


@router.message(CaptionEditSG.waiting_for_edit_instruction, F.text)
async def handle_edit_instruction(message: Message, state: FSMContext) -> None:
    """User described what to change — revise with AI and re-preview."""
    instruction = (message.text or "").strip()
    if not instruction:
        await message.answer("Instruction can't be empty. Try again, or send /cancel.")
        return

    data = await state.get_data()
    draft_id: str = data.get("draft_id", "")
    option_idx: int = data.get("option_idx", 0)

    # Validate the draft exists before clearing state — transient DB errors stay recoverable
    draft = await get_draft(draft_id)
    if not draft:
        await state.clear()
        await message.answer("Couldn't find the original draft. Please try again.")
        return

    await state.clear()

    # Get current caption text
    caption_variants = draft.get("caption_variants") or []
    if option_idx < len(caption_variants):
        current_caption = caption_variants[option_idx].get("text", "")
    else:
        current_caption = caption_variants[0].get("text", "") if caption_variants else ""

    tenant_id: str = draft["tenant_id"]

    # Load brand context
    profile = await load_brand_profile(tenant_id)
    if profile is None:
        logger.error("Brand profile not found for revision", extra={"tenant_id": tenant_id})
        await message.answer("Brand profile not found. Please contact support.")
        return

    examples = await load_few_shot_examples(tenant_id)

    # Revise with Claude
    try:
        revised = await revise_caption(
            current_caption=current_caption,
            instruction=instruction,
            profile=profile,
            examples=examples,
        )
    except Exception:
        logger.exception("Caption revision failed", extra={"draft_id": draft_id})
        await message.answer("Something went wrong generating the revision. Please try again.")
        return

    # Save the revised caption
    try:
        await update_draft_caption(draft_id, option_idx, revised.text)
    except Exception:
        logger.exception("Failed to save revised caption", extra={"draft_id": draft_id})
        await message.answer("Something went wrong saving the revision. Please try again.")
        return

    # Log caption revision cost (AFTER primary op succeeds)
    try:
        from pipeline.cost_utils import compute_anthropic_cost

        cost = compute_anthropic_cost(
            revised.model, revised.input_tokens or 0, revised.output_tokens or 0
        )
        await log_usage_event(
            tenant_id=tenant_id,
            event_type="caption_revision",
            provider="anthropic",
            cost_usd=cost,
            input_tokens=revised.input_tokens,
            output_tokens=revised.output_tokens,
            model=revised.model,
        )
    except Exception:
        logger.exception("Failed to log caption revision cost")

    # Log feedback event for brand voice learning
    try:
        await create_feedback_event(
            draft_id=draft_id,
            tenant_id=tenant_id,
            action="edit",
            edited_caption=revised.text,
            original_caption=current_caption,
            edit_instruction=instruction,
        )
    except Exception:
        logger.warning("Failed to log feedback event for edit", extra={"draft_id": draft_id})
        # Non-critical — don't block the user

    # Fire-and-forget: analyze edit pattern with Haiku
    try:
        from pipeline.learning.edit_analyzer import fire_and_forget_edit_analysis
        fire_and_forget_edit_analysis(
            tenant_id=tenant_id,
            original_caption=current_caption,
            edit_instruction=instruction,
            edited_caption=revised.text,
        )
    except Exception:
        pass  # Learning is non-critical

    # Build re-preview keyboard: Post it / Edit Again / Discard (permanently rejects draft)
    option_number = option_idx + 1
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Post it",
                    callback_data=f"approve:{draft_id}:{option_number}",
                ),
                InlineKeyboardButton(
                    text="✏️ Edit Again",
                    callback_data=f"edit:{draft_id}:{option_number}",
                ),
                InlineKeyboardButton(
                    text="❌ Discard",
                    callback_data=f"reject:{draft_id}",
                ),
            ]
        ]
    )

    # Truncate the raw caption before wrapping in HTML to avoid cutting mid-tag
    display_caption = revised.text if len(revised.text) <= 950 else revised.text[:947] + "..."
    caption_text = f"<b>Revised caption:</b>\n\n{display_caption}"

    image_urls = draft.get("image_urls") or []
    image_url = image_urls[option_idx] if option_idx < len(image_urls) else None

    try:
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
        logger.exception("Failed to send re-preview", extra={"draft_id": draft_id})
        await message.answer("✅ Caption revised. Use the original approval buttons to post.")
