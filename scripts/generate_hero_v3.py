#!/usr/bin/env python3
"""Hero Video v3 — "The Future" (Horse & Buggy vs Silver Supercar).

This script generates Veo clips DIRECTLY using our approved reference images
as anchors. No Nano Banana frame generation — we feed Veo the actual reference
photos we've already reviewed and approved.

Each Veo prompt follows the skill exactly:
- 100-150 words
- ONE subject per clip
- ONE primary action
- Max 2 camera movements (described physically)
- Physical light sources named
- Audio direction embedded
- Negative block included

Scene breakdown (6-7 clips + 1 PIL CTA = ~35-40s):
1. Wide establishing — dusty road, golden hour, empty western landscape
2. Horse & buggy trotting past camera (side shot → behind)
3. WHOOSH — blur streaks past, dust explosion
4. Dust settles, silver supercar revealed, stopped on road
5. Rearview mirror — driver smiles
6. Car takes off — dust kicks up, fills the screen
7. PIL CTA — "The Future of Content Creation" + logo

Usage:
    cd /home/ronald/projects/scribario
    python3 -m scripts.generate_hero_v3
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
logger = logging.getLogger("hero-v3")

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
RON_CHAT_ID = 7560539974
OUTPUT_DIR = "/mnt/c/Users/ronal/Downloads/scribario-hero-v3"
REF_DIR = "/mnt/c/Users/ronal/Downloads/scribario-reference-angles"

# Brand assets for CTA card
BRAND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "brand")
LOGO_PATH = os.path.join(BRAND_DIR, "logo-orange-on-transparent-2048.png")
FONT_BOLD = os.path.join(BRAND_DIR, "fonts", "Inter-Bold.ttf")
FONT_MEDIUM = os.path.join(BRAND_DIR, "fonts", "Inter-Medium.ttf")
FONT_REGULAR = os.path.join(BRAND_DIR, "fonts", "Inter-Regular.ttf")

# -----------------------------------------------------------------------
# CHARACTER BIBLE — pasted verbatim into every prompt that includes him
# -----------------------------------------------------------------------
DRIVER = (
    "DRIVER: confident young man, late 20s, short dark hair, light stubble, "
    "sharp jawline, wearing dark aviator sunglasses and fitted black t-shirt."
)

# -----------------------------------------------------------------------
# CAR DESIGN BIBLE — pasted verbatim into every prompt with the car
# -----------------------------------------------------------------------
CAR = (
    "CAR: sleek silver futuristic supercar, polished silver metallic paint, "
    "clean aerodynamic curves like a McLaren or Porsche concept. Glowing "
    "orange-amber tinted windows. Orange LED accent lighting along edges. "
    "Bright orange underglow illuminating the ground beneath. No tentacles, "
    "no horns, no organic shapes, no biomechanical features."
)

# Standard negative block (from Veo skill)
NEG = (
    "Avoid: deformed hands, extra fingers, blurry faces, text overlays, "
    "subtitles, watermarks, morphing objects, jump cuts within clip, "
    "unintended camera shake, visual artifacts, floating objects, duplicate "
    "subjects, background shift. No subtitles. No on-screen text."
)

# -----------------------------------------------------------------------
# SCENE DEFINITIONS
# Each scene: ONE subject, ONE action, ONE Veo clip
# -----------------------------------------------------------------------
SCENES = [
    # SCENE 1: ESTABLISHING — empty dusty road, western atmosphere
    {
        "name": "scene1_establishing",
        "ref_image": "road_straight_ahead.jpg",
        "prompt": (
            "Wide establishing shot of a long straight dusty dirt road stretching "
            "to the horizon across flat open prairie at golden hour. "
            "Golden-brown grass on both sides. Dust haze drifting low over the road. "
            "Tire tracks in packed brown earth. Vast open sky with warm clouds. "
            "Camera locked off on tripod, completely still. The emptiness is vast. "
            "Key light: golden hour sun low on horizon, warm amber, long shadows "
            "across the prairie grass. Atmospheric haze. "
            "Shot on 35mm, natural grain, warm color grade. "
            "Wind whisper through dry grass, distant bird call, silence. No background music score. "
            f"{NEG}"
        ),
    },

    # SCENE 2: HORSE & BUGGY — side shot, trotting past camera
    {
        "name": "scene2_buggy_side",
        "ref_image": "cowboy_side.jpg",
        "prompt": (
            "Wide shot of a weathered old-timer driving a red wooden stagecoach "
            "cart pulled by two brown draft horses, trotting along a dusty dirt road "
            "at golden hour. Tan leather jacket, brown cowboy hat, blue neckerchief. "
            "Camera is static at roadside as the cart passes from left to right. "
            "Billowing dust trail behind the cart. Golden-brown prairie on both sides. "
            "Key light: golden hour sun from camera-right, warm amber rim light on "
            "the horse manes, dust particles glowing gold in the backlight. "
            "Shot on 35mm, natural grain, anamorphic feel. "
            "Horse hooves on packed dirt, wooden cart creaking, leather harness jingle. "
            "No background music score. "
            f"{NEG}"
        ),
    },

    # SCENE 3: BUGGY FROM BEHIND — trotting away down the road
    {
        "name": "scene3_buggy_behind",
        "ref_image": "cowboy_rear.jpg",
        "prompt": (
            "Wide shot from behind a weathered cowboy driving a red wooden stagecoach "
            "cart pulled by two brown draft horses, heading down a dusty desert road "
            "into the distance at golden hour. Cowboy's back centered, tan leather "
            "jacket, brown hat. Dust trail billowing behind the cart. "
            "Camera is static, the cart moves slowly away from us down the straight road. "
            "Key light: golden hour sun directly ahead, creating dramatic silhouette "
            "and warm rim light on the cowboy's hat and shoulders. "
            "Shot on 35mm, natural grain, warm western palette. "
            "Horse hooves fading, cart wheels on dirt, gentle wind. No background music score. "
            f"{NEG}"
        ),
    },

    # SCENE 4: THE WHOOSH — blur streaks past, dust explosion
    {
        "name": "scene4_whoosh",
        "ref_image": "road_behind_looking_back.jpg",
        "prompt": (
            "Wide shot of a dusty desert road at golden hour. A massive dust cloud "
            "EXPLODES across the frame as something impossibly fast streaks through "
            "from left to right — a silver metallic blur with orange light trailing "
            "behind it. The dust billows violently outward in the wake. "
            "Camera is static on tripod. The blur passes in under a second, then "
            "dust hangs thick in the warm golden air, slowly settling. "
            "Key light: golden hour sun low on horizon, backlighting the dust cloud "
            "into glowing amber and gold particles. "
            "Shot on 35mm, anamorphic lens, warm grade. "
            "Massive deep bass whoosh, air displacement rumble, dust explosion. "
            "No background music score. "
            f"{NEG}"
        ),
    },

    # SCENE 5: THE REVEAL — dust settles, silver car is stopped
    {
        "name": "scene5_car_reveal",
        "ref_image": "car_v2_3q_rear.jpg",
        "prompt": (
            f"Medium-wide shot of a dust cloud settling on a desert road at golden hour, "
            f"slowly revealing a sleek silver supercar stopped on the road. "
            f"Polished silver metallic body, orange-amber tinted windows, orange underglow. "
            f"Dust particles drift in warm golden air around the vehicle. "
            f"Camera slowly pans right, revealing the car's profile. "
            f"Key light: golden hour sun behind creating warm rim light on silver panels. "
            f"Shot on 35mm, shallow DOF, warm cinematic grade. "
            f"Settling dust, faint engine idle hum, warm wind. No background music score. "
            f"{NEG}"
        ),
    },

    # SCENE 6: REARVIEW MIRROR — driver smiles
    {
        "name": "scene6_mirror_smile",
        "ref_image": "rearview_mirror_smile_v2.jpg",
        "prompt": (
            f"Close-up of a rectangular rearview mirror inside a futuristic car at "
            f"golden hour. In the mirror reflection, a confident young man wearing "
            f"dark aviator sunglasses grins. {DRIVER} "
            f"Dusty desert road visible through the windshield behind his reflection. "
            f"Orange dashboard glow illuminates the interior. "
            f"Camera locked off, focused tight on the rearview mirror. Interior in "
            f"soft bokeh. "
            f"Key light: warm golden sun flooding through windshield from ahead. "
            f"Orange ambient from dashboard instruments. "
            f"Shot on 35mm, shallow DOF, warm grade. "
            f"Subtle confident engine idle, warm desert wind. No background music score. "
            f"{NEG}"
        ),
    },

    # SCENE 7: TAKEOFF — car launches, dust fills the screen
    {
        "name": "scene7_takeoff",
        "ref_image": "car_v2_rear.jpg",
        "prompt": (
            f"Medium-wide rear shot of a sleek silver supercar on a dusty desert road "
            f"at golden hour. Orange-amber windows, orange underglow, polished silver body. "
            f"The car LAUNCHES forward with explosive acceleration. Massive dust cloud "
            f"erupts from rear wheels and billows toward camera until dust fills the frame. "
            f"Camera is static behind the car. Car shrinks to a dot, dust overtakes. "
            f"Key light: golden hour backlight, sun low ahead, rim light on dust. "
            f"Shot on 35mm, anamorphic, warm grade. "
            f"Engine roar building to scream, tire spin, dust explosion, "
            f"then muffled silence. No background music score. "
            f"{NEG}"
        ),
    },
]


async def upload_ref_image(local_path: str, filename: str) -> str:
    """Upload a reference image to Supabase storage, return signed URL."""
    from supabase import create_client

    from bot.config import get_settings

    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

    bucket = "reference-images"
    try:
        supabase.storage.get_bucket(bucket)
    except Exception:
        supabase.storage.create_bucket(bucket, options={"public": False})

    storage_path = f"hero-video-v3/{filename}"
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

    signed = supabase.storage.from_(bucket).create_signed_url(storage_path, 14400)
    url = signed.get("signedURL", "") or signed.get("signedUrl", "")
    if not url:
        raise RuntimeError(f"Failed to get signed URL for {storage_path}: {signed}")
    return url


def generate_cta_card(output_path: str) -> str:
    """Generate CTA end card with PIL — clean text that AI can't render."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_headline = ImageFont.truetype(FONT_BOLD, 64)
    font_subhead = ImageFont.truetype(FONT_MEDIUM, 32)
    font_url = ImageFont.truetype(FONT_REGULAR, 26)

    headline = "The Future of Content Creation"
    bbox = draw.textbbox((0, 0), headline, font=font_headline)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 340), headline, fill="white", font=font_headline)

    subhead = "Your social media team in a text."
    bbox = draw.textbbox((0, 0), subhead, font=font_subhead)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 430), subhead, fill=(200, 200, 200), font=font_subhead)

    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_h = 120
        logo_w = int(logo.width * (logo_h / logo.height))
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        logo_x = (W - logo_w) // 2
        img.paste(logo, (logo_x, 530), logo)
    else:
        logger.warning("Logo not found at %s", LOGO_PATH)

    url_text = "scribario.com"
    bbox = draw.textbbox((0, 0), url_text, font=font_url)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 680), url_text, fill=(180, 180, 180), font=font_url)

    img.save(output_path, "PNG")
    logger.info("CTA card generated: %s", output_path)
    return output_path


