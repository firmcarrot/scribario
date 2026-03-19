#!/usr/bin/env python3
"""Generate reference angles v2 — sleeker car, dusty roads, driver, mirror shot.

Usage:
    cd /home/ronald/projects/scribario
    python3 -m scripts.generate_reference_angles_v2
"""

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
logger = logging.getLogger("ref-angles-v2")

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
OUTPUT_DIR = "/mnt/c/Users/ronal/Downloads/scribario-reference-angles"

# References already uploaded from v1
CAR_REF_LOCAL = "/mnt/c/Users/ronal/Downloads/car design.jpg"
COWBOY_REF_LOCAL = "/mnt/c/Users/ronal/Downloads/man-in-western-costume-driving-horse-drawn-cart-along-old-cariboo-A25895.jpg"
ROAD_REF_LOCAL = "/mnt/c/Users/ronal/Downloads/dusty-dirt-road-stretches-into-the-horizon-under-a-cloudy-sky-photo.jpeg"

NEG = (
    "Avoid: deformed hands, extra fingers, blurry faces, text overlays, "
    "subtitles, watermarks, morphing objects, floating objects, duplicate "
    "subjects, CGI quality, oversaturated colors, tentacles, organic appendages."
)

# -----------------------------------------------------------------------
# SLEEK CAR — silver body, orange windows, glowing orange, NO tentacles
# -----------------------------------------------------------------------
CAR_PROMPTS = [
    {
        "name": "car_v2_front",
        "prompt": (
            "Front view of a sleek silver futuristic supercar parked on flat desert sand at golden hour. "
            "Clean aerodynamic body with smooth flowing curves, no appendages, no tentacles. "
            "Polished silver metallic paint. Glowing orange-amber tinted windshield and windows. "
            "Bright orange LED headlights and orange underglow illuminating the sand beneath. "
            "Low-slung wide stance, aggressive but elegant. Desert mesa silhouette behind. "
            "Camera straight-on from ground level, symmetrical composition. "
            "Golden hour sun behind camera, warm amber reflections on the silver body panels. "
            "Shot on ARRI Alexa Mini, 50mm lens, f/4, ISO 200. Premium automotive photography. "
            f"{NEG}"
        ),
    },
    {
        "name": "car_v2_3q_front",
        "prompt": (
            "Three-quarter front view of a sleek silver futuristic supercar on desert sand at golden hour. "
            "Smooth polished silver metallic body, clean aerodynamic lines, no appendages. "
            "Glowing orange-amber tinted windshield. Orange LED running lights along the front edge. "
            "Orange underglow casting warm light on the ground. Low aggressive profile. "
            "Camera at 45 degrees front-left, slightly below eye level. "
            "Golden hour sun from camera-right, warm highlights on silver curves and chrome details. "
            "Shot on ARRI Alexa Mini, 35mm lens, f/4, ISO 200. Automotive hero shot. "
            f"{NEG}"
        ),
    },
    {
        "name": "car_v2_side",
        "prompt": (
            "Full side profile of a sleek silver futuristic supercar on desert sand at golden hour. "
            "Long flowing aerodynamic silhouette. Polished silver metallic body, smooth curves. "
            "Glowing orange-amber tinted side windows revealing interior glow. "
            "Orange accent lighting along the rocker panels and wheel arches. Orange underglow. "
            "Camera at exact 90-degree side angle, level with the vehicle center. "
            "Golden hour backlight creating dramatic rim light on the silver roof line. "
            "Shot on ARRI Alexa Mini, 85mm lens, f/2.8, ISO 200. Automotive catalog shot. "
            f"{NEG}"
        ),
    },
    {
        "name": "car_v2_3q_rear",
        "prompt": (
            "Three-quarter rear view of a sleek silver futuristic supercar on desert sand at golden hour. "
            "Clean smooth silver metallic body with elegant curves tapering to the rear. "
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
            "Clean symmetrical rear design with smooth silver body panels. "
            "Full-width glowing orange LED tail light bar. Orange-amber tinted rear window. "
            "Bright orange underglow illuminating the sand. Desert road ahead. "
            "Camera straight behind, symmetrical composition, slightly below eye level. "
            "Golden hour sun creating warm rim light around the vehicle silhouette. "
            "Shot on ARRI Alexa Mini, 50mm lens, f/4, ISO 200. Automotive photography. "
            f"{NEG}"
        ),
    },
]

