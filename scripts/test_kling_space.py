#!/usr/bin/env python3
"""Test Kling 3.0 — Astronaut bullet scene.

Pushing boundaries: close-up astronaut fires gun in space,
camera follows the bullet. Testing Kling 3.0 via Kie.ai.

Usage:
    cd /home/ronald/projects/scribario
    python3 -m scripts.test_kling_space
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("kling-space-test")

import httpx

from bot.config import get_settings

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
RON_CHAT_ID = 7560539974

# ──────────────────────────────────────────────
# PROMPTS — all research lessons applied
# ──────────────────────────────────────────────

# Nano Banana 2 validation frame
FRAME_PROMPT = (
    "A cinematic extreme close-up of an astronaut floating in deep space. "
    "The astronaut's helmet visor is down, completely reflective — we cannot "
    "see the face. In the curved visor reflection we see the interior edge "
    "of a spacecraft module, distant stars, the blue curve of Earth on the "
    "horizon, and the faint glow of instrument panels. The astronaut's "
    "gloved right hand grips a matte black futuristic handgun, arm extended "
    "forward toward the right of frame. The gun has subtle orange LED "
    "accents along the barrel. "
    "Lighting: harsh single-source sunlight from upper-left, creating deep "
    "black shadows on the right side of the helmet. A faint blue earthshine "
    "fill on the shadow side. Stars visible in the pure black background. "
    "Shot on 50mm lens, f/2.0, ISO 200. Anamorphic lens, subtle horizontal "
    "bokeh flares from the sun hitting the visor edge. "
    "Hyper-realistic, cinematic film, muted colors. No skin smoothing. "
    "AVOID: cartoon, CGI look, visible face, plastic, oversaturated."
)

# Kling 3.0 video prompt — style FIRST, no camera equipment words, exact audio
VIDEO_PROMPT = (
    "Cinematic sci-fi film, muted colors, photorealistic. "
    "Opening: extreme close-up of an astronaut's reflective helmet visor "
    "floating in deep space. Stars and the blue curve of Earth reflected "
    "in the curved glass. The visor is fully down — no face visible, only "
    "reflections. Harsh white sunlight from the upper left, deep black "
    "shadows. A gloved hand grips a matte black futuristic handgun with "
    "subtle orange LED accents. "
    "The astronaut slowly raises the gun toward frame right. A beat of "
    "stillness. Then fires — a bright orange muzzle flash blooms in the "
    "void. The viewpoint instantly shifts to follow the bullet as it "
    "streaks through empty space, spinning slowly, trailing a faint heat "
    "distortion. Stars streak past. The bullet tumbles forward in slow "
    "motion against the infinite black void. "
    "Audio: deep silence of space, then a muffled metallic BANG that "
    "reverberates through the suit, then a high-pitched ringing tone "
    "fading into absolute silence as the bullet flies. No music. "
    "No dialogue. No subtitles. No on-screen text. "
    "Avoid: deformed hands, morphing objects, text overlays, floating "
    "objects, subtitle text, cartoon effects, jittery motion."
)


async def generate_frame() -> str:
    """Generate validation frame with Nano Banana 2."""
    from pipeline.image_gen import ImageGenerationService

    logger.info("=== STEP 1: Validation frame (Nano Banana 2, $.04) ===")
    service = ImageGenerationService(tenant_id=SCRIBARIO_TENANT_ID)
    result = await service.generate(prompt=FRAME_PROMPT, aspect_ratio="16:9")
    logger.info("Frame: %s ($%.2f)", result.url, result.cost_usd)
    return result.url


async def generate_kling_clip(api_key: str) -> str:
    """Generate video with Kling 3.0 via Kie.ai jobs API.

    Uses the same createTask/poll pattern as images but with
    kling-3.0/video model ID.
    """
    logger.info("=== STEP 2: Kling 3.0 video clip ===")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "kling-3.0/video",
        "callBackUrl": "",
        "input": {
            "prompt": VIDEO_PROMPT,
            "sound": True,
            "aspect_ratio": "16:9",
            "duration": "10",
            "mode": "pro",
            "multi_shots": False,
            "multi_prompt": [],
        },
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Create task
        resp = await client.post(
            "https://api.kie.ai/api/v1/jobs/createTask",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info("Create task response: %s", data)

        if data.get("code") != 200:
            raise RuntimeError(f"Kling createTask failed: {data}")

        task_id = data.get("data", {}).get("taskId")
        if not task_id:
            raise RuntimeError(f"No taskId returned: {data}")

        logger.info("Kling 3.0 task: %s — polling...", task_id)

        # Poll for completion (up to 10 min)
        for attempt in range(60):
            await asyncio.sleep(10)
            resp = await client.get(
                "https://api.kie.ai/api/v1/jobs/recordInfo",
                headers=headers,
                params={"taskId": task_id},
            )
            resp.raise_for_status()
            poll_data = resp.json()

            if poll_data.get("code") != 200:
                raise RuntimeError(f"Poll failed: {poll_data}")

            task_info = poll_data["data"]
            status = task_info.get("successFlag", 0)

            if status == 1:
                # Extract video URL
                response_obj = task_info.get("response", {})
                result_urls = response_obj.get("resultUrls", [])
                if result_urls:
                    video_url = result_urls[0]
                else:
                    works = task_info.get("works", [])
                    if works:
                        video_url = works[0].get("resource", {}).get("resource", "")
                    else:
                        raise RuntimeError(f"No video URL in response: {task_info}")

                logger.info("Kling 3.0 complete: %s", video_url)
                return video_url

            if status in (2, 3):
                raise RuntimeError(f"Kling 3.0 generation FAILED: {task_info}")

            logger.info("  Poll %d/60 — still generating...", attempt + 1)

        raise TimeoutError("Kling 3.0 timed out after 10 minutes")


async def main():
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import FSInputFile

    settings = get_settings()
    api_key = settings.kie_ai_api_key
    tmp_dir = f"/tmp/scribario/kling-space-{int(time.time())}"
    os.makedirs(tmp_dir, exist_ok=True)
    start = time.time()

    # 1. Validation frame
    frame_url = await generate_frame()

    # Save frame to Downloads
    frames_dir = "/mnt/c/Users/ronal/Downloads/scribario-kling-space"
    os.makedirs(frames_dir, exist_ok=True)
    async with httpx.AsyncClient() as client:
        resp = await client.get(frame_url, timeout=60.0)
        resp.raise_for_status()
        frame_path = os.path.join(frames_dir, "validation_frame.jpg")
        with open(frame_path, "wb") as f:
            f.write(resp.content)
    logger.info("Frame saved: %s", frame_path)

    # 2. Kling 3.0 video
    video_url = await generate_kling_clip(api_key)

    # Download video
    clip_path = os.path.join(tmp_dir, "kling_space.mp4")
    async with httpx.AsyncClient() as client:
        resp = await client.get(video_url, timeout=120.0)
        resp.raise_for_status()
        with open(clip_path, "wb") as f:
            f.write(resp.content)
    logger.info("Clip downloaded: %.1f MB", len(resp.content) / 1_000_000)

    elapsed = time.time() - start

    # 3. Copy to Downloads
    dl_path = "/mnt/c/Users/ronal/Downloads/scribario-kling-space.mp4"
    shutil.copy2(clip_path, dl_path)
    logger.info("Saved: %s", dl_path)

    # Also copy to frames dir
    shutil.copy2(clip_path, os.path.join(frames_dir, "kling_space.mp4"))

    # 4. Send to Telegram
    logger.info("=== Sending to Telegram ===")
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        await bot.send_video(
            chat_id=RON_CHAT_ID,
            video=FSInputFile(clip_path),
            caption=(
                f"<b>Kling 3.0 Pro — Space Bullet Test</b>\n\n"
                f"Model: Kling 3.0 Pro + audio\n"
                f"Duration: 10s target\n"
                f"Generated in: {elapsed:.0f}s\n\n"
                f"Lessons applied:\n"
                f"• Style keywords FIRST\n"
                f"• No camera equipment words\n"
                f"• Exact audio specification\n"
                f"• Single subject, dramatic action\n"
                f"• Muted colors, cinematic film"
            ),
        )
        logger.info("Sent to Telegram!")
    finally:
        await bot.session.close()

    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)
    logger.info("=== DONE in %.0fs ===", elapsed)
    logger.info("Output: %s", dl_path)


if __name__ == "__main__":
    asyncio.run(main())
