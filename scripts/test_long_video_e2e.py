#!/usr/bin/env python3
"""End-to-end integration test for the long-form video pipeline.

Runs each stage with REAL API calls. Costs ~$2-3 per run.
Usage: python3 scripts/test_long_video_e2e.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("e2e")

TENANT_ID = "52590da5-bc80-4161-ac13-62e9bcd75424"  # Mondo Shrimp
PROJECT_ID = f"e2e-test-{int(time.time())}"
INTENT = "Showcase our signature spicy shrimp sauce — the most interesting sauce in the world"


async def test_step_1_script_gen():
    """Step 1: Generate script via Claude."""
    logger.info("=== STEP 1: Script Generation ===")
    from pipeline.brand_voice import load_brand_profile
    from pipeline.long_video.script_gen import generate_script

    profile = await load_brand_profile(TENANT_ID)
    if profile is None:
        from pipeline.long_video.orchestrator import _default_profile
        profile = _default_profile(TENANT_ID)
        logger.warning("No brand profile found, using default")

    script = await generate_script(INTENT, profile)
    logger.info("Script: %s (%d scenes)", script.title, script.total_scenes)
    for scene in script.scenes:
        logger.info("  Scene %d [%s]: %s", scene.index, scene.scene_type, scene.voiceover_text[:60])
    return script


async def test_step_2_tts(script):
    """Step 2: Generate voiceovers via ElevenLabs."""
    logger.info("=== STEP 2: TTS Generation ===")
    from pipeline.long_video.tts import generate_voiceover

    tmp_dir = f"/tmp/scribario/{PROJECT_ID}"
    os.makedirs(tmp_dir, exist_ok=True)

    # Use default voice (Adam) for testing
    voice_id = "pNInz6obpgDQGcFmaJgB"

    tts_results = []
    for scene in script.scenes:
        result = await generate_voiceover(
            text=scene.voiceover_text,
            voice_id=voice_id,
            output_dir=tmp_dir,
        )
        logger.info("  Scene %d TTS: %.1fs, %s", scene.index, result.duration_seconds, result.audio_url)
        tts_results.append(result)

    return tts_results


async def test_step_3_sfx(script):
    """Step 3: Generate SFX via ElevenLabs."""
    logger.info("=== STEP 3: SFX Generation ===")
    from pipeline.long_video.sfx import generate_sfx_batch

    tmp_dir = f"/tmp/scribario/{PROJECT_ID}"
    descriptions = [
        {"description": s.sfx_description, "duration_seconds": 3.0}
        for s in script.scenes
    ]

    results = await generate_sfx_batch(descriptions, output_dir=tmp_dir)
    for i, r in enumerate(results):
        if r:
            logger.info("  Scene %d SFX: %s", i, r.audio_path)
        else:
            logger.warning("  Scene %d SFX: FAILED", i)
    return results


async def test_step_4_frames(script):
    """Step 4: Generate frames via Kie.ai Nano Banana 2."""
    logger.info("=== STEP 4: Frame Generation ===")
    from pipeline.long_video.frame_gen import generate_all_frames

    assets = await generate_all_frames(script.scenes, aspect_ratio="16:9")
    for a in assets:
        logger.info(
            "  Scene %d frames: start=%s, end=%s",
            a.scene_index,
            a.start_frame_url[:60] if a.start_frame_url else "NONE",
            a.end_frame_url[:60] if a.end_frame_url else "NONE",
        )
    return assets


async def test_step_5_clips(frame_assets, video_prompts):
    """Step 5: Generate video clips via Kie.ai Veo 3.1."""
    logger.info("=== STEP 5: Clip Generation ===")
    from pipeline.long_video.clip_gen import generate_all_clips

    clip_assets = await generate_all_clips(frame_assets, video_prompts, aspect_ratio="16:9")
    for ca in clip_assets:
        logger.info(
            "  Scene %d clip: %s (cost=$%.2f)",
            ca.scene_index,
            ca.video_clip_url[:60] if ca.video_clip_url else "NONE",
            ca.cost_usd,
        )
    return clip_assets


async def test_step_6_stitch(clip_assets, tts_results, sfx_results, script):
    """Step 6: Stitch everything together with FFmpeg."""
    logger.info("=== STEP 6: FFmpeg Stitch ===")
    from pipeline.long_video.models import StitchSpec
    from pipeline.long_video.stitcher import stitch

    # Download remote clip URLs to local files first
    import httpx

    tmp_dir = f"/tmp/scribario/{PROJECT_ID}"
    local_clips = []
    async with httpx.AsyncClient() as client:
        for i, ca in enumerate(clip_assets):
            if ca.video_clip_url and ca.video_clip_url.startswith("http"):
                local_path = os.path.join(tmp_dir, f"clip_{i}.mp4")
                logger.info("  Downloading clip %d...", i)
                resp = await client.get(ca.video_clip_url, timeout=120.0)
                resp.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                local_clips.append(local_path)
            elif ca.video_clip_url:
                local_clips.append(ca.video_clip_url)
            else:
                logger.warning("  Scene %d has no clip, skipping", ca.scene_index)

    if not local_clips:
        raise RuntimeError("No clips to stitch!")

    voiceover_paths = [r.audio_url for r in tts_results]
    sfx_paths = [r.audio_path for r in sfx_results if r is not None]

    spec = StitchSpec(
        project_id=PROJECT_ID,
        scene_clips=local_clips,
        scene_voiceovers=voiceover_paths[:len(local_clips)],
        aspect_ratio="16:9",
        scene_sfx=sfx_paths[:len(local_clips)],
    )

    result = await stitch(spec)
    logger.info(
        "Final video: %s (%.1fs, %.1f MB)",
        result.output_path,
        result.duration_seconds,
        result.file_size_bytes / 1_000_000,
    )
    return result


async def main():
    start = time.time()
    logger.info("Starting E2E test for long-form video pipeline")
    logger.info("Project ID: %s", PROJECT_ID)

    # Step 1: Script
    script = await test_step_1_script_gen()

    # Step 2 + 3: TTS + SFX (parallel)
    tts_results, sfx_results = await asyncio.gather(
        test_step_2_tts(script),
        test_step_3_sfx(script),
    )

    # Step 4: Frames
    frame_assets = await test_step_4_frames(script)

    # Step 5: Clips
    video_prompts = [s.visual_description for s in script.scenes]
    clip_assets = await test_step_5_clips(frame_assets, video_prompts)

    # Step 6: Stitch
    stitch_result = await test_step_6_stitch(clip_assets, tts_results, sfx_results, script)

    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info("E2E TEST COMPLETE in %.0f seconds", elapsed)
    logger.info("Final video: %s", stitch_result.output_path)
    logger.info("Duration: %.1fs", stitch_result.duration_seconds)
    logger.info("Size: %.1f MB", stitch_result.file_size_bytes / 1_000_000)
    logger.info("=" * 60)

    # Keep the video file for inspection
    print(f"\n\nVIDEO FILE: {stitch_result.output_path}")
    print("Copy to Windows: cp {} /mnt/c/Users/ronal/Downloads/".format(stitch_result.output_path))


if __name__ == "__main__":
    asyncio.run(main())
