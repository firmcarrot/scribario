"""Approval handler — inline button callbacks for approve/reject/edit."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)

router = Router(name="approval")

# Callback data format: "approve:{draft_id}" / "reject:{draft_id}" / "edit:{draft_id}"


@router.callback_query(F.data.startswith("approve:"))
async def handle_approve(callback: CallbackQuery) -> None:
    """Handle approval — mark draft as approved, enqueue posting job."""
    if not callback.data:
        return

    draft_id = callback.data.split(":", 1)[1]
    logger.info("Draft approved", extra={"draft_id": draft_id})

    # TODO: Update content_draft status → 'approved'
    # TODO: Create posting_jobs for each target platform
    # TODO: Enqueue posting jobs to pgmq

    await callback.answer("Approved! Posting now...")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply("Your content is being posted to all connected platforms.")


@router.callback_query(F.data.startswith("reject:"))
async def handle_reject(callback: CallbackQuery) -> None:
    """Handle rejection — mark draft as rejected, optionally regenerate."""
    if not callback.data:
        return

    draft_id = callback.data.split(":", 1)[1]
    logger.info("Draft rejected", extra={"draft_id": draft_id})

    # TODO: Update content_draft status → 'rejected'
    # TODO: Log feedback_event

    await callback.answer("Rejected.")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(
            "No problem! Want me to try again with a different approach? "
            "Just tell me what to change."
        )


@router.callback_query(F.data.startswith("regen:"))
async def handle_regenerate(callback: CallbackQuery) -> None:
    """Handle regenerate — create new draft from same request."""
    if not callback.data:
        return

    draft_id = callback.data.split(":", 1)[1]
    logger.info("Regeneration requested", extra={"draft_id": draft_id})

    # TODO: Get original content_request from draft
    # TODO: Enqueue new generation job

    await callback.answer("Regenerating...")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply("Generating new options... I'll send them in a moment.")
