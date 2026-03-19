"""Top-level orchestrator for the long-form video generation pipeline."""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from bot.config import get_settings
from bot.db import log_usage_event
from pipeline.brand_voice import BrandProfile, load_brand_profile, load_few_shot_examples
from pipeline.cost_utils import compute_anthropic_cost
from pipeline.long_video.clip_gen import generate_all_clips
from pipeline.long_video.frame_gen import generate_all_frames
from pipeline.long_video.models import (
    LongVideoScript,
    SceneAssets,
    StitchSpec,
)
from pipeline.long_video.script_gen import SCRIPT_GEN_COST_USD, generate_script
from pipeline.long_video.sfx import generate_sfx_batch
from pipeline.long_video.stitcher import stitch
from pipeline.long_video.tts import TTS_COST_PER_SCENE, generate_voiceover
from pipeline.prompt_engine.models import GenerationPlan

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    project_id: str
    video_path: str
    duration_seconds: float
    total_cost_usd: float
    script: LongVideoScript
    scene_count: int
    scenes_completed: int
    captions: list[dict] = field(default_factory=list)


def _default_profile(tenant_id: str) -> BrandProfile:
    """Fallback brand profile when none exists in the database."""
    return BrandProfile(
        tenant_id=tenant_id,
        name="Brand",
        tone_words=["professional", "engaging"],
        audience_description="General audience",
        do_list=["Be clear and concise"],
        dont_list=["Don't be boring"],
    )


async def _notify(
    callback: Callable[[str, str], Awaitable[None]] | None,
    status: str,
    message: str,
) -> None:
    """Call status callback if provided."""
    if callback is not None:
        await callback(status, message)


