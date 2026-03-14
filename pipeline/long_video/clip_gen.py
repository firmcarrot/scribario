"""Video clip generation -- Veo 3.1 with frame pairs and fallback chain."""

from __future__ import annotations

import asyncio
import logging

from pipeline.long_video.models import SceneAssets
from pipeline.video_gen import VideoGenerationService

logger = logging.getLogger(__name__)

CLIP_COST_USD = 0.40  # Veo 3.1 Fast per clip
_SILENT_SUFFIX = " No music, no sound effects, no dialogue."
_MAX_CONCURRENT = 4


async def generate_scene_clip(
    assets: SceneAssets,
    video_prompt: str,
    video_service: VideoGenerationService,
    aspect_ratio: str = "16:9",
) -> SceneAssets:
    """Generate a video clip for a scene with 3-level fallback.

    Fallback chain (levels skipped if required frames are missing):
    1. FIRST_AND_LAST_FRAMES_2_VIDEO (start + end frames)
    2. REFERENCE_2_VIDEO (start frame only)
    3. TEXT_2_VIDEO (prompt only)

    Updates assets.video_clip_url and assets.cost_usd.
    """
    prompt = video_prompt + _SILENT_SUFFIX
    has_start = assets.start_frame_url is not None
    has_end = assets.end_frame_url is not None

    # Build ordered list of (generation_type, image_urls) to try
    attempts: list[tuple[str, list[str] | None]] = []

    if has_start and has_end:
        attempts.append((
            "FIRST_AND_LAST_FRAMES_2_VIDEO",
            [assets.start_frame_url, assets.end_frame_url],  # type: ignore[list-item]
        ))

    if has_start:
        attempts.append((
            "REFERENCE_2_VIDEO",
            [assets.start_frame_url],  # type: ignore[list-item]
        ))

    attempts.append(("TEXT_2_VIDEO", None))

    for gen_type, image_urls in attempts:
        try:
            result = await video_service.generate(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                generation_type=gen_type,
                image_urls=image_urls,
            )
            assets.video_clip_url = result.url
            assets.cost_usd += result.cost_usd
            logger.info(
                "Clip generated",
                extra={
                    "scene": assets.scene_index,
                    "gen_type": gen_type,
                    "cost": result.cost_usd,
                },
            )
            return assets
        except Exception:
            logger.warning(
                "Clip generation failed, trying next fallback",
                extra={"scene": assets.scene_index, "gen_type": gen_type},
                exc_info=True,
            )

    logger.error("All clip generation methods failed", extra={"scene": assets.scene_index})
    return assets


async def generate_all_clips(
    scene_assets: list[SceneAssets],
    video_prompts: list[str],
    video_service: VideoGenerationService | None = None,
    aspect_ratio: str = "16:9",
) -> list[SceneAssets]:
    """Generate clips for all scenes in parallel (semaphore-limited)."""
    if video_service is None:
        video_service = VideoGenerationService()

    sem = asyncio.Semaphore(_MAX_CONCURRENT)

    async def _gen(assets: SceneAssets, prompt: str) -> SceneAssets:
        async with sem:
            return await generate_scene_clip(assets, prompt, video_service, aspect_ratio)

    tasks = [
        asyncio.create_task(_gen(assets, prompt))
        for assets, prompt in zip(scene_assets, video_prompts)
    ]
    return list(await asyncio.gather(*tasks))
