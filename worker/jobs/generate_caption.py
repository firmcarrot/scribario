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
    message["intent"]
    message.get("platform_targets", ["instagram"])

    logger.info(
        "Generating captions",
        extra={"request_id": request_id, "tenant_id": tenant_id},
    )

    # DEPRECATED: This handler is superseded by generate_content.
    # No jobs of type "generate_caption" should be enqueued in normal operation.
    logger.error(
        "generate_caption job type is deprecated — use generate_content instead",
        extra={"request_id": request_id, "tenant_id": tenant_id},
    )
    raise NotImplementedError(
        "generate_caption is a deprecated stub. Enqueue 'generate_content' jobs instead."
    )
