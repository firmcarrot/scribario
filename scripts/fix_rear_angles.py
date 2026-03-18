#!/usr/bin/env python3
"""Regenerate car rear angles using clean front/side as reference instead of original."""

from __future__ import annotations

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("fix-rear")

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
OUTPUT_DIR = "/mnt/c/Users/ronal/Downloads/scribario-reference-angles"

# Use the CLEAN front image as reference (not the original biomechanical design)
CLEAN_CAR_REF = os.path.join(OUTPUT_DIR, "car_v2_front.jpg")

NEG = (
    "Avoid: deformed hands, extra fingers, blurry faces, text overlays, "
    "subtitles, watermarks, morphing objects, floating objects, duplicate "
    "subjects, CGI quality, oversaturated colors, tentacles, organic appendages, "
    "horns, fins, biomechanical, alien, creature-like features."
)

REAR_PROMPTS = [
    {
        "name": "car_v2_3q_rear",
        "prompt": (
            "Three-quarter rear view of a sleek silver futuristic supercar on desert sand at golden hour. "
            "Clean smooth silver metallic body with elegant curves tapering to the rear. "
            "Similar to a McLaren or Porsche concept car. No organic shapes, no horns, no fins, no tentacles. "
            "Glowing orange-amber tinted rear window. Bright orange LED tail lights in a horizontal bar. "
            "Orange exhaust glow and underglow. Desert sunset sky behind. "
            "Camera at 45 degrees rear-right, slightly above eye level. "
            "Golden hour sun low on horizon, warm amber rim light on the silver body. "
            "Shot on ARRI Alexa Mini, 35mm lens, f/4, ISO 200. Automotive reveal shot. "
            f"{NEG}"
        ),
    },
    {
        "name": "car_v2_rear",
        "prompt": (
            "Direct rear view of a sleek silver futuristic supercar on desert sand at golden hour. "
            "Clean symmetrical rear design with smooth silver body panels. No horns, no fins, no tentacles. "
            "Similar to a McLaren or Lamborghini rear end — flat, wide, aggressive but clean. "
            "Full-width glowing orange LED tail light bar. Orange-amber tinted rear window. "
            "Bright orange underglow illuminating the sand. Desert road ahead. "
            "Camera straight behind, symmetrical composition, slightly below eye level. "
            "Golden hour sun creating warm rim light around the vehicle silhouette. "
            "Shot on ARRI Alexa Mini, 50mm lens, f/4, ISO 200. Automotive photography. "
            f"{NEG}"
        ),
    },
]


async def upload_to_supabase(local_path: str, filename: str) -> str:
    """Upload a local file to Supabase storage and return a signed URL."""
    from supabase import create_client

    from bot.config import get_settings

    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

    bucket = "reference-images"
    try:
        supabase.storage.get_bucket(bucket)
    except Exception:
        supabase.storage.create_bucket(bucket, options={"public": False})

    storage_path = f"hero-video/{filename}"
    with open(local_path, "rb") as f:
        file_bytes = f.read()

    try:
        supabase.storage.from_(bucket).remove([storage_path])
    except Exception:
        pass

    supabase.storage.from_(bucket).upload(
        storage_path,
        file_bytes,
        file_options={"content-type": "image/jpeg", "upsert": "true"},
    )

    signed = supabase.storage.from_(bucket).create_signed_url(storage_path, 3600)
    url = signed.get("signedURL", "") or signed.get("signedUrl", "")
    if not url:
        raise RuntimeError(f"Failed to get signed URL for {storage_path}: {signed}")
    logger.info("Uploaded %s → %s", filename, url[:80])
    return url


async def main():
    import httpx

    from pipeline.image_gen import ImageGenerationService

    image_service = ImageGenerationService(tenant_id=SCRIBARIO_TENANT_ID)

    # Upload the CLEAN front render as reference (not the original design)
    logger.info("=== Uploading clean car front as reference ===")
    clean_ref_url = await upload_to_supabase(CLEAN_CAR_REF, "car-v2-front-ref.jpg")

    total_cost = 0.0

    async with httpx.AsyncClient() as client:
        for item in REAR_PROMPTS:
            logger.info("  Generating %s...", item["name"])
            result = await image_service.generate(
                prompt=item["prompt"],
                aspect_ratio="16:9",
                reference_image_urls=[clean_ref_url],
            )
            total_cost += result.cost_usd

            resp = await client.get(result.url, timeout=60.0)
            resp.raise_for_status()
            path = os.path.join(OUTPUT_DIR, f"{item['name']}.jpg")
            with open(path, "wb") as f:
                f.write(resp.content)
            logger.info("  Saved %s (%.0f KB)", item["name"], len(resp.content) / 1024)

    logger.info("=== DONE === 2 rear angles fixed, $%.2f", total_cost)


if __name__ == "__main__":
    asyncio.run(main())
