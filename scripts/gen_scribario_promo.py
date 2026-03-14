#!/usr/bin/env python3
"""Generate a Scribario promo video and send it via Telegram.

UGC-style: business owner can't stop praising how they replaced an entire team
with a text. Tagline: "Text it. Approve it. Posted."
Logo: orange background, white S.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("scribario-promo")

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
PROJECT_ID = f"scribario-promo-{int(time.time())}"
RON_CHAT_ID = 7560539974

INTENT = (
    "UGC-style testimonial video for Scribario. A busy small business owner (restaurant, salon, "
    "or contractor type) is raving about how they replaced their entire social media team with "
    "a single text message. They're blown away — they just text what they want to post, approve "
    "it, and it's live everywhere. Show real scenarios: owner texting on their phone, content "
    "appearing on social feeds, the simplicity of it. End with Scribario branding — orange "
    "background with white S logo, tagline 'Text it. Approve it. Posted.' and 'scribario.com'. "
    "Tone: no-bullshit, relatable, empowering. This is for real business owners who hate tech."
)


async def main():
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import FSInputFile

    from bot.config import get_settings
    from pipeline.brand_voice import load_brand_profile
    from pipeline.long_video.models import StitchSpec
    from pipeline.long_video.script_gen import generate_script
    from pipeline.long_video.sfx import generate_sfx_batch
    from pipeline.long_video.stitcher import stitch
    from pipeline.long_video.tts import generate_voiceover
    from pipeline.long_video.frame_gen import generate_all_frames
    from pipeline.long_video.clip_gen import generate_all_clips

    import httpx

    settings = get_settings()
    tmp_dir = f"/tmp/scribario/{PROJECT_ID}"
    os.makedirs(tmp_dir, exist_ok=True)

    start = time.time()

    # --- 1. Script ---
    logger.info("=== STEP 1: Script Generation ===")
    profile = await load_brand_profile(SCRIBARIO_TENANT_ID)
    script = await generate_script(INTENT, profile)
    logger.info("Script: %s (%d scenes)", script.title, script.total_scenes)
    for s in script.scenes:
        logger.info("  Scene %d: %s", s.index, s.voiceover_text[:80])

    # --- 2. TTS + SFX (parallel) ---
    logger.info("=== STEP 2: TTS + SFX ===")
    voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam (default)

    async def do_tts():
        results = []
        for scene in script.scenes:
            r = await generate_voiceover(scene.voiceover_text, voice_id, tmp_dir)
            logger.info("  TTS scene %d: %.1fs", scene.index, r.duration_seconds)
            results.append(r)
        return results

    async def do_sfx():
        descs = [
            {"description": s.sfx_description, "duration_seconds": 3.0}
            for s in script.scenes
        ]
        return await generate_sfx_batch(descs, output_dir=tmp_dir)

    tts_results, sfx_results = await asyncio.gather(do_tts(), do_sfx())

    # --- 3. Frames ---
    logger.info("=== STEP 3: Frame Generation ===")
    frame_assets = await generate_all_frames(script.scenes, aspect_ratio="16:9")
    for a in frame_assets:
        logger.info("  Scene %d: frames OK", a.scene_index)

    # --- 4. Clips ---
    logger.info("=== STEP 4: Clip Generation ===")
    video_prompts = [s.visual_description for s in script.scenes]
    clip_assets = await generate_all_clips(frame_assets, video_prompts, aspect_ratio="16:9")
    for ca in clip_assets:
        logger.info("  Scene %d: clip=%s", ca.scene_index,
                     "OK" if ca.video_clip_url else "FAILED")

    # --- 5. Download clips to local files ---
    logger.info("=== STEP 5: Download clips ===")
    local_clips = []
    async with httpx.AsyncClient() as client:
        for i, ca in enumerate(clip_assets):
            if ca.video_clip_url and ca.video_clip_url.startswith("http"):
                local_path = os.path.join(tmp_dir, f"clip_{i}.mp4")
                resp = await client.get(ca.video_clip_url, timeout=120.0)
                resp.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                local_clips.append(local_path)
                logger.info("  Downloaded clip %d", i)

    # --- 6. Stitch ---
    logger.info("=== STEP 6: FFmpeg Stitch ===")
    voiceover_paths = [r.audio_url for r in tts_results[:len(local_clips)]]
    sfx_paths = [r.audio_path for r in sfx_results[:len(local_clips)] if r is not None]

    spec = StitchSpec(
        project_id=PROJECT_ID,
        scene_clips=local_clips,
        scene_voiceovers=voiceover_paths,
        aspect_ratio="16:9",
        scene_sfx=sfx_paths,
    )
    result = await stitch(spec)
    logger.info("Final: %s (%.1fs, %.1f MB)",
                result.output_path, result.duration_seconds,
                result.file_size_bytes / 1_000_000)

    elapsed = time.time() - start
    logger.info("Pipeline complete in %.0f seconds", elapsed)

    # --- 7. Send via Telegram as file upload ---
    logger.info("=== STEP 7: Send to Telegram ===")
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        video_file = FSInputFile(result.output_path)
        await bot.send_video(
            chat_id=RON_CHAT_ID,
            video=video_file,
            caption=(
                f"<b>Scribario Promo Video</b>\n\n"
                f"Script: {script.title}\n"
                f"Scenes: {script.total_scenes}\n"
                f"Duration: {result.duration_seconds:.1f}s\n"
                f"Generated in {elapsed:.0f}s\n\n"
                f"Text it. Approve it. Posted."
            ),
            parse_mode=ParseMode.HTML,
        )
        logger.info("Video sent to Telegram chat %d", RON_CHAT_ID)
    finally:
        await bot.session.close()

    # Also copy to Windows Downloads
    dl_path = "/mnt/c/Users/ronal/Downloads/scribario-promo.mp4"
    import shutil
    shutil.copy2(result.output_path, dl_path)
    logger.info("Also saved to %s", dl_path)

    print(f"\nDONE! Video sent to Telegram and saved to Downloads.")


if __name__ == "__main__":
    asyncio.run(main())
