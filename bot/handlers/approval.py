"""Approval handler — inline button callbacks for approve/reject/edit."""

from __future__ import annotations

import hashlib
import logging
import time

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.db import (
    create_feedback_event,
    create_posting_job,
    enqueue_job,
    get_draft,
    get_supabase_client,
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
    """Handle approval — mark draft as approved, enqueue posting jobs.

    Callback data format: "approve:{draft_id}:{option_number}"
    """
    if not callback.data:
        return

    parts = callback.data.split(":")
    draft_id = parts[1]
    # Option number (1-indexed), default to 1 for backwards compat
    option_idx = int(parts[2]) - 1 if len(parts) > 2 else 0

    # Validate user has access to this draft
    draft = await _validate_draft_access(callback, draft_id)
    if not draft:
        return

    # Prevent double-click: only approve if still in "previewing" state
    if draft.get("status") != "previewing":
        await callback.answer("Already handled.")
        return

    logger.info("Draft approved", extra={"draft_id": draft_id, "option": option_idx + 1})

    tenant_id = draft["tenant_id"]

    # Update draft status
    await update_draft_status(draft_id, "approved")

    # Record feedback
    await create_feedback_event(draft_id=draft_id, tenant_id=tenant_id, action="approve")

    # Pick the selected caption variant
    caption_variants = draft.get("caption_variants", [])
    if option_idx < len(caption_variants):
        caption = caption_variants[option_idx].get("text", "")
    elif caption_variants:
        caption = caption_variants[0].get("text", "")
    else:
        caption = ""
    all_image_urls = draft.get("image_urls", [])
    image_urls = [all_image_urls[option_idx]] if option_idx < len(all_image_urls) else all_image_urls[:1]

    # Load platform_targets from the originating content_request
    _client = get_supabase_client()
    _req = (
        _client.table("content_requests")
        .select("platform_targets")
        .eq("id", draft["request_id"])
        .limit(1)
        .execute()
    )
    platform_targets: list[str] | None = (
        _req.data[0].get("platform_targets") if _req.data else None
    ) or None

    # Create one posting job — worker matches against connected Postiz integrations
    idempotency_key = hashlib.sha256(f"{draft_id}:post_content".encode()).hexdigest()

    job = await create_posting_job(
        draft_id=draft_id,
        tenant_id=tenant_id,
        platform="all",
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
            "caption": caption,
            "image_urls": image_urls,
            "platform_targets": platform_targets,
        },
        idempotency_key=f"{draft_id}:post:all",
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

    if draft.get("status") != "previewing":
        await callback.answer("Already handled.")
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

    if draft.get("status") not in ("previewing", "generated"):
        await callback.answer("Already handled.")
        return

    logger.info("Regeneration requested", extra={"draft_id": draft_id})

    await create_feedback_event(
        draft_id=draft_id, tenant_id=draft["tenant_id"], action="regenerate"
    )

    # Load the original content request to get the intent
    client = get_supabase_client()
    req_result = (
        client.table("content_requests")
        .select("intent, platform_targets")
        .eq("id", draft["request_id"])
        .limit(1)
        .execute()
    )
    original = req_result.data[0] if req_result.data else {}

    # Re-enqueue generation for the original request
    await enqueue_job(
        queue_name="content_generation",
        job_type="generate_content",
        payload={
            "request_id": draft["request_id"],
            "tenant_id": draft["tenant_id"],
            "intent": original.get("intent", ""),
            "platform_targets": original.get("platform_targets") or None,
            "telegram_chat_id": callback.message.chat.id if callback.message else None,
        },
        idempotency_key=f"{draft_id}:regenerate",
    )

    await callback.answer("Regenerating...")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply("Generating new options... I'll send them in a moment.")


@router.callback_query(F.data.startswith("make_video:"))
async def handle_make_video(callback: CallbackQuery) -> None:
    """Handle "Make Video" — enqueue video generation using the draft's first image + caption.

    Callback data format: "make_video:{draft_id}"
    """
    if not callback.data:
        return

    draft_id = callback.data.split(":", 1)[1]

    draft = await _validate_draft_access(callback, draft_id)
    if not draft:
        return

    if draft.get("status") not in ("previewing", "generated"):
        await callback.answer("Already handled.")
        return

    tenant_id = draft["tenant_id"]

    # Build prompt from first caption's visual_prompt, fallback to caption text
    caption_variants = draft.get("caption_variants") or []
    prompt = ""
    if caption_variants:
        prompt = caption_variants[0].get("visual_prompt", "") or caption_variants[0].get("text", "")

    # Use first image as reference if available
    image_urls = draft.get("image_urls") or []
    generation_type = "REFERENCE_2_VIDEO" if image_urls else "TEXT_2_VIDEO"
    ref_urls = image_urls[:1] if image_urls else None

    logger.info(
        "Make Video requested",
        extra={"draft_id": draft_id, "tenant_id": tenant_id, "generation_type": generation_type},
    )

    await create_feedback_event(
        draft_id=draft_id, tenant_id=tenant_id, action="make_video"
    )

    minute_bucket = int(time.time()) // 60
    try:
        await enqueue_job(
            queue_name="content_generation",
            job_type="generate_video",
            payload={
                "draft_id": draft_id,
                "tenant_id": tenant_id,
                "prompt": prompt,
                "aspect_ratio": "16:9",
                "generation_type": generation_type,
                "image_urls": ref_urls,
                "telegram_chat_id": callback.message.chat.id if callback.message else None,
            },
            idempotency_key=f"{draft_id}:make_video:{minute_bucket}",
        )
    except Exception as exc:
        logger.warning(
            "make_video enqueue failed (likely duplicate tap)",
            extra={"draft_id": draft_id, "error": str(exc)},
        )
        await callback.answer("Already generating video — please wait.")
        return

    await callback.answer("Generating video...")
    if callback.message:
        await callback.message.reply(
            "Generating a video from your content... This takes 1-3 minutes."
        )


@router.callback_query(F.data.startswith("approve_video:"))
async def handle_approve_video(callback: CallbackQuery) -> None:
    """Handle video approval — enqueue posting with video."""
    if not callback.data:
        return

    draft_id = callback.data.split(":", 1)[1]

    draft = await _validate_draft_access(callback, draft_id)
    if not draft:
        return

    if draft.get("status") not in ("previewing", "generated"):
        await callback.answer("Already handled.")
        return

    tenant_id = draft["tenant_id"]

    await update_draft_status(draft_id, "approved")
    await create_feedback_event(draft_id=draft_id, tenant_id=tenant_id, action="approve_video")

    # Use the video_url for posting
    video_url = draft.get("video_url", "")
    caption_variants = draft.get("caption_variants", [])
    caption = caption_variants[0].get("text", "") if caption_variants else ""

    # Load platform_targets from originating content_request
    _client = get_supabase_client()
    _req = (
        _client.table("content_requests")
        .select("platform_targets")
        .eq("id", draft["request_id"])
        .limit(1)
        .execute()
    )
    platform_targets: list[str] | None = (
        _req.data[0].get("platform_targets") if _req.data else None
    ) or None

    idempotency_key = hashlib.sha256(f"{draft_id}:post_video".encode()).hexdigest()

    job = await create_posting_job(
        draft_id=draft_id,
        tenant_id=tenant_id,
        platform="all",
        caption=caption,
        asset_urls=[video_url] if video_url else [],
        idempotency_key=idempotency_key,
    )

    await enqueue_job(
        queue_name="posting",
        job_type="post_content",
        payload={
            "job_id": job["id"],
            "draft_id": draft_id,
            "tenant_id": tenant_id,
            "caption": caption,
            "image_urls": [video_url] if video_url else [],
            "media_type": "video",
            "platform_targets": platform_targets,
        },
        idempotency_key=f"{draft_id}:post:video",
    )

    await callback.answer("Approved! Posting video now...")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(
            "Your video is being posted to all connected platforms."
        )


@router.callback_query(F.data.startswith("reject_video:"))
async def handle_reject_video(callback: CallbackQuery) -> None:
    """Handle video rejection."""
    if not callback.data:
        return

    draft_id = callback.data.split(":", 1)[1]

    draft = await _validate_draft_access(callback, draft_id)
    if not draft:
        return

    if draft.get("status") not in ("previewing", "generated"):
        await callback.answer("Already handled.")
        return

    await create_feedback_event(
        draft_id=draft_id, tenant_id=draft["tenant_id"], action="reject_video"
    )

    await callback.answer("Video rejected.")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(
            "No problem! The original images are still available above."
        )


@router.callback_query(F.data.startswith("regen_image:"))
async def handle_regen_image(callback: CallbackQuery) -> None:
    """Handle image-only regeneration — regenerate one image, keep its caption.

    Callback data format: "regen_image:{draft_id}:{option_number}"
    """
    if not callback.data:
        return

    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Invalid request.")
        return

    draft_id = parts[1]
    try:
        option_number = int(parts[2])
    except ValueError:
        await callback.answer("Invalid option number.")
        return

    option_idx = option_number - 1  # 0-indexed

    draft = await _validate_draft_access(callback, draft_id)
    if not draft:
        return

    if draft.get("status") not in ("previewing", "generated"):
        await callback.answer("Already handled.")
        return

    # Get the visual prompt for this option
    caption_variants = draft.get("caption_variants") or []
    if option_idx >= len(caption_variants):
        await callback.answer("Option not found.")
        return

    visual_prompt = caption_variants[option_idx].get("visual_prompt", "")
    tenant_id = draft["tenant_id"]

    logger.info(
        "Image-only regen requested",
        extra={"draft_id": draft_id, "option_idx": option_idx, "tenant_id": tenant_id},
    )

    await create_feedback_event(
        draft_id=draft_id, tenant_id=tenant_id, action="regenerate"
    )

    # Use a minute-bucket key so users can retry regen after each completes
    minute_bucket = int(time.time()) // 60
    try:
        await enqueue_job(
            queue_name="content_generation",
            job_type="regen_image",
            payload={
                "draft_id": draft_id,
                "tenant_id": tenant_id,
                "option_idx": option_idx,
                "visual_prompt": visual_prompt,
                "telegram_chat_id": callback.message.chat.id if callback.message else None,
            },
            idempotency_key=f"{draft_id}:regen_image:{option_idx}:{minute_bucket}",
        )
    except Exception:
        logger.warning(
            "regen_image job already queued (duplicate tap)",
            extra={"draft_id": draft_id, "option_idx": option_idx},
        )
        await callback.answer("Already regenerating — please wait a moment.")
        return

    await callback.answer(f"Regenerating image #{option_number}...")
    if callback.message:
        await callback.message.reply(
            f"Generating a new image for option #{option_number}... I'll send it in a moment."
        )