# -----------------------------------------------------------------------
# DRIVER — young confident guy, aviator sunglasses
# -----------------------------------------------------------------------
DRIVER_PROMPTS = [
    {
        "name": "driver_in_car",
        "prompt": (
            "Medium shot of a confident young man sitting inside a futuristic silver supercar. "
            "He wears dark aviator sunglasses and a fitted black t-shirt. Short dark hair, light stubble. "
            "Relaxed confident posture, one hand on the steering wheel. "
            "The car interior glows warm orange-amber from the tinted windows. "
            "Orange dashboard lighting illuminates his face from below. "
            "Camera from passenger side looking at the driver, slightly low angle. "
            "Warm golden light from the driver-side window. "
            "Shot on ARRI Alexa Mini, 35mm lens, f/2.0, ISO 400. Cinematic shallow DOF. "
            f"{NEG}"
        ),
    },
    {
        "name": "driver_closeup",
        "prompt": (
            "Close-up portrait of a confident young man wearing dark aviator sunglasses. "
            "Short dark hair, light stubble, sharp jawline. Slight knowing smile. "
            "Warm orange-amber light reflected in the sunglasses from a car windshield. "
            "Background is soft bokeh of a desert landscape through a car window. "
            "Golden hour warm light on his face from camera-left. "
            "Shot on ARRI Alexa Mini, 85mm lens, f/1.8, ISO 200. Portrait photography. "
            f"{NEG}"
        ),
    },
]

# -----------------------------------------------------------------------
# MONEY SHOT — rearview mirror with smile
# -----------------------------------------------------------------------
MIRROR_PROMPTS = [
    {
        "name": "mirror_smile_v1",
        "prompt": (
            "Extreme close-up of a chrome side-view mirror on a sleek silver futuristic supercar. "
            "In the mirror's reflection, a confident young man with dark aviator sunglasses smiles knowingly. "
            "Desert road and golden sunset visible in the mirror reflection behind him. "
            "The chrome mirror housing catches warm golden hour light creating bright highlights. "
            "Silver car body visible around the mirror with orange accent lighting. "
            "Shallow depth of field, mirror reflection in sharp focus. "
            "Shot on ARRI Alexa Mini, 100mm macro lens, f/2.0, ISO 200. "
            f"{NEG}"
        ),
    },
    {
        "name": "mirror_smile_v2",
        "prompt": (
            "Close-up of a chrome rearview mirror on a silver futuristic car at golden hour. "
            "The mirror reflects a young man in aviator sunglasses, grinning confidently. "
            "Dusty desert road stretches into the distance in the mirror's reflection. "
            "Warm amber sunset light bathes the chrome mirror surface. "
            "Orange-tinted car window edge visible in frame. Silver body panel in foreground bokeh. "
            "Camera focuses tight on the mirror, everything else falls to soft bokeh. "
            "Shot on ARRI Alexa Mini, 85mm lens, f/2.0, ISO 200. Cinematic detail shot. "
            f"{NEG}"
        ),
    },
]

