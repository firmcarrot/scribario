#!/usr/bin/env python3
"""Test Kling 3.0 — Chariot vs Hovercraft rematch.

Same concept as the failed hero video, but with all research lessons
applied and Kling 3.0 instead of Veo.

Key lessons applied:
- Style keywords FIRST
- No camera equipment words — describe what's IN FRAME
- Simple scene: one road, one old vehicle, one blur passing it
- Exact audio: horse hooves, leather, then WHOOSH
- "muted colors, cinematic film" for photorealism
- Single continuous action, no cuts

Usage:
    cd /home/ronald/projects/scribario
    python3 -m scripts.test_kling_chariot
"""

from __future__ import annotations

import asyncio
import json
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
logger = logging.getLogger("kling-chariot")

import httpx

from bot.config import get_settings

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
RON_CHAT_ID = 7560539974

# ──────────────────────────────────────────────
# PROMPTS
# ──────────────────────────────────────────────

# Validation frame (Nano Banana 2)
FRAME_PROMPT = (
    "Cinematic film, muted colors, shot on a Sony camera. "
    "A wide shot of a dusty golden-hour desert highway stretching to the "
    "horizon. A weathered old-timer in a wide-brimmed hat and dusty brown "
    "coat sits on a rickety wooden horse-drawn cart pulled by a single "
    "brown horse. They are moving slowly along the right side of the road, "
    "kicking up a thin trail of dust. The desert landscape is vast and "
    "empty — red rock mesas in the distance, scrub brush, cracked earth. "
    "Golden hour sunlight from camera-left, long warm shadows stretching "
    "across the road. Warm amber and sepia tones. "
    "Shot on 35mm, f/2.8, ISO 200. Anamorphic lens, slight horizontal "
    "bokeh flares from the low sun. Subtle film grain. "
    "Documentary realism. Natural imperfect framing. "
    "No skin smoothing, no CGI. "
    "AVOID: modern vehicles, plastic look, oversaturated, cartoon."
)

# Kling 3.0 video — the money shot
VIDEO_PROMPT = (
    "Cinematic film, muted colors, photorealistic, shot on 35mm anamorphic. "
    "A wide shot of a dusty golden-hour desert highway. A weathered old "
    "cowboy in a wide-brimmed hat and dusty brown duster coat drives a "
    "rickety wooden horse-drawn cart pulled by a single brown horse. They "
    "plod slowly along the road, dust rising gently behind the wooden "
    "wheels. The desert is vast — red mesas, scrub brush, empty sky. "
    "Suddenly a sleek matte-black futuristic hovercraft with glowing "
    "orange accent lines BLASTS past from behind, streaking through frame "
    "in a blur of black and orange. A massive wall of dust and wind "
    "erupts. The horse rears up in shock. The old cowboy grabs his hat "
    "with one hand, jaw dropped, staring after the machine as it shrinks "
    "into the distance leaving a trail of orange-glowing exhaust. "
    "Golden hour sunlight from the left, long warm shadows, amber tones. "
    "Audio: slow horse hooves clopping on packed dirt, leather creaking, "
    "wooden wheels grinding on gravel. Then a rising high-pitched engine "
    "whine approaching fast from behind. A massive WHOOSH as the "
    "hovercraft blasts past — wind blast, gravel spray. The horse "
    "whinnies in panic. Then fading engine hum into desert silence. "
    "No music. No dialogue. No subtitles. No on-screen text. "
    "Avoid: deformed hands, morphing objects, text overlays, floating "
    "objects, jittery motion, cartoon effects, subtitle text."
)


async def generate_frame(api_key: str) -> str:
    """Validation frame via Nano Banana 2."""
    from pipeline.image_gen import ImageGenerationService

    logger.info("=== STEP 1: Validation frame ($.04) ===")
    service = ImageGenerationService(tenant_id=SCRIBARIO_TENANT_ID)
    result = await service.generate(prompt=FRAME_PROMPT, aspect_ratio="16:9")
    logger.info("Frame: %s ($%.2f)", result.url, result.cost_usd)
    return result.url


