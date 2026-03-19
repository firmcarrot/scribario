#!/usr/bin/env python3
"""Regenerate mirror shots as REARVIEW mirror (interior, on windshield) not side-view."""

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
logger = logging.getLogger("fix-mirror")

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
OUTPUT_DIR = "/mnt/c/Users/ronal/Downloads/scribario-reference-angles"

# Use the clean driver closeup as reference for face consistency
DRIVER_REF = os.path.join(OUTPUT_DIR, "driver_closeup.jpg")

NEG = (
    "Avoid: deformed hands, extra fingers, blurry faces, text overlays, "
    "subtitles, watermarks, morphing objects, floating objects, duplicate "
    "subjects, CGI quality, oversaturated colors, tentacles, organic appendages."
)

MIRROR_PROMPTS = [
    {
        "name": "rearview_mirror_smile_v1",
        "prompt": (
            "Interior car shot looking at the rearview mirror mounted on the windshield. "
            "The rectangular rearview mirror reflects a confident young man with dark aviator sunglasses "
            "and a knowing smile. Short dark hair, light stubble. "
            "Through the rear window behind his reflection, a long dusty desert road stretches to the horizon. "
            "Warm orange-amber dashboard glow illuminates the interior. "
            "Camera from the back seat looking forward at the mirror. Shallow depth of field, mirror in sharp focus. "
            "Golden hour warm light flooding through the windshield. "
            "Shot on ARRI Alexa Mini, 85mm lens, f/2.0, ISO 200. Cinematic interior detail. "
            f"{NEG}"
        ),
    },
    {
        "name": "rearview_mirror_smile_v2",
        "prompt": (
            "Close-up of a rectangular rearview mirror inside a futuristic car at golden hour. "
            "In the mirror reflection, a young man wearing aviator sunglasses grins confidently. "
            "The dusty desert road and golden sunset sky are visible through the rear window in the reflection. "
            "The car interior has warm orange ambient lighting from the dashboard. "
            "Windshield frame and headliner visible around the mirror. "
            "Camera focused tight on the rearview mirror, interior falls to soft bokeh. "
            "Warm golden light from the windshield side. "
            "Shot on ARRI Alexa Mini, 100mm lens, f/2.0, ISO 200. Cinematic detail shot. "
            f"{NEG}"
        ),
    },
]

# Files to delete — old wrong side-view mirror shots
DELETE_FILES = [
    "mirror_smile_v1.jpg",
    "mirror_smile_v2.jpg",
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

    # Delete old wrong files first
    for fname in DELETE_FILES:
        path = os.path.join(OUTPUT_DIR, fname)
        if os.path.exists(path):
            os.remove(path)
            logger.info("Deleted old file: %s", fname)

    image_service = ImageGenerationService(tenant_id=SCRIBARIO_TENANT_ID)

    # Upload driver closeup as reference for face consistency
    logger.info("=== Uploading driver reference ===")
    driver_ref_url = await upload_to_supabase(DRIVER_REF, "driver-closeup-ref.jpg")

    total_cost = 0.0

    async with httpx.AsyncClient() as client:
        for item in MIRROR_PROMPTS:
            logger.info("  Generating %s...", item["name"])
            result = await image_service.generate(
                prompt=item["prompt"],
                aspect_ratio="16:9",
                reference_image_urls=[driver_ref_url],
            )
            total_cost += result.cost_usd

            resp = await client.get(result.url, timeout=60.0)
            resp.raise_for_status()
            path = os.path.join(OUTPUT_DIR, f"{item['name']}.jpg")
            with open(path, "wb") as f:
                f.write(resp.content)
            logger.info("  Saved %s (%.0f KB)", item["name"], len(resp.content) / 1024)

    logger.info("=== DONE === 2 rearview mirror shots, $%.2f", total_cost)


if __name__ == "__main__":
    asyncio.run(main())