async def image_to_video(image_path: str, output_path: str, duration: float = 4.0) -> None:
    """Create static video from image with silent audio track using FFmpeg.

    MUST include a silent audio stream so acrossfade works when stitching.
    """
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-t", str(duration),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=24",
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        output_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr.decode()[-300:]}")


async def main():
    import httpx
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import FSInputFile

    from bot.config import get_settings
    from pipeline.video_gen import VideoGenerationService

    settings = get_settings()
    tmp_dir = f"/tmp/scribario/hero-v3-{int(time.time())}"
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start = time.time()

    video_service = VideoGenerationService(tenant_id=SCRIBARIO_TENANT_ID)
    total_cost = 0.0

    # ---------------------------------------------------------------
    # STEP 1: Upload all reference images we'll need
    # ---------------------------------------------------------------
    logger.info("=== STEP 1: Upload Reference Images ===")

    # Collect unique ref image filenames across all scenes
    all_refs: set[str] = set()
    for scene in SCENES:
        all_refs.add(scene["ref_image"])

    ref_urls: dict[str, str] = {}
    for ref_name in sorted(all_refs):
        local_path = os.path.join(REF_DIR, ref_name)
        if not os.path.exists(local_path):
            logger.warning("Ref image not found: %s", local_path)
            continue
        # Retry upload up to 3 times (transient SSL errors on WSL2)
        for attempt in range(3):
            try:
                url = await upload_ref_image(local_path, ref_name)
                ref_urls[ref_name] = url
                logger.info("  Uploaded %s", ref_name)
                break
            except Exception as e:
                if attempt < 2:
                    logger.warning("  Upload failed for %s (attempt %d): %s — retrying...", ref_name, attempt + 1, e)
                    await asyncio.sleep(3)
                else:
                    raise

    logger.info("  %d reference images uploaded", len(ref_urls))

    # ---------------------------------------------------------------
    # STEP 2: Generate Veo clips — one per scene, sequentially
    # ---------------------------------------------------------------
    logger.info("=== STEP 2: Generate Veo Clips (%d scenes) ===", len(SCENES))

    local_clips: list[str] = []
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=30, read=300, write=30, pool=30)) as client:
        for i, scene in enumerate(SCENES):
            logger.info("  [%d/%d] %s", i + 1, len(SCENES), scene["name"])

            # Resolve single reference image URL for this scene
            ref_name = scene["ref_image"]
            ref_url = ref_urls.get(ref_name)

            if ref_url:
                gen_type = "REFERENCE_2_VIDEO"
                image_urls = [ref_url]
            else:
                gen_type = "TEXT_2_VIDEO"
                image_urls = None
                logger.warning("    Missing ref: %s — using TEXT_2_VIDEO", ref_name)

            logger.info("    gen_type=%s, ref=%s", gen_type, ref_name)

            try:
                result = await video_service.generate(
                    prompt=scene["prompt"],
                    aspect_ratio="16:9",
                    generation_type=gen_type,
                    image_urls=image_urls,
                )
            except Exception as e:
                logger.error("    FAILED: %s — retrying once...", e)
                await asyncio.sleep(5)
                result = await video_service.generate(
                    prompt=scene["prompt"],
                    aspect_ratio="16:9",
                    generation_type=gen_type,
                    image_urls=image_urls,
                )
            total_cost += result.cost_usd
            logger.info("    Clip generated ($%.2f)", result.cost_usd)

            # Download clip
            resp = await client.get(result.url, timeout=120.0)
            resp.raise_for_status()
            clip_path = os.path.join(tmp_dir, f"clip_{i:02d}_{scene['name']}.mp4")
            with open(clip_path, "wb") as f:
                f.write(resp.content)
            local_clips.append(clip_path)
            logger.info("    Saved %s (%.1f MB)", scene["name"], len(resp.content) / 1_000_000)

            # Save clip to output dir for review
            review_path = os.path.join(OUTPUT_DIR, f"{scene['name']}.mp4")
            shutil.copy2(clip_path, review_path)

    # ---------------------------------------------------------------
    # STEP 3: Generate CTA card (PIL → FFmpeg)
    # ---------------------------------------------------------------
    logger.info("=== STEP 3: CTA Card ===")
    cta_png = os.path.join(tmp_dir, "cta_card.png")
    generate_cta_card(cta_png)
    cta_clip = os.path.join(tmp_dir, "clip_99_cta.mp4")
    await image_to_video(cta_png, cta_clip, duration=4.0)
    local_clips.append(cta_clip)
    shutil.copy2(cta_png, os.path.join(OUTPUT_DIR, "cta_card.png"))

    # ---------------------------------------------------------------
    # STEP 4: Stitch (FFmpeg) — Veo native audio, no separate SFX
    # ---------------------------------------------------------------
    logger.info("=== STEP 4: Stitch ===")

    # Veo generates native audio in each clip. We don't need separate SFX.
    # The stitcher will use the audio tracks already embedded in the clips.
    # We pass empty voiceovers and empty SFX — the clips have their own audio.

    # First, let's just concat with crossfades using ffmpeg directly
    # since the stitcher expects separate audio tracks.
    final_path = os.path.join(tmp_dir, "hero-v3-final.mp4")

    if len(local_clips) == 1:
        shutil.copy2(local_clips[0], final_path)
    else:
        # Build FFmpeg xfade + acrossfade command
        transition = 0.3
        cmd = ["ffmpeg", "-y"]
        for clip in local_clips:
            cmd.extend(["-i", clip])

        # Video xfade chain
        n = len(local_clips)
        filter_parts = []
        prev_label = "[0:v]"

        # We need clip durations to calculate xfade offsets
        # Probe each clip for duration
        durations = []
        for clip in local_clips:
            probe = await asyncio.create_subprocess_exec(
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", clip,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await probe.communicate()
            dur = float(stdout.decode().strip())
            durations.append(dur)
            logger.info("    Clip %s: %.2fs", os.path.basename(clip), dur)

        # Calculate xfade offsets
        # offset_i = sum(durations[0..i]) - i * transition_duration
        offset = durations[0] - transition
        for i in range(1, n):
            if i < n - 1:
                out_label = f"[v{i}]"
            else:
                out_label = "[vout]"

            filter_parts.append(
                f"{prev_label}[{i}:v]xfade=transition=fade:duration={transition}:"
                f"offset={round(offset, 3)}{out_label}"
            )
            prev_label = out_label
            if i < n - 1:
                offset = round(offset + durations[i] - transition, 3)

        # Audio crossfade chain
        prev_audio = "[0:a]"
        for i in range(1, n):
            if i < n - 1:
                out_label = f"[a{i}]"
            else:
                out_label = "[aout]"

            filter_parts.append(
                f"{prev_audio}[{i}:a]acrossfade=d={transition}:c1=tri:c2=tri{out_label}"
            )
            prev_audio = out_label

        filter_complex = ";".join(filter_parts)
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            final_path,
        ])

        logger.info("    Running FFmpeg stitch...")
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error("FFmpeg stitch failed: %s", stderr.decode()[-500:])
            # Fallback: simple concat without transitions
            logger.info("    Falling back to simple concat...")
            concat_file = os.path.join(tmp_dir, "concat.txt")
            with open(concat_file, "w") as f:
                for clip in local_clips:
                    f.write(f"file '{clip}'\n")
            proc2 = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_file,
                "-c:v", "libx264", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                final_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr2 = await proc2.communicate()
            if proc2.returncode != 0:
                raise RuntimeError(f"FFmpeg concat also failed: {stderr2.decode()[-300:]}")

    # Get final video info
    probe = await asyncio.create_subprocess_exec(
        "ffprobe", "-v", "error", "-show_entries", "format=duration,size",
        "-of", "default=noprint_wrappers=1:nokey=1", final_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await probe.communicate()
    lines = stdout.decode().strip().split("\n")
    final_duration = float(lines[0])
    final_size = int(lines[1])

    elapsed = time.time() - start
    logger.info("=== COMPLETE ===")
    logger.info("  Duration: %.1fs", final_duration)
    logger.info("  Size: %.1f MB", final_size / 1_000_000)
    logger.info("  Cost: $%.2f (%d clips × $0.40)", total_cost, len(SCENES))
    logger.info("  Time: %.0fs", elapsed)

    # ---------------------------------------------------------------
    # STEP 5: Copy to Downloads + Send to Telegram
    # ---------------------------------------------------------------
    dl_path = "/mnt/c/Users/ronal/Downloads/scribario-hero-v3.mp4"
    try:
        shutil.copy2(final_path, dl_path)
        logger.info("  Saved to %s", dl_path)
    except OSError:
        logger.warning("  Could not copy to Windows Downloads")

    logger.info("=== Sending to Telegram ===")
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        video_file = FSInputFile(final_path)
        await bot.send_video(
            chat_id=RON_CHAT_ID,
            video=video_file,
            caption=(
                f"<b>Scribario Hero v3 — \"The Future\"</b>\n"
                f"<i>Horse & Buggy vs Silver Supercar</i>\n\n"
                f"Clips: {len(SCENES)} Veo + 1 PIL CTA\n"
                f"Duration: {final_duration:.1f}s\n"
                f"Generated in: {elapsed:.0f}s\n"
                f"Cost: ${total_cost:.2f}\n\n"
                f"Reference-anchored. No frame gen. By the book."
            ),
            parse_mode=ParseMode.HTML,
        )
        logger.info("  Sent to Telegram")
    finally:
        await bot.session.close()

    # Individual clips are already saved in OUTPUT_DIR for review
    logger.info("  Individual clips saved to %s", OUTPUT_DIR)

    print(f"\nDONE! {final_duration:.1f}s video")
    print(f"Final: {dl_path}")
    print(f"Clips: {OUTPUT_DIR}")
    print(f"Cost: ${total_cost:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
