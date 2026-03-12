"""Job handler — image-only regeneration for a single draft option."""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import get_settings
from bot.db import get_supabase_client, log_usage_event
from pipeline.image_gen import ImageGenerationService

logger = logging.getLogger(__name__)


async def handle_regen_image_job(message: dict) -> None:
    """Regenerate the image for one draft option, keeping the caption.

    Message format:
        {
            "draft_id": "uuid",
            "tenant_id": "uuid",
            "option_idx": 0,           # 0-indexed
            "visual_prompt": "...",
            "telegram_chat_id": 12345  # optional
        }
    """
    draft_id = message["draft_id"]
    tenant_id = message["tenant_id"]
    option_idx = message["option_idx"]
    visual_prompt = message["visual_prompt"]
    telegram_chat_id = message.get("telegram_chat_id")

    logger.info(
        "Regen image job started",
        extra={"draft_id": draft_id, "option_idx": option_idx, "tenant_id": tenant_id},
    )

    # 1. Generate the new image
    image_service = ImageGenerationService()
    result = await image_service.generate(visual_prompt)

    await log_usage_event(
        tenant_id=tenant_id,
        event_type="image_generation",
        provider=result.provider,
        cost_usd=result.cost_usd,
        metadata={"draft_id": draft_id, "option_idx": option_idx, "prompt": visual_prompt[:100]},
    )

    # 2. Load current draft and replace image_urls[option_idx]
    client = get_supabase_client()
    draft_result = (
        client.table("content_drafts")
        .select("image_urls, caption_variants")
        .eq("id", draft_id)
        .limit(1)
        .execute()
    )
    if not draft_result.data:
        logger.error("Draft not found for regen_image", extra={"draft_id": draft_id})
        return

    draft = draft_result.data[0]
    image_urls: list[str] = list(draft.get("image_urls") or [])
    caption_variants: list[dict] = draft.get("caption_variants") or []

    # Ensure list is long enough
    while len(image_urls) <= option_idx:
        image_urls.append("")
    image_urls[option_idx] = result.url

    client.table("content_drafts").update({"image_urls": image_urls}).eq(
        "id", draft_id
    ).execute()

    logger.info(
        "Draft image updated",
        extra={"draft_id": draft_id, "option_idx": option_idx, "new_url": result.url},
    )

    # 3. Send updated image preview to Telegram
    if not telegram_chat_id:
        logger.info("No telegram_chat_id — skipping preview send", extra={"draft_id": draft_id})
        return

    caption_text = ""
    if option_idx < len(caption_variants):
        raw = caption_variants[option_idx].get("text", "")
        caption_text = f"<b>Option {option_idx + 1} — new image:</b>\n{raw}"
        if len(caption_text) > 1020:
            caption_text = caption_text[:1017] + "..."

    from bot.services.telegram import build_preview_keyboard
    keyboard = build_preview_keyboard(draft_id, num_options=len(caption_variants))

    settings = get_settings()
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        await bot.send_photo(
            chat_id=telegram_chat_id,
            photo=result.url,
            caption=caption_text or f"Option {option_idx + 1} — new image",
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
    except Exception:
        logger.exception(
            "Failed to send regen image preview",
            extra={"draft_id": draft_id, "chat_id": telegram_chat_id},
        )
    finally:
        await bot.session.close()
