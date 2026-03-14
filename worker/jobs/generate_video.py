"""Job handler — video generation for a content draft."""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import get_settings
from bot.db import get_draft, log_usage_event
from pipeline.brand_voice import BrandProfile, load_brand_profile
from pipeline.video_gen import VideoGenerationService
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
        optimized_prompt = await generate_video_prompt(
            intent=prompt,
            brand_profile=profile,
            aspect_ratio=aspect_ratio,
            reference_has_image=bool(image_urls),
        )
        await log_usage_event(
            tenant_id=tenant_id,
            event_type="video_prompt_generation",
            provider="anthropic",
            cost_usd=VIDEO_PROMPT_COST_USD,
            metadata={"draft_id": draft_id, "prompt_len": len(optimized_prompt)},
        )
    except Exception as exc:
        logger.warning(
            "Video prompt gen failed in Make Video path, using raw prompt",
            extra={"error": str(exc)},
        )
        optimized_prompt = prompt

    # Generate video with optimized prompt
    service = VideoGenerationService()
    result = await service.generate(
        optimized_prompt,
        aspect_ratio=aspect_ratio,
        generation_type=generation_type,
        image_urls=image_urls if generation_type != "TEXT_2_VIDEO" else None,
    )

    # Log usage
    await log_usage_event(
        tenant_id=tenant_id,
        event_type="video_generation",
        provider=result.provider,
        cost_usd=result.cost_usd,
        metadata={
            "draft_id": draft_id,
            "prompt": prompt[:100],
            "generation_type": generation_type,
        },
    )

    # Store video URL on the draft
    await update_draft_video_url(draft_id, result.url)

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
            caption=_get_first_caption(draft),
        )
    else:
        logger.info(
            "No telegram_chat_id — skipping video preview",
            extra={"draft_id": draft_id},
        )


def _get_first_caption(draft: dict | None) -> str:
    """Extract the first caption text from a draft."""
    if not draft:
        return ""
    variants = draft.get("caption_variants") or []
    if variants:
        return variants[0].get("text", "")
    return ""


def _build_video_keyboard(draft_id: str) -> InlineKeyboardMarkup:
    """Build inline keyboard for video approval."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Approve Video",
                    callback_data=f"approve_video:{draft_id}",
                ),
                InlineKeyboardButton(
                    text="Reject Video",
                    callback_data=f"reject_video:{draft_id}",
                ),
            ],
        ]
    )


async def _send_video_preview(
    chat_id: int,
    draft_id: str,
    video_url: str,
    caption: str,
) -> None:
    """Send video preview to Telegram with approve/reject buttons."""
    settings = get_settings()
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    try:
        caption_text = f"<b>Video preview:</b>\n{caption}" if caption else "Video preview"
        if len(caption_text) > 1020:
            caption_text = caption_text[:1017] + "..."

        keyboard = _build_video_keyboard(draft_id)

        await bot.send_video(
            chat_id=chat_id,
            video=video_url,
            caption=caption_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
        logger.info("Video preview sent", extra={"draft_id": draft_id, "chat_id": chat_id})
    except Exception:
        logger.exception(
            "Failed to send video preview",
            extra={"draft_id": draft_id, "chat_id": chat_id},
        )
    finally:
        await bot.session.close()
