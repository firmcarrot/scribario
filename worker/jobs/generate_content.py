"""Job handler — full content generation (captions + images).

This is the main generation job — orchestrates caption gen then image gen,
then sends the preview back to the user via Telegram.
"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import get_settings
from bot.db import (
    create_approval_request,
    create_content_draft,
    get_default_reference_photos,
    log_usage_event,
    update_content_request_status,
    update_draft_status,
)
from bot.services.storage import get_signed_urls_for_generation
from bot.services.telegram import build_preview_keyboard
from pipeline.brand_voice import (
    BrandProfile,
    load_brand_profile,
    load_few_shot_examples,
)
from pipeline.caption_gen import generate_captions
from pipeline.image_gen import ImageGenerationService, build_image_input_array

logger = logging.getLogger(__name__)


async def handle_generate_content(message: dict) -> None:
    """Generate captions + images for a content request.

    Message format:
        {
            "request_id": "uuid",
            "tenant_id": "uuid",
            "intent": "post about our new ghost pepper sauce",
            "platform_targets": ["instagram", "facebook"],
        }
    """
    request_id = message["request_id"]
    tenant_id = message["tenant_id"]
    intent = message["intent"]
    platform_targets: list[str] = message.get("platform_targets") or []
    new_photo_storage_paths: list[str] = message.get("new_photo_storage_paths", [])
    style_override: str | None = message.get("style_override")

    logger.info(
        "Starting content generation",
        extra={"request_id": request_id, "tenant_id": tenant_id},
    )

    # Update request status
    await update_content_request_status(request_id, "generating")

    # Load brand context
    profile = await load_brand_profile(tenant_id)
    examples = await load_few_shot_examples(tenant_id)

    # Use defaults if no profile found yet
    if not profile:
        logger.warning("No brand profile found, using defaults", extra={"tenant_id": tenant_id})
        profile = BrandProfile(
            tenant_id=tenant_id,
            name="Brand",
            tone_words=["professional", "engaging"],
            audience_description="General audience",
            do_list=[],
            dont_list=[],
        )

    if not examples:
        examples = []

    # Resolve style: job payload style_override takes priority, then brand default
    effective_style = style_override or profile.default_image_style

    # Step 1: Generate captions (includes visual prompts)
    captions = await generate_captions(
        intent=intent,
        profile=profile,
        examples=examples,
        platform_targets=platform_targets,
        num_options=3,
        style=effective_style,
    )

    # Log caption generation cost
    await log_usage_event(
        tenant_id=tenant_id,
        event_type="caption_generation",
        provider="anthropic",
        cost_usd=0.02,  # Approximate per-request cost
        metadata={"request_id": request_id, "caption_count": len(captions)},
    )

    # Step 2: Build reference image array from saved defaults + new photos
    default_refs = await get_default_reference_photos(tenant_id)
    default_paths = [r["storage_path"] for r in default_refs]

    # Generate signed URLs for all reference photos (fresh, 600s TTL)
    new_signed = get_signed_urls_for_generation(new_photo_storage_paths) if new_photo_storage_paths else []
    default_signed = get_signed_urls_for_generation(default_paths) if default_paths else []

    reference_urls, truncated = build_image_input_array(
        new_photo_urls=new_signed,
        default_ref_urls=default_signed,
        return_truncated=True,
    )

    if truncated:
        logger.warning(
            "Default reference photos truncated to fit 14-image limit",
            extra={"tenant_id": tenant_id, "default_count": len(default_paths)},
        )

    # Step 3: Generate images from visual prompts — ALL IN PARALLEL
    image_service = ImageGenerationService()

    async def _generate_one(caption_obj: object) -> str:
        """Generate one image and log usage. Returns URL or empty string on failure."""
        try:
            result = await image_service.generate(
                caption_obj.visual_prompt,
                reference_image_urls=reference_urls if reference_urls else None,
            )
            await log_usage_event(
                tenant_id=tenant_id,
                event_type="image_generation",
                provider=result.provider,
                cost_usd=result.cost_usd,
                metadata={"request_id": request_id, "prompt": caption_obj.visual_prompt[:100]},
            )
            return result.url
        except Exception:
            logger.exception("Image generation failed for one variant")
            return ""

    images = await asyncio.gather(*[_generate_one(cap) for cap in captions])

    # Step 3: Create draft in database
    caption_variants = [
        {"text": c.text, "visual_prompt": c.visual_prompt} for c in captions
    ]

    draft = await create_content_draft(
        request_id=request_id,
        tenant_id=tenant_id,
        caption_variants=caption_variants,
        image_urls=[url for url in images if url],
    )

    # Update request status
    await update_content_request_status(request_id, "preview_ready")

    draft_id = draft["id"]

    logger.info(
        "Content generation complete",
        extra={
            "request_id": request_id,
            "draft_id": draft_id,
            "caption_count": len(captions),
            "image_count": len([u for u in images if u]),
        },
    )

    # Send preview to Telegram
    telegram_chat_id = message.get("telegram_chat_id")
    if telegram_chat_id:
        await _send_preview(
            chat_id=telegram_chat_id,
            draft_id=draft_id,
            tenant_id=tenant_id,
            captions=captions,
            image_urls=[url for url in images if url],
            platform_targets=platform_targets,
        )
    else:
        logger.warning("No telegram_chat_id — can't send preview", extra={"draft_id": draft_id})


async def _send_preview(
    chat_id: int,
    draft_id: str,
    tenant_id: str,
    captions: list,
    image_urls: list[str],
    platform_targets: list[str],
) -> None:
    """Send caption + image preview to Telegram with approval buttons."""

    bot = Bot(
        token=get_settings().telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    try:
        keyboard = build_preview_keyboard(draft_id, num_options=len(captions))
        sent = None

        try:
            # If we have images, send each option as a photo with caption
            if image_urls:
                for i, cap in enumerate(captions):
                    image_url = image_urls[i] if i < len(image_urls) else None
                    caption_text = (
                        f"<b>Option {i + 1}:</b>\n{cap.text}"
                    )
                    # Telegram photo captions max 1024 chars
                    if len(caption_text) > 1020:
                        caption_text = caption_text[:1017] + "..."

                    if image_url:
                        await bot.send_photo(
                            chat_id=chat_id,
                            photo=image_url,
                            caption=caption_text,
                            parse_mode=ParseMode.HTML,
                        )
                    else:
                        await bot.send_message(chat_id=chat_id, text=caption_text)

                # Send the action buttons as a separate message
                footer = (
                    f"<b>Posting to:</b> {', '.join(p.title() for p in platform_targets) if platform_targets else 'all connected platforms'}\n\n"
                    "<i>Tap Approve to post the option you like, Reject All to skip, "
                    "or Regenerate for new options.</i>"
                )
                sent = await bot.send_message(
                    chat_id=chat_id, text=footer, reply_markup=keyboard
                )
            else:
                # No images — text-only preview
                lines = ["<b>Here are your caption options:</b>\n"]
                for i, cap in enumerate(captions, 1):
                    lines.append(f"<b>Option {i}:</b>\n{cap.text}\n")

                preview_text = "\n".join(lines)
                preview_text += (
                    f"\n<b>Posting to:</b> {', '.join(p.title() for p in platform_targets) if platform_targets else 'all connected platforms'}\n\n"
                    "<i>Tap Approve to post, Reject All to skip, or Regenerate for new options.</i>"
                )

                if len(preview_text) > 4000:
                    preview_text = preview_text[:3997] + "..."

                sent = await bot.send_message(
                    chat_id=chat_id, text=preview_text, reply_markup=keyboard
                )
        except Exception:
            logger.exception("Failed to send Telegram preview", extra={"draft_id": draft_id})

        # Always update DB state — even if Telegram send partially failed
        if sent:
            await create_approval_request(
                draft_id=draft_id,
                tenant_id=tenant_id,
                telegram_message_id=sent.message_id,
                telegram_chat_id=chat_id,
            )
            await update_draft_status(draft_id, "previewing")
            logger.info("Preview sent", extra={"draft_id": draft_id, "chat_id": chat_id})
        else:
            # Telegram failed — mark draft so it can be retried
            logger.error("Preview send failed — draft stays in generated state", extra={"draft_id": draft_id})

    finally:
        await bot.session.close()
