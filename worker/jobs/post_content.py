"""Job handler — content posting via Postiz."""

from __future__ import annotations

import logging

from pipeline.posting import PostizClient

logger = logging.getLogger(__name__)


async def handle_post_content(message: dict) -> None:
    """Post approved content to target platforms via Postiz.

    Message format:
        {
            "id": "job-uuid",
            "type": "post_content",
            "tenant_id": "tenant-uuid",
            "draft_id": "draft-uuid",
            "caption": "final approved caption text",
            "image_urls": ["https://..."],
            "platforms": ["instagram", "facebook"],
            "idempotency_key": "hash(draft_id + post_content)"
        }
    """
    draft_id = message["draft_id"]
    caption = message["caption"]
    image_urls = message.get("image_urls", [])
    # If no platforms specified, post to all connected integrations
    platforms = message.get("platforms") or ([message["platform"]] if message.get("platform") else None)

    logger.info(
        "Posting content",
        extra={"draft_id": draft_id, "platforms": platforms},
    )

    # TODO: Check idempotency_key — skip if already posted
    # TODO: Load tenant's Postiz credentials from platform_connections

    client = PostizClient()
    results = await client.post(
        caption=caption,
        image_urls=image_urls,
        platforms=platforms or None,
    )

    for result in results:
        logger.info(
            "Posting result",
            extra={
                "platform": result.platform,
                "success": result.success,
                "url": result.platform_url,
            },
        )
        # TODO: Insert posting_result row
        # TODO: Update posting_job status

    # TODO: Send confirmation to user via Telegram
    # TODO: Log usage_event