async def generate_kling_clip(api_key: str) -> str:
    """Kling 3.0 Pro, 10s, with audio."""
    logger.info("=== STEP 2: Kling 3.0 Pro clip (10s + audio) ===")

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
        logger.info("CreateTask: code=%s msg=%s", data.get("code"), data.get("msg"))

        if data.get("code") != 200:
            raise RuntimeError(f"Kling createTask failed: {data}")

        task_id = data["data"]["taskId"]
        logger.info("Task: %s — polling (up to 15 min)...", task_id)

        # Poll — Kling Pro can take up to 12+ min
        for attempt in range(90):  # 90 * 10s = 15 min
            await asyncio.sleep(10)
            resp = await client.get(
                "https://api.kie.ai/api/v1/jobs/recordInfo",
                headers=headers,
                params={"taskId": task_id},
            )
            resp.raise_for_status()
            poll = resp.json()

            if poll.get("code") != 200:
                raise RuntimeError(f"Poll error: {poll}")

            task_info = poll["data"]
            state = task_info.get("state", "")
            success_flag = task_info.get("successFlag", 0)

            if state == "success" or success_flag == 1:
                # Parse resultJson
                result_json_str = task_info.get("resultJson", "{}")
                try:
                    result_obj = json.loads(result_json_str)
                except (json.JSONDecodeError, TypeError):
                    result_obj = {}

                result_urls = result_obj.get("resultUrls", [])
                if result_urls:
                    logger.info("Kling complete: %s", result_urls[0])
                    return result_urls[0]

                # Fallback: check response object
                response_obj = task_info.get("response", {})
                result_urls = response_obj.get("resultUrls", [])
                if result_urls:
                    logger.info("Kling complete: %s", result_urls[0])
                    return result_urls[0]

                # Fallback: works array
                works = task_info.get("works", [])
                if works:
                    url = works[0].get("resource", {}).get("resource", "")
                    if url:
                        logger.info("Kling complete: %s", url)
                        return url

                raise RuntimeError(f"Success but no video URL: {task_info}")

            if state == "failed" or success_flag in (2, 3):
                raise RuntimeError(
                    f"Kling FAILED: {task_info.get('failMsg', 'unknown')}"
                )

            if attempt % 6 == 0:
                logger.info("  Poll %d/90 — state=%s, still generating...", attempt + 1, state)

        raise TimeoutError(f"Kling timed out after 15 min. Task: {task_id}")


async def main():
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import FSInputFile

    settings = get_settings()
    api_key = settings.kie_ai_api_key
    start = time.time()

    # 1. Validation frame
    frame_url = await generate_frame(api_key)

    frames_dir = "/mnt/c/Users/ronal/Downloads/scribario-kling-chariot"
    os.makedirs(frames_dir, exist_ok=True)
    async with httpx.AsyncClient() as client:
        resp = await client.get(frame_url, timeout=60.0)
        resp.raise_for_status()
        with open(os.path.join(frames_dir, "validation_frame.jpg"), "wb") as f:
            f.write(resp.content)
    logger.info("Frame saved to Downloads")

    # 2. Kling 3.0 video
    video_url = await generate_kling_clip(api_key)

    # Download
    tmp_path = "/tmp/kling_chariot.mp4"
    async with httpx.AsyncClient() as client:
        resp = await client.get(video_url, timeout=120.0)
        resp.raise_for_status()
        with open(tmp_path, "wb") as f:
            f.write(resp.content)
    size_mb = os.path.getsize(tmp_path) / 1e6
    logger.info("Downloaded: %.1f MB", size_mb)

    elapsed = time.time() - start

    # 3. Save to Downloads
    dl_path = "/mnt/c/Users/ronal/Downloads/scribario-kling-chariot.mp4"
    shutil.copy2(tmp_path, dl_path)
    shutil.copy2(tmp_path, os.path.join(frames_dir, "kling_chariot.mp4"))

    # 4. Telegram
    logger.info("=== Sending to Telegram ===")
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        await bot.send_video(
            chat_id=RON_CHAT_ID,
            video=FSInputFile(tmp_path),
            caption=(
                f"<b>Kling 3.0 Pro — Chariot vs Hovercraft REMATCH</b>\n\n"
                f"Same concept as failed hero video, new model + new prompting.\n\n"
                f"Model: Kling 3.0 Pro + native audio\n"
                f"Duration: 10s\n"
                f"Size: {size_mb:.1f} MB\n"
                f"Generated in: {elapsed:.0f}s\n\n"
                f"Key differences from old attempt:\n"
                f"• Style keywords FIRST\n"
                f"• Zero camera equipment words\n"
                f"• Exact audio: hooves → whoosh → whinny → silence\n"
                f"• Kling 3.0 Pro (not Veo)\n"
                f"• Single continuous shot, no cuts"
            ),
        )
        logger.info("Sent to Telegram!")
    finally:
        await bot.session.close()

    os.remove(tmp_path)
    logger.info("=== DONE in %.0fs ===", elapsed)


if __name__ == "__main__":
    asyncio.run(main())