async def run_pipeline(
    tenant_id: str,
    project_id: str,
    intent: str,
    aspect_ratio: str = "16:9",
    status_callback: Callable[[str, str], Awaitable[None]] | None = None,
    generation_plan: GenerationPlan | None = None,
) -> PipelineResult:
    """Run the full long-form video generation pipeline.

    Steps:
    1. Load brand profile (or use default)
    2. Generate script via Claude
    3. Get/create branded voice
    4. Generate voiceovers (sequential — timing matters)
    5. Generate frames (parallel)
    6. Generate clips + SFX (parallel with each other)
    7. Stitch final video
    8. Clean up temp files

    Raises:
        RuntimeError: If cost exceeds limit or no scenes survive filtering.
    """
    settings = get_settings()
    max_cost = settings.long_video_max_cost_usd
    running_cost = 0.0
    tmp_dir = f"/tmp/scribario/{project_id}"

    os.makedirs(tmp_dir, exist_ok=True)

    try:
        # --- 1. Load brand profile ---
        profile = await load_brand_profile(tenant_id)
        if profile is None:
            logger.info("No brand profile found for %s, using default", tenant_id)
            profile = _default_profile(tenant_id)

        # --- 2. Generate plan + script ---
        await _notify(status_callback, "scripting", "Generating video script...")
        if generation_plan is None:
            # Generate a plan so we always have captions + optimized prompts
            from pipeline.prompt_engine.asset_resolver import resolve_assets
            from pipeline.prompt_engine.engine import generate_plan

            examples = await load_few_shot_examples(tenant_id)
            assets = await resolve_assets(tenant_id)
            try:
                plan_result = await generate_plan(
                    intent=intent,
                    profile=profile,
                    examples=examples,
                    assets=assets,
                )
                generation_plan = plan_result.plan

                # Log plan generation cost (GAP 6)
                if plan_result.input_tokens and plan_result.output_tokens:
                    plan_cost = compute_anthropic_cost(
                        plan_result.model or "claude-sonnet-4-20250514",
                        plan_result.input_tokens,
                        plan_result.output_tokens,
                    )
                    running_cost += plan_cost
                    await log_usage_event(
                        tenant_id=tenant_id,
                        event_type="long_video_plan_gen",
                        provider="anthropic",
                        cost_usd=plan_cost,
                        input_tokens=plan_result.input_tokens,
                        output_tokens=plan_result.output_tokens,
                        model=plan_result.model,
                        metadata={"project_id": project_id},
                    )
            except Exception:
                logger.warning(
                    "Prompt engine failed, falling back to legacy script_gen",
                    exc_info=True,
                )

        if generation_plan is not None:
            from pipeline.prompt_engine.plan_adapter import plan_to_script
            script = plan_to_script(generation_plan)
            # Cost already logged as long_video_plan_gen above
        else:
            script = await generate_script(intent, profile)
            running_cost += SCRIPT_GEN_COST_USD
            await log_usage_event(
                tenant_id=tenant_id,
                event_type="script_gen",
                provider="anthropic",
                cost_usd=SCRIPT_GEN_COST_USD,
                metadata={"project_id": project_id, "title": script.title},
            )

        _check_cost(running_cost, max_cost)

        # --- 3. Get/create voice (pool-aware) ---
        from pipeline.long_video.voice_library import get_voice_from_pool_or_create
        voice_info = await get_voice_from_pool_or_create(
            tenant_id,
            script.voice_style,
            voice_pool=profile.voice_pool,
            tenant_name=profile.name,
        )

        # --- 4. Generate voiceovers (sequential) ---
        await _notify(status_callback, "tts", "Generating voiceovers...")
        tts_results: list[tuple[int, object]] = []  # (scene_index, TTSResult)

        for scene in script.scenes:
            try:
                tts_result = await generate_voiceover(
                    text=scene.voiceover_text,
                    voice_id=voice_info.voice_id,
                    output_dir=tmp_dir,
                )
                tts_results.append((scene.index, tts_result))
                running_cost += tts_result.cost_usd
            except Exception:
                logger.warning(
                    "TTS failed for scene %d, skipping", scene.index, exc_info=True
                )
                continue

            _check_cost(running_cost, max_cost)

        await log_usage_event(
            tenant_id=tenant_id,
            event_type="tts",
            provider="elevenlabs",
            cost_usd=TTS_COST_PER_SCENE * len(tts_results),
            metadata={"project_id": project_id, "scenes": len(tts_results)},
        )

        # Filter scenes to only those with successful TTS
        surviving_indices = {idx for idx, _ in tts_results}
        surviving_scenes = [s for s in script.scenes if s.index in surviving_indices]

        if not surviving_scenes:
            raise RuntimeError("No scenes survived TTS generation — cannot produce video")

        # Build index → tts_result lookup
        tts_by_index = {idx: result for idx, result in tts_results}

        # --- 5. Generate frames (parallel) ---
        # tenant_id passed to service for automatic per-call usage logging
        from pipeline.image_gen import ImageGenerationService

        frame_image_service = ImageGenerationService(tenant_id=tenant_id)
        await _notify(status_callback, "generating_frames", "Generating scene frames...")
        frame_assets = await generate_all_frames(
            surviving_scenes, image_service=frame_image_service, aspect_ratio=aspect_ratio
        )
        frame_cost = sum(fa.cost_usd for fa in frame_assets)
        running_cost += frame_cost

        _check_cost(running_cost, max_cost)

        # --- 6. Generate clips + SFX (parallel with each other) ---
        # tenant_id passed to service for automatic per-call usage logging
        from pipeline.video_gen import VideoGenerationService

        clip_video_service = VideoGenerationService(tenant_id=tenant_id)
        await _notify(status_callback, "generating_clips", "Generating video clips and SFX...")

        video_prompts = [s.visual_description for s in surviving_scenes]
        sfx_descriptions = [
            {"description": s.sfx_description, "duration_seconds": 3.0}
            for s in surviving_scenes
        ]

        # Snapshot cost before clip gen to avoid double-counting frame cost
        # (clip_gen mutates the same SceneAssets objects, accumulating cost)
        pre_clip_costs = {fa.scene_index: fa.cost_usd for fa in frame_assets}

        clip_assets, sfx_results = await asyncio.gather(
            generate_all_clips(
                frame_assets, video_prompts,
                video_service=clip_video_service, aspect_ratio=aspect_ratio,
            ),
            generate_sfx_batch(sfx_descriptions, output_dir=tmp_dir),
        )

        # Add only the clip cost delta (total - frame cost already counted)
        for ca in clip_assets:
            clip_only_cost = ca.cost_usd - pre_clip_costs.get(ca.scene_index, 0.0)
            running_cost += max(clip_only_cost, 0.0)
        for sr in sfx_results:
            if sr is not None:
                running_cost += sr.cost_usd

        # Log SFX cost (GAP 5)
        sfx_total_cost = sum(sr.cost_usd for sr in sfx_results if sr is not None)
        if sfx_total_cost > 0:
            try:
                await log_usage_event(
                    tenant_id=tenant_id,
                    event_type="sfx_generation",
                    provider="elevenlabs",
                    cost_usd=sfx_total_cost,
                    metadata={
                        "project_id": project_id,
                        "clips": sum(1 for sr in sfx_results if sr is not None),
                    },
                )
            except Exception:
                logger.exception("Failed to log SFX cost")

        _check_cost(running_cost, max_cost)

        # --- 7. Filter to scenes with BOTH clip AND voiceover ---
        stitchable: list[tuple[SceneAssets, object, object | None]] = []
        for i, ca in enumerate(clip_assets):
            if ca.video_clip_url is None:
                logger.warning("Scene %d has no clip, skipping from stitch", ca.scene_index)
                continue
            tts_r = tts_by_index.get(ca.scene_index)
            if tts_r is None:
                continue
            sfx_r = sfx_results[i] if i < len(sfx_results) else None
            stitchable.append((ca, tts_r, sfx_r))

        if not stitchable:
            raise RuntimeError("No scenes have both clip and voiceover — cannot stitch")

        # --- 8. Stitch ---
        await _notify(status_callback, "stitching", "Stitching final video...")

        spec = StitchSpec(
            project_id=project_id,
            scene_clips=[ca.video_clip_url for ca, _, _ in stitchable],
            scene_voiceovers=[tts_r.audio_url for _, tts_r, _ in stitchable],
            aspect_ratio=aspect_ratio,
            scene_sfx=[
                sfx_r.audio_path for _, _, sfx_r in stitchable if sfx_r is not None
            ],
        )

        stitch_result = await stitch(spec)

        # Copy final video out of tmp_dir so it survives cleanup.
        # Caller is responsible for deleting this file after upload.
        output_dir = f"/tmp/scribario-output"
        os.makedirs(output_dir, exist_ok=True)
        final_path = os.path.join(output_dir, f"{project_id}.mp4")
        shutil.copy2(stitch_result.output_path, final_path)

        return PipelineResult(
            project_id=project_id,
            video_path=final_path,
            duration_seconds=stitch_result.duration_seconds,
            total_cost_usd=running_cost,
            script=script,
            scene_count=script.total_scenes,
            scenes_completed=len(stitchable),
            captions=generation_plan.captions if generation_plan else [],
        )

    finally:
        # Clean up temp dir (intermediate assets only — final is copied out)
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)


def _check_cost(running_cost: float, max_cost: float) -> None:
    """Abort if cost exceeds the configured limit."""
    if running_cost > max_cost:
        raise RuntimeError(
            f"Cost limit exceeded: ${running_cost:.2f} > ${max_cost:.2f}. "
            f"Pipeline aborted to prevent overspend."
        )
