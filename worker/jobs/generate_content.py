"""Job handler — full content generation (captions + images).

This is the main generation job — orchestrates caption gen then image gen.
"""

from __future__ import annotations

import logging

from bot.db import (
    create_content_draft,
    log_usage_event,
    update_content_request_status,
)
from pipeline.brand_voice import (
    BrandProfile,
    FewShotExample,
    load_brand_profile,
    load_few_shot_examples,
)
from pipeline.caption_gen import generate_captions
from pipeline.image_gen import ImageGenerationService

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
    platform_targets = message.get("platform_targets", ["instagram"])

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

    # Step 1: Generate captions (includes visual prompts)
    captions = await generate_captions(
        intent=intent,
        profile=profile,
        examples=examples,
        platform_targets=platform_targets,
        num_options=3,
    )

    # Log caption generation cost
    await log_usage_event(
        tenant_id=tenant_id,
        event_type="caption_generation",
        provider="anthropic",
        cost_usd=0.02,  # Approximate per-request cost
        metadata={"request_id": request_id, "caption_count": len(captions)},
    )

    # Step 2: Generate images from visual prompts
    image_service = ImageGenerationService()
    images = []
    for caption in captions:
        try:
            result = await image_service.generate(caption.visual_prompt)
            images.append(result.url)

            await log_usage_event(
                tenant_id=tenant_id,
                event_type="image_generation",
                provider=result.provider,
                cost_usd=result.cost_usd,
                metadata={"request_id": request_id, "prompt": caption.visual_prompt[:100]},
            )
        except Exception:
            logger.exception("Image generation failed for one variant")
            images.append("")  # Placeholder — draft can still work with partial images

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

    logger.info(
        "Content generation complete",
        extra={
            "request_id": request_id,
            "draft_id": draft["id"],
            "caption_count": len(captions),
            "image_count": len([u for u in images if u]),
        },
    )

    # TODO: Send preview to Telegram user
    # This requires the bot instance — either:
    # 1. Worker sends via Telegram API directly (needs bot token)
    # 2. Worker enqueues a "send_preview" job that the bot picks up
    # For now, the draft is created — preview sending will be wired in Step 2 completion
