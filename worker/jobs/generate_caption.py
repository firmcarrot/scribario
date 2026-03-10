"""Job handler — caption generation."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def handle_generate_caption(message: dict) -> None:
    """Generate captions for a content request.

    Message format:
        {
            "id": "job-uuid",
            "type": "generate_caption",
            "tenant_id": "tenant-uuid",
            "request_id": "request-uuid",
            "intent": "post about our new ghost pepper sauce",
            "platform_targets": ["instagram", "facebook"],
            "idempotency_key": "hash(request_id + generate_caption)"
        }
    """
    tenant_id = message["tenant_id"]
    request_id = message["request_id"]
    intent = message["intent"]
    platform_targets = message.get("platform_targets", ["instagram"])

    logger.info(
        "Generating captions",
        extra={"request_id": request_id, "tenant_id": tenant_id},
    )

    # TODO: Check idempotency_key — skip if already completed
    # TODO: Load brand profile + few-shot examples
    # TODO: Call pipeline.caption_gen.generate_captions
    # TODO: Store results in content_drafts table
    # TODO: Log usage_event for cost tracking
    # TODO: Enqueue generate_image jobs for each caption's visual_prompt

    logger.info("Caption generation complete", extra={"request_id": request_id})
