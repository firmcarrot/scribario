#!/usr/bin/env python3
"""Scribario Hero Video — Kling 3.0 Multi-Shot with Element References.

Hero video for scribario.com: "The Future of Content Creation"
Old world (stagecoach) vs future tech (supercar). 3 shots, 15s.

Shot 1: Stagecoach trotting, supercar streaks past, dust erupts
Shot 2: Car stopped on road, dust settles, camera orbits
Shot 3: Close-up rear, car launches forward, dust storm

Usage:
    cd /home/ronald/projects/scribario
    python3 -m scripts.test_kling_multishot
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
logger = logging.getLogger("kling-multishot")

import httpx

from bot.config import get_settings

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
RON_CHAT_ID = 7560539974

# Reference images — 3 angles each
REF_DIR = "/mnt/c/Users/ronal/Downloads/scribario-reference-angles"
CAR_REFS = [
    f"{REF_DIR}/car_v2_front.jpg",
    f"{REF_DIR}/car_v2_side.jpg",
    f"{REF_DIR}/car_v2_rear.jpg",
]
COACH_REFS = [
    f"{REF_DIR}/cowboy_front.jpg",
    f"{REF_DIR}/cowboy_side.jpg",
    f"{REF_DIR}/cowboy_rear.jpg",
]

# ──────────────────────────────────────────────
# Director-style prompts — simple, what happens, <500 chars each
# ──────────────────────────────────────────────

SHOT_1 = (
    "Wide shot, dusty desert road at golden hour. "
    "@element_coach trotting slowly toward camera, dust rising from hooves. "
    "Suddenly @element_car streaks past as a silver blur, "
    "massive dust cloud erupts. Horses rear up, cowboy grabs his hat. "
    "Engine roar, whoosh, horse whinny, gravel spray."
)

SHOT_2 = (
    "Low angle, @element_car stopped on the desert road. "
    "Dust slowly settling around it. Camera orbits revealing the full body. "
    "Orange underglow pulses on the sand. Sunset behind. "
    "Descending engine hum, wind, settling dust."
)

SHOT_3 = (
    "Close-up, rear of @element_car on desert road at golden hour. "
    "Orange tail lights glowing bright. Then it launches forward, "
    "kicking up a massive dust storm that fills the entire frame. "
    "Engine roar building, tires spinning, gravel spray, rushing wind."
)


async def upload_refs_to_supabase(
    ref_paths: list[str], prefix: str
) -> list[str]:
    """Upload reference images to Supabase storage, return signed URLs."""
    from supabase import create_client

    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

    bucket = "reference-images"
    try:
        supabase.storage.get_bucket(bucket)
    except Exception:
        supabase.storage.create_bucket(bucket, options={"public": False})

    urls = []
    for i, local_path in enumerate(ref_paths):
        filename = f"kling-{prefix}-{i}.jpg"
        storage_path = f"hero-video/{filename}"

        with open(local_path, "rb") as f:
            file_bytes = f.read()

        # Retry up to 3 times for transient SSL/network errors
        for attempt in range(3):
            try:
                try:
                    supabase.storage.from_(bucket).remove([storage_path])
                except Exception:
                    pass

                supabase.storage.from_(bucket).upload(
                    storage_path,
                    file_bytes,
                    file_options={"content-type": "image/jpeg", "upsert": "true"},
                )
                break
            except Exception as e:
                if attempt < 2:
                    logger.warning("Upload attempt %d failed: %s — retrying...", attempt + 1, e)
                    import time as _time
                    _time.sleep(2)
                else:
                    raise

        # 1-hour signed URL
        signed = supabase.storage.from_(bucket).create_signed_url(storage_path, 3600)
        url = signed.get("signedURL", "") or signed.get("signedUrl", "")
        if not url:
            raise RuntimeError(f"No signed URL for {storage_path}: {signed}")

        logger.info("Uploaded %s → %s", os.path.basename(local_path), url[:80])
        urls.append(url)

    return urls


async def generate_multishot(
    api_key: str, car_ref_urls: list[str], coach_ref_urls: list[str]
) -> str:
    """Kling 3.0 multi-shot with element references."""
    logger.info("=== Kling 3.0 Multi-Shot + Element References ===")
    logger.info("  Car refs: %d, Coach refs: %d", len(car_ref_urls), len(coach_ref_urls))

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "kling-3.0/video",
        "callBackUrl": "",
        "input": {
            "prompt": "",
            "sound": True,
            "aspect_ratio": "16:9",
            "duration": "15",
            "mode": "pro",
            "multi_shots": True,
            "image_urls": [coach_ref_urls[0]],  # Start frame: stagecoach approaching
            "multi_prompt": [
                {"prompt": SHOT_1, "duration": 5},
                {"prompt": SHOT_2, "duration": 5},
                {"prompt": SHOT_3, "duration": 5},
            ],
            "kling_elements": [
                {
                    "name": "element_car",
                    "description": "Silver futuristic supercar with orange glow",
                    "element_input_urls": car_ref_urls,
                },
                {
                    "name": "element_coach",
                    "description": "Red stagecoach with two horses and cowboy driver",
                    "element_input_urls": coach_ref_urls,
                },
            ],
        },
    }

    logger.info("Payload: %s", json.dumps(payload, indent=2)[:500])

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
            logger.error("Full response: %s", json.dumps(data, indent=2))
            raise RuntimeError(f"Kling createTask failed: {data}")

        task_id = data["data"]["taskId"]
        logger.info("Task: %s — polling (up to 20 min for multi-shot)...", task_id)

        # Poll — multi-shot Pro with audio can take LONGER than single-shot
        for attempt in range(120):  # 120 × 10s = 20 min
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
                    logger.info("Kling multi-shot complete: %s", result_urls[0])
                    return result_urls[0]

                # Fallback: response object
                response_obj = task_info.get("response", {})
                result_urls = response_obj.get("resultUrls", [])
                if result_urls:
                    logger.info("Kling multi-shot complete: %s", result_urls[0])
                    return result_urls[0]

                # Fallback: works array
                works = task_info.get("works", [])
                if works:
                    url = works[0].get("resource", {}).get("resource", "")
                    if url:
                        logger.info("Kling multi-shot complete: %s", url)
                        return url

                raise RuntimeError(f"Success but no video URL: {task_info}")

            if state in ("failed", "fail") or success_flag in (2, 3):
                fail_msg = task_info.get("failMsg", "unknown")
                fail_code = task_info.get("failCode", "")
                logger.error("Full task_info: %s", json.dumps(task_info, indent=2)[:1000])
                raise RuntimeError(f"Kling FAILED (code={fail_code}): {fail_msg}")

            if attempt % 6 == 0:
                logger.info(
                    "  Poll %d/120 — state=%s, still generating...",
                    attempt + 1,
                    state,
                )

        raise TimeoutError(f"Kling timed out after 20 min. Task: {task_id}")


async def main():
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import FSInputFile

    settings = get_settings()
    api_key = settings.kie_ai_api_key
    start = time.time()

    # 1. Upload reference images (car + stagecoach)
    logger.info("=== STEP 1: Upload reference images ===")
    car_ref_urls = await upload_refs_to_supabase(CAR_REFS, "car")
    coach_ref_urls = await upload_refs_to_supabase(COACH_REFS, "coach")

    # 2. Generate multi-shot video
    logger.info("=== STEP 2: Kling 3.0 multi-shot generation ===")
    video_url = await generate_multishot(api_key, car_ref_urls, coach_ref_urls)

    # 3. Download
    tmp_path = "/tmp/kling_multishot.mp4"
    async with httpx.AsyncClient() as client:
        resp = await client.get(video_url, timeout=120.0)
        resp.raise_for_status()
        with open(tmp_path, "wb") as f:
            f.write(resp.content)
    size_mb = os.path.getsize(tmp_path) / 1e6
    logger.info("Downloaded: %.1f MB", size_mb)

    elapsed = time.time() - start

    # 4. Save to Downloads
    dl_dir = "/mnt/c/Users/ronal/Downloads/scribario-hero-video"
    os.makedirs(dl_dir, exist_ok=True)
    dl_path = os.path.join(dl_dir, "hero_v2_director_style.mp4")
    shutil.copy2(tmp_path, dl_path)
    shutil.copy2(tmp_path, "/mnt/c/Users/ronal/Downloads/scribario-hero-v2.mp4")

    # 5. Telegram
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
                f"<b>Scribario Hero Video v2 — Director-Style Prompts</b>\n\n"
                f"2 elements: @element_car (3 refs) + @element_coach (3 refs)\n\n"
                f"Shot 1: Stagecoach trotting, supercar streaks past\n"
                f"Shot 2: Car stopped, dust settles, camera orbits\n"
                f"Shot 3: Close-up rear, car launches, dust storm\n\n"
                f"Kling 3.0 Pro + audio + multi-shot\n"
                f"15s (3×5s) | {size_mb:.1f} MB | {elapsed:.0f}s gen time"
            ),
        )
        logger.info("Sent to Telegram!")
    finally:
        await bot.session.close()

    os.remove(tmp_path)
    logger.info("=== DONE in %.0fs ===", elapsed)
    logger.info("Output: %s", dl_path)


if __name__ == "__main__":
    asyncio.run(main())
