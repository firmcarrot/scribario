#!/usr/bin/env python3
"""Test: Product photo → scene image → animated video.

The Scribario video flow:
1. User uploads product photo (Mondo Shrimp bowl)
2. Nano Banana generates scene image using product as reference ($0.04)
3. Veo 3.1 Fast animates the scene image ($0.40)
4. Preview → approve → post

Total: ~$0.44 per video post.

Usage:
    cd /home/ronald/projects/scribario
    python3 -m scripts.test_video_from_product
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
logger = logging.getLogger("video-from-product")

import httpx

from bot.config import get_settings
from pipeline.image_gen import ImageGenerationService
from pipeline.video_gen import VideoGenerationService

RON_CHAT_ID = 7560539974
MONDO_TENANT_ID = "52590da5-bc80-4161-ac13-62e9bcd75424"

PRODUCT_IMAGE = "/mnt/c/Users/ronal/Downloads/1768105438756-BD26891E-E222-4ED5-84E3-8DFA4B97A694 (1).png"


async def upload_product_to_supabase(local_path: str) -> str:
    """Upload product photo to Supabase storage, return signed URL."""
    from supabase import create_client

    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

    bucket = "reference-images"
    storage_path = "video-test/mondo-shrimp-product.png"

    with open(local_path, "rb") as f:
        file_bytes = f.read()

    try:
        supabase.storage.from_(bucket).remove([storage_path])
    except Exception:
        pass

    supabase.storage.from_(bucket).upload(
        storage_path,
        file_bytes,
        file_options={"content-type": "image/png", "upsert": "true"},
    )

    signed = supabase.storage.from_(bucket).create_signed_url(storage_path, 3600)
    url = signed.get("signedURL", "") or signed.get("signedUrl", "")
    if not url:
        raise RuntimeError(f"No signed URL: {signed}")

    logger.info("Product photo uploaded: %s", url[:80])
    return url


async def main():
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import FSInputFile

    settings = get_settings()
    start = time.time()

    # 1. Upload product photo to get a URL for Nano Banana reference
    logger.info("=== STEP 1: Upload product photo ===")
    product_url = await upload_product_to_supabase(PRODUCT_IMAGE)

    # 2. Generate scene image with Nano Banana — product as reference
    logger.info("=== STEP 2: Generate scene image (Nano Banana) ===")

    scene_prompt = (
        "A candid photo of a young professional man on a busy New York City subway. "
        "The train is packed and chaotic — people standing, holding rails, a blur of "
        "movement around him. But he sits calmly with a satisfied smile, eyes closed, "
        "savoring a bite from the bowl of shrimp shown in the reference photo. "
        "The white bowl with the exact shrimp dish from the reference is on his lap. "
        "Warm overhead fluorescent subway lighting, golden tones on his face. "
        "Shot from across the aisle, 35mm lens, f/2.8, ISO 800, shallow depth of field "
        "— the chaos behind him is slightly blurred while he and the food are sharp. "
        "Documentary realism. No skin smoothing, no beauty filters. Candid energy. "
        "No text, no logos, no watermarks."
    )

    image_service = ImageGenerationService()
    image_result = await image_service.generate(
        prompt=scene_prompt,
        aspect_ratio="9:16",  # Vertical for Reels/TikTok/Stories
        reference_image_urls=[product_url],
    )
    logger.info("Scene image generated: %s (cost: $%.2f)", image_result.url[:80], image_result.cost_usd)

    # Download scene image to verify
    scene_image_path = "/tmp/mondo_scene.jpg"
    async with httpx.AsyncClient() as client:
        resp = await client.get(image_result.url, timeout=60.0)
        resp.raise_for_status()
        with open(scene_image_path, "wb") as f:
            f.write(resp.content)
    logger.info("Scene image downloaded: %s", scene_image_path)

    # Upload scene image to Supabase for Veo reference
    from supabase import create_client

    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    storage_path = "video-test/mondo-scene-frame.jpg"
    with open(scene_image_path, "rb") as f:
        scene_bytes = f.read()
    try:
        supabase.storage.from_("reference-images").remove([storage_path])
    except Exception:
        pass
    supabase.storage.from_("reference-images").upload(
        storage_path,
        scene_bytes,
        file_options={"content-type": "image/jpeg", "upsert": "true"},
    )
    signed = supabase.storage.from_("reference-images").create_signed_url(storage_path, 3600)
    scene_url = signed.get("signedURL", "") or signed.get("signedUrl", "")
    logger.info("Scene image uploaded for Veo: %s", scene_url[:80])

    # 3. Animate with Veo 3.1 Fast — reference image to video
    logger.info("=== STEP 3: Animate scene (Veo 3.1 Fast) ===")

    video_prompt = (
        "Cinematic film, muted warm colors. The man on the subway takes a slow, "
        "satisfying bite of shrimp. His eyes close with pleasure. Around him, "
        "passengers sway and shuffle — subtle motion blur. The train rocks gently. "
        "Warm fluorescent light flickers slightly. Shallow depth of field. "
        "Audio: muffled subway rumble, distant train announcements, the soft "
        "clatter of the train on tracks. No music. No dialogue. "
        "No subtitles. No on-screen text. "
        "Avoid: deformed hands, morphing objects, text overlays, floating objects."
    )

    video_service = VideoGenerationService(tenant_id=MONDO_TENANT_ID)
    video_result = await video_service.generate(
        prompt=video_prompt,
        aspect_ratio="9:16",
        generation_type="REFERENCE_2_VIDEO",
        image_urls=[scene_url],
    )
    logger.info("Video generated: %s (cost: $%.2f)", video_result.url[:80], video_result.cost_usd)

    # 4. Download video
    video_path = "/tmp/mondo_shrimp_video.mp4"
    async with httpx.AsyncClient() as client:
        resp = await client.get(video_result.url, timeout=120.0)
        resp.raise_for_status()
        with open(video_path, "wb") as f:
            f.write(resp.content)
    size_mb = os.path.getsize(video_path) / 1e6
    elapsed = time.time() - start
    logger.info("Video downloaded: %.1f MB in %.0fs", size_mb, elapsed)

    # 5. Save to Downloads
    dl_dir = "/mnt/c/Users/ronal/Downloads/scribario-video-test"
    os.makedirs(dl_dir, exist_ok=True)
    shutil.copy2(scene_image_path, os.path.join(dl_dir, "mondo_scene.jpg"))
    shutil.copy2(video_path, os.path.join(dl_dir, "mondo_shrimp_video.mp4"))
    shutil.copy2(video_path, "/mnt/c/Users/ronal/Downloads/mondo-shrimp-video.mp4")

    # 6. Send both to Telegram
    logger.info("=== Sending to Telegram ===")
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        # Send scene image first
        await bot.send_photo(
            chat_id=RON_CHAT_ID,
            photo=FSInputFile(scene_image_path),
            caption=(
                "<b>Mondo Shrimp — Scene Image (Nano Banana)</b>\n\n"
                "Product photo → subway scene with reference\n"
                f"Cost: ${image_result.cost_usd:.2f}"
            ),
        )

        # Send video
        await bot.send_video(
            chat_id=RON_CHAT_ID,
            video=FSInputFile(video_path),
            caption=(
                f"<b>Mondo Shrimp — Animated Video (Veo 3.1 Fast)</b>\n\n"
                f"Scene image animated into 5-8s clip\n"
                f"9:16 vertical (Reels/TikTok/Stories)\n\n"
                f"Pipeline: Product photo → Nano Banana scene → Veo animate\n"
                f"Total cost: ${image_result.cost_usd + video_result.cost_usd:.2f}\n"
                f"{size_mb:.1f} MB | {elapsed:.0f}s total"
            ),
        )
        logger.info("Sent to Telegram!")
    finally:
        await bot.session.close()

    # Cleanup
    for f in [scene_image_path, video_path]:
        try:
            os.remove(f)
        except OSError:
            pass

    logger.info("=== DONE in %.0fs ===", elapsed)
    logger.info("Scene: %s", os.path.join(dl_dir, "mondo_scene.jpg"))
    logger.info("Video: %s", os.path.join(dl_dir, "mondo_shrimp_video.mp4"))
    logger.info("Total cost: $%.2f", image_result.cost_usd + video_result.cost_usd)


if __name__ == "__main__":
    asyncio.run(main())
