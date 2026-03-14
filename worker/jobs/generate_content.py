"""Job handler — full content generation via Prompt Engine.

Orchestrates: Prompt Engine → image gen → draft creation → Telegram preview.
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
    log_usage_event,
    update_content_request_status,
    update_draft_status,
)
from bot.services.telegram import build_preview_keyboard
from pipeline.brand_voice import (
    BrandProfile,
    load_brand_profile,
    load_few_shot_examples,
)
from pipeline.image_gen import ImageGenerationService
from pipeline.prompt_engine.asset_resolver import resolve_assets
from pipeline.prompt_engine.engine import ENGINE_COST_USD, generate_plan
from pipeline.prompt_engine.models import RefImageAssignment, ScenePlan

logger = logging.getLogger(__name__)


async def handle_generate_content(message: dict) -> None:
    """Generate content for a request using the Prompt Engine.

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

    logger.info(
        "Starting content generation",
        extra={"request_id": request_id, "tenant_id": tenant_id},
    )

    await update_content_request_status(request_id, "generating")

    # Load brand context
    profile = await load_brand_profile(tenant_id)
    examples = await load_few_shot_examples(tenant_id)

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

    # Step 1: Resolve assets (categorized reference photos + logo)
    assets = await resolve_assets(tenant_id, new_photo_paths=new_photo_storage_paths or None)

    # Step 2: Generate plan via Prompt Engine (replaces generate_captions)
    try:
        plan = await generate_plan(
            intent=intent,
            profile=profile,
            examples=examples,
            assets=assets,
            platform_targets=platform_targets,
        )
    except Exception:
        logger.exception("Prompt engine failed", extra={"request_id": request_id})
        await update_content_request_status(request_id, "failed")
        raise

    await log_usage_event(
        tenant_id=tenant_id,
        event_type="prompt_engine",
        provider="anthropic",
        cost_usd=ENGINE_COST_USD,
        metadata={"request_id": request_id, "format": plan.content_format, "scenes": len(plan.scenes)},
    )

    # Step 3: Generate images from plan scenes — ALL IN PARALLEL
    image_service = ImageGenerationService()

    async def _generate_one(scene: ScenePlan) -> str:
        """Generate one image from a scene's start_frame. Returns URL or empty string."""
        frame = scene.start_frame
        ref_urls = RefImageAssignment.flat_urls(frame.reference_images) or None
        try:
            result = await image_service.generate(
                frame.prompt,
                reference_image_urls=ref_urls,
            )
            await log_usage_event(
                tenant_id=tenant_id,
                event_type="image_generation",
                provider=result.provider,
                cost_usd=result.cost_usd,
                metadata={"request_id": request_id, "prompt": frame.prompt[:100]},
            )
            return result.url
        except Exception:
            logger.exception("Image generation failed for scene %d", scene.index)
            return ""

    images = await asyncio.gather(*[_generate_one(scene) for scene in plan.scenes])

    # Step 4: Create draft in database (captions come from plan directly)
    draft = await create_content_draft(
        request_id=request_id,
        tenant_id=tenant_id,
        caption_variants=plan.captions,
        image_urls=[url for url in images if url],
    )

    await update_content_request_status(request_id, "preview_ready")

    draft_id = draft["id"]

    logger.info(
        "Content generation complete",
        extra={
            "request_id": request_id,
            "draft_id": draft_id,
            "format": plan.content_format,
            "scene_count": len(plan.scenes),
            "image_count": len([u for u in images if u]),
        },
    )

    # If video generation was requested, enqueue the video job
    if message.get("generate_video"):
        from bot.db import enqueue_job
        from pipeline.video_prompt_gen import VIDEO_PROMPT_COST_USD, generate_video_prompt

        video_aspect = message.get("video_aspect_ratio", "16:9")
        first_image_url = images[0] if images and images[0] else None

        try:
            video_prompt = await generate_video_prompt(
                intent=intent,
                brand_profile=profile,
                visual_prompt=plan.scenes[0].start_frame.prompt if plan.scenes else None,
                aspect_ratio=video_aspect,
                reference_has_image=bool(first_image_url),
            )
            await log_usage_event(
                tenant_id=tenant_id,
                event_type="video_prompt_generation",
                provider="anthropic",
                cost_usd=VIDEO_PROMPT_COST_USD,
                metadata={"request_id": request_id, "prompt_len": len(video_prompt)},
            )
        except Exception as exc:
            logger.warning(
                "Video prompt gen failed, using plan start_frame prompt",
                extra={"error": str(exc)},
            )
            video_prompt = plan.scenes[0].start_frame.prompt if plan.scenes else intent

        await enqueue_job(
            queue_name="content_generation",
            job_type="generate_video",
            payload={
                "draft_id": draft_id,
                "tenant_id": tenant_id,
                "prompt": video_prompt,
                "aspect_ratio": video_aspect,
                "generation_type": "REFERENCE_2_VIDEO" if first_image_url else "TEXT_2_VIDEO",
                "image_urls": [first_image_url] if first_image_url else None,
                "telegram_chat_id": message.get("telegram_chat_id"),
            },
            idempotency_key=f"{request_id}:generate_video",
        )
        logger.info("Video generation job enqueued", extra={"draft_id": draft_id})

    # Send preview to Telegram
    telegram_chat_id = message.get("telegram_chat_id")
    if telegram_chat_id:
        await _send_preview(
            chat_id=telegram_chat_id,
            draft_id=draft_id,
            tenant_id=tenant_id,
            captions=plan.captions,
            image_urls=[url for url in images if url],
            platform_targets=platform_targets,
        )
    else:
        logger.warning("No telegram_chat_id — can't send preview", extra={"draft_id": draft_id})


async def _send_preview(
    chat_id: int,
    draft_id: str,
    tenant_id: str,
    captions: list[dict],
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
            if image_urls:
                for i, cap in enumerate(captions):
                    image_url = image_urls[i] if i < len(image_urls) else None
                    cap_text = cap.get("text", "") if isinstance(cap, dict) else str(cap)
                    caption_text = f"<b>Option {i + 1}:</b>\n{cap_text}"
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

                footer = (
                    f"<b>Posting to:</b> {', '.join(p.title() for p in platform_targets) if platform_targets else 'all connected platforms'}\n\n"
                    "<i>Tap Approve to post the option you like, Reject All to skip, "
                    "or Regenerate for new options.</i>"
                )
                sent = await bot.send_message(
                    chat_id=chat_id, text=footer, reply_markup=keyboard
                )
            else:
                lines = ["<b>Here are your caption options:</b>\n"]
                for i, cap in enumerate(captions, 1):
                    cap_text = cap.get("text", "") if isinstance(cap, dict) else str(cap)
                    lines.append(f"<b>Option {i}:</b>\n{cap_text}\n")

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
            logger.error("Preview send failed — draft stays in generated state", extra={"draft_id": draft_id})

    finally:
        await bot.session.close()
