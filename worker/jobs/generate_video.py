"""Job handler — video generation for a content draft."""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.config import get_settings
from bot.db import create_approval_request, get_draft, log_usage_event, update_draft_status
from bot.services.telegram import build_video_preview_keyboard
from pipeline.brand_voice import BrandProfile, load_brand_profile
from pipeline.video_gen import VideoGenerationService
from pipeline.cost_utils import compute_anthropic_cost
from pipeline.video_prompt_gen import VIDEO_PROMPT_COST_USD, generate_video_prompt

logger = logging.getLogger(__name__)


async def update_draft_video_url(draft_id: str, video_url: str) -> None:
    """Update the video_url column on a content draft."""
    from bot.db import get_supabase_client

    client = get_supabase_client()
    client.table("content_drafts").update({"video_url": video_url}).eq(
        "id", draft_id
    ).execute()


async def handle_generate_video(message: dict) -> None:
    """Generate a video for a content draft.

    Message format:
        {
            "draft_id": "uuid",
            "tenant_id": "uuid",
            "prompt": "video description",
            "aspect_ratio": "16:9" | "9:16",
            "generation_type": "TEXT_2_VIDEO" | "REFERENCE_2_VIDEO",
            "image_urls": ["..."],          # for REFERENCE_2_VIDEO
            "telegram_chat_id": 12345,      # optional
        }
    """
    draft_id = message["draft_id"]
    tenant_id = message["tenant_id"]
    prompt = message["prompt"]
    aspect_ratio = message.get("aspect_ratio", "16:9")
    generation_type = message.get("generation_type", "TEXT_2_VIDEO")
    image_urls = message.get("image_urls")
    telegram_chat_id = message.get("telegram_chat_id")

    logger.info(
        "Video generation started",
        extra={
            "draft_id": draft_id,
            "tenant_id": tenant_id,
            "generation_type": generation_type,
        },
    )

    # Load brand profile for video prompt optimization
    profile = await load_brand_profile(tenant_id)
    if not profile:
        logger.warning(
            "No brand profile for video prompt gen, using defaults",
            extra={"tenant_id": tenant_id},
        )
        profile = BrandProfile(
            tenant_id=tenant_id,
            name="Brand",
            tone_words=["professional", "engaging"],
            audience_description="General audience",
            do_list=[],
            dont_list=[],
        )

    # Optimize prompt via Claude (falls back to raw prompt on failure)
    try:
        vp_result = await generate_video_prompt(
            intent=prompt,
            brand_profile=profile,
            aspect_ratio=aspect_ratio,
            reference_has_image=bool(image_urls),
        )
        optimized_prompt = vp_result.text

        # Log with real token cost if available, else fallback
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
            metadata={"draft_id": draft_id, "prompt_len": len(optimized_prompt)},
        )
    except Exception as exc:
        logger.warning(
            "Video prompt gen failed in Make Video path, using raw prompt",
            extra={"error": str(exc)},
        )
        optimized_prompt = prompt

    # Generate video with optimized prompt
    # tenant_id passed to service for automatic usage logging
    service = VideoGenerationService(tenant_id=tenant_id)
    result = await service.generate(
        optimized_prompt,
        aspect_ratio=aspect_ratio,
        generation_type=generation_type,
        image_urls=image_urls if generation_type != "TEXT_2_VIDEO" else None,
    )

    # Store video URL on the draft
    await update_draft_video_url(draft_id, result.url)

    # Deduct video credit AFTER successful generation
    from bot.services.budget import decrement_video_credit
    await decrement_video_credit(tenant_id)

    logger.info(
        "Video generation complete",
        extra={"draft_id": draft_id, "video_url": result.url},
    )

    # Send preview to Telegram
    if telegram_chat_id:
        draft = await get_draft(draft_id)
        await _send_video_preview(
            chat_id=telegram_chat_id,
            draft_id=draft_id,
            video_url=result.url,
            draft=draft,
            tenant_id=tenant_id,
        )
    else:
        logger.info(
            "No telegram_chat_id — skipping video preview",
            extra={"draft_id": draft_id},
        )


async def _send_video_preview(
    chat_id: int,
    draft_id: str,
    video_url: str,
    draft: dict | None,
    tenant_id: str | None = None,
) -> None:
    """Send video preview to Telegram with all caption options + approve buttons."""
    settings = get_settings()
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    sent = None
    try:
        # Send the video
        await bot.send_video(
            chat_id=chat_id,
            video=video_url,
            caption="<b>Here's your video!</b> Choose a caption below.",
            parse_mode=ParseMode.HTML,
        )

        # Build caption options text
        caption_variants = (draft or {}).get("caption_variants") or []
        num_options = len(caption_variants)

        if caption_variants:
            lines = []
            for i, cap in enumerate(caption_variants, 1):
                cap_text = cap.get("text", "") if isinstance(cap, dict) else str(cap)
                lines.append(f"<b>Option {i}:</b>\n{cap_text}\n")

            preview_text = "\n".join(lines)
            preview_text += (
                "\n<i>Tap Approve to post the video with your chosen caption, "
                "Reject All to skip, or Regenerate for new options.</i>"
            )

            if len(preview_text) > 4000:
                preview_text = preview_text[:3997] + "..."
        else:
            preview_text = "<i>No captions available. Tap Approve to post or Reject to skip.</i>"
            num_options = 1

        keyboard = build_video_preview_keyboard(draft_id, num_options=num_options)

        sent = await bot.send_message(
            chat_id=chat_id,
            text=preview_text,
            reply_markup=keyboard,
        )
    except Exception:
        logger.exception(
            "Failed to send video preview",
            extra={"draft_id": draft_id, "chat_id": chat_id},
        )

    if sent:
        _tenant_id = tenant_id or (draft or {}).get("tenant_id", "")
        await create_approval_request(
            draft_id=draft_id,
            tenant_id=_tenant_id,
            telegram_message_id=sent.message_id,
            telegram_chat_id=chat_id,
        )
        await update_draft_status(draft_id, "previewing")
        logger.info("Video preview sent", extra={"draft_id": draft_id, "chat_id": chat_id})
    else:
        logger.error(
            "Video preview send failed — draft stays in generated state",
            extra={"draft_id": draft_id},
        )

    await bot.session.close()