# -----------------------------------------------------------------------
# DUSTY ROAD — 5 angles
# -----------------------------------------------------------------------
ROAD_PROMPTS = [
    {
        "name": "road_straight_ahead",
        "prompt": (
            "A long straight dusty dirt road stretching to the horizon across flat open prairie. "
            "Golden-brown grass on both sides. Dust haze hanging low over the road surface. "
            "Tire tracks in the packed earth. Vast open sky with golden hour clouds. "
            "Camera at ground level centered on the road, symmetrical vanishing point composition. "
            "Golden hour sun low ahead, warm amber light through the dust haze. "
            "Shot on ARRI Alexa Mini, 24mm lens, f/8, ISO 200. Landscape cinema. "
            f"{NEG}"
        ),
    },
    {
        "name": "road_side_angle",
        "prompt": (
            "A dusty dirt road cutting across flat desert prairie, seen from the roadside at 45 degrees. "
            "Packed brown earth with tire ruts, golden-brown grass and scrub alongside. "
            "Low dust haze drifting across the road. Vast open landscape to the horizon. "
            "Camera low, looking along the road at a diagonal angle. "
            "Golden hour sun from camera-left, long warm shadows across the road surface. "
            "Shot on ARRI Alexa Mini, 35mm lens, f/5.6, ISO 200. Western landscape. "
            f"{NEG}"
        ),
    },
    {
        "name": "road_wide_landscape",
        "prompt": (
            "Wide landscape shot of a dusty dirt road winding through vast open prairie. "
            "The road is a thin brown line cutting through golden grassland. "
            "Dust cloud hanging in the air from a recent vehicle passing. "
            "Dramatic cloudy sky above. Distant mountains or mesas on the horizon. "
            "Camera elevated slightly, wide establishing shot showing the scale of emptiness. "
            "Golden hour light, warm tones, long shadows. "
            "Shot on ARRI Alexa Mini, 24mm lens, f/8, ISO 200. Epic western establishing shot. "
            f"{NEG}"
        ),
    },
    {
        "name": "road_closeup_surface",
        "prompt": (
            "Extreme close-up of a dusty dirt road surface. Packed brown earth with cracks and small stones. "
            "Tire tracks pressed into the dry soil. Fine dust particles visible floating in golden light. "
            "Dried grass blades at the road edge in soft foreground bokeh. "
            "Low angle, camera nearly touching the ground, looking along the surface. "
            "Golden hour sun low, backlighting the dust particles into glowing amber specks. "
            "Shot on ARRI Alexa Mini, 50mm macro lens, f/2.8, ISO 200. Texture detail shot. "
            f"{NEG}"
        ),
    },
    {
        "name": "road_behind_looking_back",
        "prompt": (
            "Looking back down a dusty dirt road from behind. Fresh dust cloud billowing and settling "
            "in the air where something just passed. Road stretches back to the horizon. "
            "Golden-brown prairie on both sides. Dramatic warm sky. "
            "Camera at road level, centered, looking backward at the settling dust. "
            "Golden hour backlight illuminating the dust cloud from behind, glowing amber and gold. "
            "Shot on ARRI Alexa Mini, 24mm lens, f/5.6, ISO 200. Cinematic dust atmosphere. "
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

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    image_service = ImageGenerationService(tenant_id=SCRIBARIO_TENANT_ID)

    # Upload references
    logger.info("=== Uploading reference images ===")
    car_ref_url = await upload_to_supabase(CAR_REF_LOCAL, "car-design-ref.jpg")
    road_ref_url = await upload_to_supabase(ROAD_REF_LOCAL, "dusty-road-ref.jpg")

    total_cost = 0.0

    all_batches = [
        ("Sleek Car v2 (5 angles)", CAR_PROMPTS, [car_ref_url]),
        ("Driver (2 shots)", DRIVER_PROMPTS, [car_ref_url]),
        ("Mirror Money Shot (2 variants)", MIRROR_PROMPTS, [car_ref_url]),
        ("Dusty Road (5 angles)", ROAD_PROMPTS, [road_ref_url]),
    ]

    async with httpx.AsyncClient() as client:
        for batch_name, prompts, ref_urls in all_batches:
            logger.info("=== %s ===", batch_name)
            for item in prompts:
                logger.info("  Generating %s...", item["name"])
                result = await image_service.generate(
                    prompt=item["prompt"],
                    aspect_ratio="16:9",
                    reference_image_urls=ref_urls,
                )
                total_cost += result.cost_usd

                resp = await client.get(result.url, timeout=60.0)
                resp.raise_for_status()
                path = os.path.join(OUTPUT_DIR, f"{item['name']}.jpg")
                with open(path, "wb") as f:
                    f.write(resp.content)
                logger.info("  Saved %s (%.0f KB)", item["name"], len(resp.content) / 1024)

    logger.info("=== DONE ===")
    logger.info("Total: %d images, $%.2f", len(CAR_PROMPTS) + len(DRIVER_PROMPTS) + len(MIRROR_PROMPTS) + len(ROAD_PROMPTS), total_cost)
    logger.info("Output: %s", OUTPUT_DIR)
    print(f"\nDONE! 14 new reference images saved to {OUTPUT_DIR}")
    print(f"Cost: ${total_cost:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
