"""Approval handler — inline button callbacks for approve/reject/edit."""

from __future__ import annotations

import hashlib
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.db import (
    create_feedback_event,
    create_posting_job,
    enqueue_job,
    get_draft,
    get_tenant_by_telegram_user,
    update_draft_status,
)

logger = logging.getLogger(__name__)

router = Router(name="approval")

# Callback data format: "approve:{draft_id}" / "reject:{draft_id}" / "regen:{draft_id}"


async def _validate_draft_access(
    callback: CallbackQuery, draft_id: str
) -> dict | None:
    """Validate that the calling user owns the draft's tenant. Returns draft or None."""
    user = callback.from_user
    if not user:
        await callback.answer("Unknown user.")
        return None

    draft = await get_draft(draft_id)
    if not draft:
        await callback.answer("Draft not found.")
        return None

    # Verify the user belongs to the draft's tenant
    membership = await get_tenant_by_telegram_user(user.id)
    if not membership or membership["tenant_id"] != draft["tenant_id"]:
        logger.warning(
            "Unauthorized draft access attempt",
            extra={"user_id": user.id, "draft_id": draft_id},
        )
        await callback.answer("You don't have access to this content.")
        return None

    return draft


@router.callback_query(F.data.startswith("approve:"))
async def handle_approve(callback: CallbackQuery) -> None:
    """Handle approval — mark draft as approved, enqueue posting jobs."""
    if not callback.data:
        return

    draft_id = callback.data.split(":", 1)[1]

    # Validate user has access to this draft
    draft = await _validate_draft_access(callback, draft_id)
    if not draft:
        return

    logger.info("Draft approved", extra={"draft_id": draft_id})

    tenant_id = draft["tenant_id"]

    # Update draft status
    await update_draft_status(draft_id, "approved")

    # Record feedback
    await create_feedback_event(draft_id=draft_id, tenant_id=tenant_id, action="approve")

    # Pick first caption variant (user selected this option)
    caption_variants = draft.get("caption_variants", [])
    caption = caption_variants[0]["text"] if caption_variants else ""
    image_urls = draft.get("image_urls", [])

    # Create posting jobs for each target platform
    # TODO: Get platform_targets from content_request, not hardcoded
    for platform in ["instagram", "facebook"]:
        idempotency_key = hashlib.sha256(
            f"{draft_id}:post_content:{platform}".encode()
        ).hexdigest()

        job = await create_posting_job(
            draft_id=draft_id,
            tenant_id=tenant_id,
            platform=platform,
            caption=caption,
            asset_urls=image_urls,
            idempotency_key=idempotency_key,
        )

        await enqueue_job(
            queue_name="posting",
            job_type="post_content",
            payload={
                "job_id": job["id"],
                "draft_id": draft_id,
                "tenant_id": tenant_id,
                "platform": platform,
                "caption": caption,
                "image_urls": image_urls,
            },
            idempotency_key=f"{draft_id}:post:{platform}",
        )

    await callback.answer("Approved! Posting now...")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(
            "Your content is being posted to all connected platforms."
        )


@router.callback_query(F.data.startswith("reject:"))
async def handle_reject(callback: CallbackQuery) -> None:
    """Handle rejection — mark draft as rejected."""
    if not callback.data:
        return

    draft_id = callback.data.split(":", 1)[1]

    draft = await _validate_draft_access(callback, draft_id)
    if not draft:
        return

    logger.info("Draft rejected", extra={"draft_id": draft_id})

    await update_draft_status(draft_id, "rejected")
    await create_feedback_event(
        draft_id=draft_id, tenant_id=draft["tenant_id"], action="reject"
    )

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

    draft = await _validate_draft_access(callback, draft_id)
    if not draft:
        return

    logger.info("Regeneration requested", extra={"draft_id": draft_id})

    await create_feedback_event(
        draft_id=draft_id, tenant_id=draft["tenant_id"], action="regenerate"
    )

    # Re-enqueue generation for the original request
    await enqueue_job(
        queue_name="content_generation",
        job_type="generate_content",
        payload={
            "request_id": draft["request_id"],
            "tenant_id": draft["tenant_id"],
            "intent": "",  # Worker will reload from content_request
            "platform_targets": ["instagram", "facebook"],
        },
        idempotency_key=f"{draft_id}:regenerate",
    )

    await callback.answer("Regenerating...")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply("Generating new options... I'll send them in a moment.")
