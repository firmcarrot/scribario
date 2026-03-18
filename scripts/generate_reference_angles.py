#!/usr/bin/env python3
"""Generate 5-angle reference sheets for hero video subjects.

Uses Nano Banana 2 with reference image input to generate consistent
multi-angle views of each subject for Veo anchoring.

Usage:
    cd /home/ronald/projects/scribario
    python3 -m scripts.generate_reference_angles
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("ref-angles")

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"

# Output
OUTPUT_DIR = "/mnt/c/Users/ronal/Downloads/scribario-reference-angles"

# Source reference images (local paths — need to upload to get URLs)
CAR_REF_LOCAL = "/mnt/c/Users/ronal/Downloads/car design.jpg"
COWBOY_REF_LOCAL = "/mnt/c/Users/ronal/Downloads/man-in-western-costume-driving-horse-drawn-cart-along-old-cariboo-A25895.jpg"

# Standard negative block
NEG = (
    "Avoid: deformed hands, extra fingers, blurry faces, text overlays, "
    "subtitles, watermarks, morphing objects, floating objects, duplicate "
    "subjects, CGI quality, oversaturated colors."
)


async def upload_to_supabase(local_path: str, filename: str) -> str:
    """Upload a local file to Supabase storage and return a signed URL."""
    from supabase import create_client

    from bot.config import get_settings

    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

    bucket = "reference-images"

    # Ensure bucket exists
    try:
        supabase.storage.get_bucket(bucket)
    except Exception:
        supabase.storage.create_bucket(bucket, options={"public": False})

    # Upload
    storage_path = f"hero-video/{filename}"
    with open(local_path, "rb") as f:
        file_bytes = f.read()

    # Remove existing file if present (upsert)
    try:
        supabase.storage.from_(bucket).remove([storage_path])
    except Exception:
        pass

    supabase.storage.from_(bucket).upload(
        storage_path,
        file_bytes,
        file_options={"content-type": "image/jpeg", "upsert": "true"},
    )

    # Get signed URL (1 hour expiry — plenty for generation)
    signed = supabase.storage.from_(bucket).create_signed_url(storage_path, 3600)
    url = signed.get("signedURL", "") or signed.get("signedUrl", "")
    if not url:
        raise RuntimeError(f"Failed to get signed URL for {storage_path}: {signed}")
    logger.info("Uploaded %s → %s", filename, url[:80])
    return url


# -----------------------------------------------------------------------
# Prompts — 5 angles per subject
# -----------------------------------------------------------------------

CAR_ANGLES = [
    {
        "name": "car_front",
        "prompt": (
            "Front view of a biomechanical futuristic vehicle parked on flat desert sand at golden hour. "
            "Organic chrome exoskeleton body with flowing tentacle-like chrome fins and horns. "
            "Glowing amber-orange translucent panels along the sides and undercarriage. "
            "Chrome bug-eye headlights. Low-slung wide stance. Desert mesa silhouette behind. "
            "Shot straight-on from ground level, symmetrical composition. "
            "Golden hour sun behind camera, warm amber light on the chrome surfaces. "
            "Shot on ARRI Alexa Mini, 50mm lens, f/4, ISO 200. Automotive photography. "
            f"{NEG}"
        ),
    },
    {
        "name": "car_3q_front",
        "prompt": (
            "Three-quarter front view of a biomechanical futuristic vehicle on desert sand at golden hour. "
            "Organic chrome exoskeleton body with flowing tentacle-like fins curling from the rear. "
            "Glowing amber-orange translucent panels visible along the flanks and underneath. "
            "Chrome details, bug-eye headlights, low-slung wide body. "
            "Camera at 45 degrees to front-left, slightly below eye level. "
            "Golden hour sun from camera-right creating warm highlights on chrome curves. "
            "Shot on ARRI Alexa Mini, 35mm lens, f/4, ISO 200. Premium automotive hero shot. "
            f"{NEG}"
        ),
    },
    {
        "name": "car_side",
        "prompt": (
            "Full side profile view of a biomechanical futuristic vehicle on desert sand at golden hour. "
            "Organic chrome exoskeleton with flowing tentacle-like fins and horns sweeping backward. "
            "Glowing amber-orange translucent panels along the entire side and glowing undercarriage. "
            "Chrome details, wheels with organic spoke patterns. Long flowing aerodynamic silhouette. "
            "Camera at exact 90-degree side angle, level with the vehicle. "
            "Golden hour backlight creating dramatic rim light on chrome edges. "
            "Shot on ARRI Alexa Mini, 85mm lens, f/2.8, ISO 200. Automotive catalog photography. "
            f"{NEG}"
        ),
    },
    {
        "name": "car_3q_rear",
        "prompt": (
            "Three-quarter rear view of a biomechanical futuristic vehicle on desert sand at golden hour. "
            "Organic chrome exoskeleton with tentacle-like tail fins extending from the rear. "
            "Glowing amber-orange translucent rear panels and exhaust glow underneath. "
            "Chrome details, curving organic body lines. Desert sunset sky behind. "
            "Camera at 45 degrees to rear-right, slightly above eye level. "
            "Golden hour sun low on horizon, warm amber rim light on the chrome. "
            "Shot on ARRI Alexa Mini, 35mm lens, f/4, ISO 200. Automotive reveal shot. "
            f"{NEG}"
        ),
    },
    {
        "name": "car_rear",
        "prompt": (
            "Direct rear view of a biomechanical futuristic vehicle on desert sand at golden hour. "
            "Organic chrome exoskeleton with twin tentacle-like tail extensions curling upward. "
            "Glowing amber-orange translucent rear panel and bright orange undercarriage glow. "
            "Chrome details, organic symmetrical rear design. Desert road stretching ahead. "
            "Camera straight behind, symmetrical composition, slightly below eye level. "
            "Golden hour sun creating rim light around the vehicle silhouette. "
            "Shot on ARRI Alexa Mini, 50mm lens, f/4, ISO 200. Automotive photography. "
            f"{NEG}"
        ),
    },
]

COWBOY_ANGLES = [
    {
        "name": "cowboy_front",
        "prompt": (
            "Front view of a cowboy driving a red wooden stagecoach cart pulled by two brown draft horses "
            "on a dusty desert road. The cowboy wears tan leather jacket, blue neckerchief, brown cowboy hat. "
            "Two large Belgian draft horses in full harness with leather straps and brass buckles. "
            "Red painted cart with yellow spoked wheels. Dusty road, desert landscape behind. "
            "Camera facing the oncoming cart, low angle, horses approaching. "
            "Golden hour sun behind camera, warm light on the horses and cart. "
            "Shot on ARRI Alexa Mini, 35mm lens, f/4, ISO 400. Documentary western photography. "
            f"{NEG}"
        ),
    },
    {
        "name": "cowboy_3q_front",
        "prompt": (
            "Three-quarter front view of a cowboy driving a red wooden stagecoach cart pulled by two brown "
            "draft horses on a dusty desert road. Cowboy in tan leather jacket, blue neckerchief, brown hat, "
            "holding leather reins. Two Belgian draft horses in harness, trotting. Red cart, yellow wheels. "
            "Dust billowing behind. Desert mountains in background. "
            "Camera at 45 degrees front-left, ground level. "
            "Golden hour sun from camera-right, warm amber tones, long shadows. "
            "Shot on ARRI Alexa Mini, 50mm lens, f/2.8, ISO 400. Cinematic western. "
            f"{NEG}"
        ),
    },
    {
        "name": "cowboy_side",
        "prompt": (
            "Full side profile view of a cowboy driving a red wooden stagecoach cart pulled by two brown "
            "draft horses on a dusty desert road. Cowboy in tan leather jacket, blue neckerchief, brown hat. "
            "Two Belgian draft horses in full harness, mid-trot. Red painted cart body, yellow spoked wheels. "
            "Billowing dust trail behind. Desert landscape, clear sky. "
            "Camera at exact 90-degree side angle, level with the cart. "
            "Golden hour backlight creating warm rim light on horse manes and dust particles. "
            "Shot on ARRI Alexa Mini, 85mm lens, f/2.8, ISO 400. Western cinema photography. "
            f"{NEG}"
        ),
    },
    {
        "name": "cowboy_3q_rear",
        "prompt": (
            "Three-quarter rear view of a cowboy driving a red wooden stagecoach cart pulled by two brown "
            "draft horses down a dusty desert road. Cowboy's back visible, tan leather jacket, brown hat. "
            "Two Belgian draft horses trotting away. Red cart with yellow wheels kicking up dust. "
            "Desert road stretching into the distance, mountains on horizon. "
            "Camera at 45 degrees rear-left, slightly elevated. "
            "Golden hour sun low ahead, silhouetting the cart against warm sky. "
            "Shot on ARRI Alexa Mini, 35mm lens, f/4, ISO 400. Epic western landscape. "
            f"{NEG}"
        ),
    },
    {
        "name": "cowboy_rear",
        "prompt": (
            "Direct rear view of a cowboy driving a red wooden stagecoach cart pulled by two brown "
            "draft horses heading down a dusty desert road into the sunset. Cowboy's back centered, "
            "tan leather jacket, brown hat. Two draft horses side by side. Red cart, yellow wheels. "
            "Dust trail billowing behind. Road vanishes to horizon, golden sunset ahead. "
            "Camera straight behind, symmetrical, ground level. "
            "Golden hour sun directly ahead creating dramatic silhouette and rim light. "
            "Shot on ARRI Alexa Mini, 50mm lens, f/4, ISO 400. Iconic western composition. "
            f"{NEG}"
        ),
    },
]


async def main():
    import httpx

    from pipeline.image_gen import ImageGenerationService

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    image_service = ImageGenerationService(tenant_id=SCRIBARIO_TENANT_ID)

    # Step 1: Upload reference images to get URLs
    logger.info("=== Uploading reference images ===")
    car_ref_url = await upload_to_supabase(CAR_REF_LOCAL, "car-design-ref.jpg")
    cowboy_ref_url = await upload_to_supabase(COWBOY_REF_LOCAL, "cowboy-cart-ref.jpg")

    total_cost = 0.0

    # Step 2: Generate car angles (with car reference)
    logger.info("=== Generating Car Reference Angles (5 views) ===")
    async with httpx.AsyncClient() as client:
        for angle in CAR_ANGLES:
            logger.info("  Generating %s...", angle["name"])
            result = await image_service.generate(
                prompt=angle["prompt"],
                aspect_ratio="16:9",
                reference_image_urls=[car_ref_url],
            )
            total_cost += result.cost_usd

            # Download and save
            resp = await client.get(result.url, timeout=60.0)
            resp.raise_for_status()
            path = os.path.join(OUTPUT_DIR, f"{angle['name']}.jpg")
            with open(path, "wb") as f:
                f.write(resp.content)
            logger.info("  Saved %s (%.0f KB)", path, len(resp.content) / 1024)

    # Step 3: Generate cowboy/cart angles (with cowboy reference)
    logger.info("=== Generating Cowboy+Cart Reference Angles (5 views) ===")
    async with httpx.AsyncClient() as client:
        for angle in COWBOY_ANGLES:
            logger.info("  Generating %s...", angle["name"])
            result = await image_service.generate(
                prompt=angle["prompt"],
                aspect_ratio="16:9",
                reference_image_urls=[cowboy_ref_url],
            )
            total_cost += result.cost_usd

            # Download and save
            resp = await client.get(result.url, timeout=60.0)
            resp.raise_for_status()
            path = os.path.join(OUTPUT_DIR, f"{angle['name']}.jpg")
            with open(path, "wb") as f:
                f.write(resp.content)
            logger.info("  Saved %s (%.0f KB)", path, len(resp.content) / 1024)

    logger.info("=== DONE ===")
    logger.info("Total cost: $%.2f (10 images × $0.04)", total_cost)
    logger.info("Output: %s", OUTPUT_DIR)
    print(f"\nDONE! 10 reference images saved to {OUTPUT_DIR}")
    print(f"Cost: ${total_cost:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
