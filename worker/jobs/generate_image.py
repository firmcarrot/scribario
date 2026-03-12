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

    # DEPRECATED: This handler is superseded by generate_content.
    # No jobs of type "generate_image" should be enqueued in normal operation.
    logger.error(
        "generate_image job type is deprecated — use generate_content instead",
        extra={"draft_id": draft_id, "tenant_id": tenant_id},
    )
    raise NotImplementedError(
        "generate_image is a deprecated stub. Enqueue 'generate_content' jobs instead."
    )
