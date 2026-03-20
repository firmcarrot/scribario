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
from bot.services.telegram import build_preview_keyboard, build_video_preview_keyboard
from pipeline.brand_voice import (
    BrandProfile,
    load_brand_profile,
    load_few_shot_examples,
)
from pipeline.image_gen import ImageGenerationService
from pipeline.prompt_engine.asset_resolver import resolve_assets
from pipeline.prompt_engine.engine import ENGINE_COST_USD, PlanResult, generate_plan
from pipeline.prompt_engine.models import RefImageAssignment, RefSlotType, ScenePlan

logger = logging.getLogger(__name__)


async def _notify_failure(job_message: dict, text: str) -> None:
    """Send a failure notification to the user via Telegram."""
    chat_id = job_message.get("telegram_chat_id")
    if not chat_id:
        return

    bot = Bot(
        token=get_settings().telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception:
        logger.exception("Failed to send failure notification")
    finally:
        await bot.session.close()


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
        # Warn user that content will be generic
        telegram_chat_id = message.get("telegram_chat_id")
        if telegram_chat_id:
            bot = Bot(
                token=get_settings().telegram_bot_token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            )
            try:
                await bot.send_message(
                    chat_id=telegram_chat_id,
                    text=(
                        "Heads up: I don't have a brand profile for you yet, "
                        "so the content will be generic. Run /start to set up "
                        "your brand voice for better results."
                    ),
                )
            except Exception:
                logger.warning("Failed to send brand profile warning")
            finally:
                await bot.session.close()

    if not examples:
        examples = []

    # Step 1: Resolve assets (categorized reference photos + logo)
    assets = await resolve_assets(tenant_id, new_photo_paths=new_photo_storage_paths or None)

    # Step 2: Generate plan via Prompt Engine (replaces generate_captions)
    try:
        plan_result: PlanResult = await generate_plan(
            intent=intent,
            profile=profile,
            examples=examples,
            assets=assets,
            platform_targets=platform_targets,
        )
        plan = plan_result.plan

        # Logo presence validation: warn if logo available but not used in any scene
        if assets.logo_url:
            logo_in_any_scene = any(
                any(
                    r.slot_type == RefSlotType.LOGO_REFERENCE
                    for r in scene.start_frame.reference_images
                )
                for scene in plan.scenes
            )
            if not logo_in_any_scene:
                logger.warning(
                    "Logo available but not included in any scene's reference images",
                    extra={"request_id": request_id, "tenant_id": tenant_id},
                )
    except Exception:
        logger.exception("Prompt engine failed", extra={"request_id": request_id})
        await update_content_request_status(request_id, "failed")
        await _notify_failure(message, "Something went wrong generating your content. Please try again or rephrase your request.")
        raise

    # Calculate actual cost from token usage if available, else use flat estimate
    if plan_result.input_tokens and plan_result.output_tokens:
        from pipeline.cost_utils import compute_anthropic_cost
        engine_cost = compute_anthropic_cost(
            plan_result.model or "claude-sonnet-4-20250514",
            plan_result.input_tokens,
            plan_result.output_tokens,
        )
    else:
        engine_cost = ENGINE_COST_USD

    await log_usage_event(
        tenant_id=tenant_id,
        event_type="prompt_engine",
        provider="anthropic",
        cost_usd=engine_cost,
        metadata={"request_id": request_id, "format": plan.content_format, "scenes": len(plan.scenes)},
        request_id=request_id,
        input_tokens=plan_result.input_tokens,
        output_tokens=plan_result.output_tokens,
        model=plan_result.model,
    )

    # Step 3: Generate images from plan scenes — ALL IN PARALLEL
    # tenant_id passed to service for automatic usage logging
    image_service = ImageGenerationService(tenant_id=tenant_id)

    async def _generate_one(scene: ScenePlan) -> str:
        """Generate one image from a scene's start_frame. Returns URL or empty string."""
        frame = scene.start_frame
        ref_urls = RefImageAssignment.flat_urls(frame.reference_images) or None
        try:
            result = await image_service.generate(
                frame.prompt,
                reference_image_urls=ref_urls,
            )
            return result.url
        except Exception:
            logger.exception("Image generation failed for scene %d", scene.index)
            return ""

    images = await asyncio.gather(*[_generate_one(scene) for scene in plan.scenes])

    # Warn if ALL images failed
    successful_images = [url for url in images if url]
    if not successful_images and plan.scenes:
        logger.warning(
            "All image generations failed",
            extra={"request_id": request_id, "scene_count": len(plan.scenes)},
        )

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

    # If video generation was requested, generate inline (not a separate job)
    video_url: str | None = None
    if message.get("generate_video"):
        from pipeline.cost_utils import compute_anthropic_cost
        from pipeline.video_gen import VideoGenerationService
        from pipeline.video_prompt_gen import VIDEO_PROMPT_COST_USD, generate_video_prompt
        from worker.jobs.generate_video import update_draft_video_url

        video_aspect = message.get("video_aspect_ratio", "16:9")
        first_image_url = images[0] if images and images[0] else None

        try:
            vp_result = await generate_video_prompt(
                intent=intent,
                brand_profile=profile,
                visual_prompt=plan.scenes[0].start_frame.prompt if plan.scenes else None,
                aspect_ratio=video_aspect,
                reference_has_image=bool(first_image_url),
            )
            video_prompt = vp_result.text

            if vp_result.input_tokens and vp_result.output_tokens:
                vp_cost = compute_anthropic_cost(
                    vp_result.model, vp_result.input_tokens, vp_result.output_tokens
                )
            else:
                vp_cost = VIDEO_PROMPT_COST_USD

            await log_usage_event(
                tenant_id=tenant_id,
                event_type="video_prompt_generation",
                provider="anthropic",
                cost_usd=vp_cost,
                input_tokens=vp_result.input_tokens,
                output_tokens=vp_result.output_tokens,
                model=vp_result.model,
                metadata={"request_id": request_id, "prompt_len": len(video_prompt)},
            )
        except Exception as exc:
            logger.warning(
                "Video prompt gen failed, using plan start_frame prompt",
                extra={"error": str(exc)},
            )
            video_prompt = plan.scenes[0].start_frame.prompt if plan.scenes else intent

        try:
            gen_type = "REFERENCE_2_VIDEO" if first_image_url else "TEXT_2_VIDEO"
            video_service = VideoGenerationService(tenant_id=tenant_id)
            video_result = await video_service.generate(
                video_prompt,
                aspect_ratio=video_aspect,
                generation_type=gen_type,
                image_urls=[first_image_url] if first_image_url else None,
            )
            video_url = video_result.url
            await update_draft_video_url(draft_id, video_url)
            logger.info(
                "Inline video generation complete",
                extra={"draft_id": draft_id, "video_url": video_url},
            )
        except Exception:
            logger.exception(
                "Inline video generation failed, falling back to image-only preview",
                extra={"draft_id": draft_id},
            )
            video_url = None
            # Notify user that video failed but images are still available
            await _notify_failure(
                message,
                "Video generation failed, but I still have image options for you. "
                "Showing image preview instead.",
            )

    # --- Autopilot source handling ---
    is_autopilot = message.get("source") == "autopilot"
    autopilot_topic_id = message.get("autopilot_topic_id")
    autopilot_mode = message.get("autopilot_mode")
    warmup_remaining = message.get("warmup_posts_remaining", 0)
    auto_approve_at_str = message.get("auto_approve_at")

    if is_autopilot and autopilot_topic_id:
        from bot.db import get_supabase_client as _get_client

        _cl = _get_client()
        _cl.table("autopilot_topics").update({
            "draft_id": draft_id,
            "status": "previewing",
        }).eq("id", autopilot_topic_id).execute()

    # Increment post count AFTER successful generation (not before)
    from bot.services.budget import increment_post_count, decrement_video_credit
    await increment_post_count(tenant_id)
    if video_url:
        await decrement_video_credit(tenant_id)

    # Send preview to Telegram
    telegram_chat_id = message.get("telegram_chat_id")
    if telegram_chat_id:
        # For autopilot Smart Queue: build timeout notice for preview footer
        autopilot_notice: str | None = None
        if is_autopilot and auto_approve_at_str:
            timeout_mins = message.get("smart_queue_timeout_minutes", 120)
            hours = timeout_mins // 60
            autopilot_notice = f"\n\n⏰ Auto-posting in {hours} hour{'s' if hours != 1 else ''} unless you reject."

        await _send_preview(
            chat_id=telegram_chat_id,
            draft_id=draft_id,
            tenant_id=tenant_id,
            captions=plan.captions,
            image_urls=[url for url in images if url],
            platform_targets=platform_targets,
            video_url=video_url,
            autopilot_notice=autopilot_notice,
        )

        # For Full Autopilot (post-warmup): auto-approve immediately
        if is_autopilot and autopilot_mode == "full_autopilot" and (warmup_remaining or 0) <= 0:
            from bot.handlers.approval import approve_draft as _approve, approve_video_draft as _approve_video
            from aiogram import Bot as _Bot
            from aiogram.client.default import DefaultBotProperties as _Defaults
            from aiogram.enums import ParseMode as _PM

            try:
                if video_url:
                    await _approve_video(draft_id, option_idx=0, tenant_id=tenant_id)
                else:
                    await _approve(draft_id, option_idx=0, tenant_id=tenant_id)

                # Send FYI notification
                _bot = _Bot(
                    token=get_settings().telegram_bot_token,
                    default=_Defaults(parse_mode=_PM.HTML),
                )
                try:
                    caption_preview = plan.captions[0].get("text", "")[:100] if plan.captions else ""
                    await _bot.send_message(
                        chat_id=telegram_chat_id,
                        text=f"✅ <b>Autopilot posted:</b>\n{caption_preview}...",
                    )
                finally:
                    await _bot.session.close()

                if autopilot_topic_id:
                    from bot.db import update_autopilot_topic_status as _update_topic
                    await _update_topic(autopilot_topic_id, "posted", expected_status="previewing")

            except Exception:
                logger.exception("Autopilot auto-approve failed", extra={"draft_id": draft_id})
    else:
        logger.warning("No telegram_chat_id — can't send preview", extra={"draft_id": draft_id})


async def _send_preview(
    chat_id: int,
    draft_id: str,
    tenant_id: str,
    captions: list[dict],
    image_urls: list[str],
    platform_targets: list[str],
    video_url: str | None = None,
    autopilot_notice: str | None = None,
) -> None:
    """Send caption + image/video preview to Telegram with approval buttons.

    When video_url is present, sends video first, then caption options with
    video-specific approval buttons (no image buttons, no "Make Video").
    """

    bot = Bot(
        token=get_settings().telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    try:
        if video_url:
            keyboard = build_video_preview_keyboard(draft_id, num_options=len(captions))
        else:
            keyboard = build_preview_keyboard(draft_id, num_options=len(captions))
        sent = None

        try:
            if video_url:
                # Video preview: send video first, then caption options as text
                await bot.send_video(
                    chat_id=chat_id,
                    video=video_url,
                    caption="<b>Here's your video!</b> Choose a caption below.",
                    parse_mode=ParseMode.HTML,
                )

                lines = []
                for i, cap in enumerate(captions, 1):
                    cap_text = cap.get("text", "") if isinstance(cap, dict) else str(cap)
                    lines.append(f"<b>Option {i}:</b>\n{cap_text}\n")

                preview_text = "\n".join(lines)
                preview_text += (
                    f"\n<b>Posting to:</b> {', '.join(p.title() for p in platform_targets) if platform_targets else 'all connected platforms'}\n\n"
                    "<i>Tap Approve to post the video with your chosen caption, "
                    "Reject All to skip, or Regenerate for new options.</i>"
                )
                if autopilot_notice:
                    preview_text += autopilot_notice

                if len(preview_text) > 4000:
                    preview_text = preview_text[:3997] + "..."

                sent = await bot.send_message(
                    chat_id=chat_id, text=preview_text, reply_markup=keyboard
                )
            elif image_urls:
                for i, cap in enumerate(captions):
                    image_url = image_urls[i] if i < len(image_urls) else None
                    cap_text = cap.get("text", "") if isinstance(cap, dict) else str(cap)
                    caption_text = f"<b>Option {i + 1}:</b>\n{cap_text}"
                    # Telegram photo captions: 1024 bytes max (UTF-8)
                    if len(caption_text.encode("utf-8")) > 1024:
                        from bot.handlers.intake import truncate_telegram_caption
                        caption_text = truncate_telegram_caption(caption_text)

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
                if autopilot_notice:
                    footer += autopilot_notice
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
                if autopilot_notice:
                    preview_text += autopilot_notice

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
