"""Frame generation — Nano Banana 2 start+end frame pairs per scene."""

from __future__ import annotations

import asyncio
import logging

from pipeline.image_gen import ImageGenerationService
from pipeline.long_video.models import Scene, SceneAssets

logger = logging.getLogger(__name__)

FRAME_COST_USD = 0.04  # $0.04 per frame (Nano Banana 2 at 1K)

# Limit concurrent Kie.ai calls to avoid starving short-video pipeline
KIE_AI_SEMAPHORE = asyncio.Semaphore(4)


async def generate_scene_frames(
    scene: Scene,
    image_service: ImageGenerationService,
    aspect_ratio: str = "16:9",
) -> SceneAssets:
    """Generate start and end frames for a single scene.

    Returns SceneAssets with start_frame_url and end_frame_url.
    Cost: 2 * $0.04 = $0.08 per scene.
    """
    start_result, end_result = await asyncio.gather(
        image_service.generate(scene.start_frame_prompt, aspect_ratio),
        image_service.generate(scene.end_frame_prompt, aspect_ratio),
    )

    return SceneAssets(
        scene_index=scene.index,
        start_frame_url=start_result.url,
        end_frame_url=end_result.url,
        cost_usd=start_result.cost_usd + end_result.cost_usd,
    )


async def _generate_scene_frames_safe(
    scene: Scene,
    image_service: ImageGenerationService,
    aspect_ratio: str,
) -> SceneAssets:
    """Wrapper that catches errors and returns empty SceneAssets on failure."""
    try:
        async with KIE_AI_SEMAPHORE:
            return await generate_scene_frames(scene, image_service, aspect_ratio)
    except Exception:
        logger.warning(
            "Frame generation failed for scene %d, skipping",
            scene.index,
            exc_info=True,
        )
        return SceneAssets(scene_index=scene.index)


async def generate_all_frames(
    scenes: list[Scene],
    image_service: ImageGenerationService | None = None,
    aspect_ratio: str = "16:9",
) -> list[SceneAssets]:
    """Generate frame pairs for all scenes in parallel (semaphore-limited).

    Failed scenes get SceneAssets with None URLs (skipped in stitch).
    """
    if image_service is None:
        image_service = ImageGenerationService()

    tasks = [
        _generate_scene_frames_safe(scene, image_service, aspect_ratio)
        for scene in scenes
    ]
    results = await asyncio.gather(*tasks)
    return list(results)
