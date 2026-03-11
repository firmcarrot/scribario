"""Job handler — image generation."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def handle_generate_image(message: dict) -> None:
    """Generate an image for a content draft.

    Message format:
        {
            "id": "job-uuid",
            "type": "generate_image",
            "tenant_id": "tenant-uuid",
            "draft_id": "draft-uuid",
            "visual_prompt": "vibrant photo of ghost pepper hot sauce...",
            "aspect_ratio": "1:1",
            "idempotency_key": "hash(draft_id + generate_image + variant_index)"
        }
    """
    tenant_id = message["tenant_id"]
    draft_id = message["draft_id"]
    message["visual_prompt"]

    logger.info(
        "Generating image",
        extra={"draft_id": draft_id, "tenant_id": tenant_id},
    )

    # TODO: Check idempotency_key — skip if already completed
    # TODO: Call pipeline.image_gen.ImageGenerationService.generate
    # TODO: Upload image to Supabase Storage (private bucket, tenant-scoped)
    # TODO: Update content_drafts with image URL
    # TODO: Log usage_event for cost tracking
    # TODO: If all images for this draft are done, update status → 'generated'

    logger.info("Image generation complete", extra={"draft_id": draft_id})
