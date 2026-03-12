"""Pipeline orchestrator — coordinates the full content creation flow.

Flow: content_request → generate captions → generate images → store draft → send preview.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from pipeline.brand_voice import BrandProfile, FewShotExample
from pipeline.caption_gen import CaptionResult, generate_captions
from pipeline.image_gen import ImageGenerationService, ImageResult

logger = logging.getLogger(__name__)


@dataclass
class ContentDraft:
    """A fully generated content draft ready for preview."""

    id: str
    request_id: str
    tenant_id: str
    captions: list[CaptionResult]
    images: list[ImageResult]
    platform_targets: list[str]


async def generate_content(
    request_id: str,
    tenant_id: str,
    intent: str,
    platform_targets: list[str],
    profile: BrandProfile,
    examples: list[FewShotExample],
    image_service: ImageGenerationService | None = None,
) -> ContentDraft:
    """Orchestrate full content generation pipeline.

    Order: captions FIRST → extract visual prompts → generate images.
    This produces better brand alignment than image-first.

    Args:
        request_id: ID of the originating content_request.
        tenant_id: Tenant this content belongs to.
        intent: User's description of what to post.
        platform_targets: Platforms to post to.
        profile: Brand voice profile.
        examples: Few-shot examples for brand voice.
        image_service: Image generation service (uses default if None).

    Returns:
        ContentDraft with captions and images ready for preview.
    """
    if image_service is None:
        image_service = ImageGenerationService()

    draft_id = str(uuid.uuid4())

    logger.info(
        "Starting content generation",
        extra={"request_id": request_id, "tenant_id": tenant_id, "intent": intent[:50]},
    )

    # Step 1: Generate captions (includes visual prompts)
    captions = await generate_captions(
        intent=intent,
        profile=profile,
        examples=examples,
        platform_targets=platform_targets,
        num_options=3,
    )

    logger.info("Captions generated", extra={"count": len(captions)})

    # Step 2: Generate images from visual prompts
    visual_prompts = [cap.visual_prompt for cap in captions]
    images = await image_service.generate_batch(visual_prompts)

    logger.info("Images generated", extra={"count": len(images)})

    # Step 3: Build draft
    draft = ContentDraft(
        id=draft_id,
        request_id=request_id,
        tenant_id=tenant_id,
        captions=captions,
        images=images,
        platform_targets=platform_targets,
    )

    # NOTE: Storage and usage logging are handled by worker/jobs/generate_content.py.
    # This orchestrator is used for unit-testing the pipeline in isolation only.

    logger.info(
        "Content draft complete",
        extra={"draft_id": draft_id, "caption_count": len(captions), "image_count": len(images)},
    )

    return draft
