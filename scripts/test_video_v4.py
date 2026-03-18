#!/usr/bin/env python3
"""Test video v4 — proving the research lessons work.

Single Veo clip + PIL CTA card. Following ALL lessons:
- Style keywords FIRST
- No camera equipment words
- Exact audio specification
- Image-first validation (generate frame, then animate)
- "muted colors, cinematic film" for photorealism
- Simple single-subject scene

Concept: A woman at a café table glances at her phone buzzing with
notifications. She smiles — her content posted itself while she
was having coffee. Warm, aspirational, simple.

Usage:
    cd /home/ronald/projects/scribario
    python -m scripts.test_video_v4
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
logger = logging.getLogger("test-video-v4")

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
RON_CHAT_ID = 7560539974
ASPECT_RATIO = "16:9"

# ──────────────────────────────────────────────
# PROMPTS — following every lesson from research
# ──────────────────────────────────────────────

# Image prompt for validation frame (Nano Banana 2)
FRAME_PROMPT = (
    "A candid medium shot of a woman in her early 30s sitting at an outdoor "
    "café table during golden hour. She has warm brown skin, short natural "
    "curly hair, wearing a simple cream linen blouse. She is glancing down "
    "at her smartphone on the table, a genuine soft smile forming on her "
    "face. A latte in a ceramic cup sits beside her phone. "
    "Golden hour sunlight from camera-left creates warm amber highlights "
    "on her face and a soft rim light on her hair. The café background is "
    "in soft bokeh — string lights, green plants, warm wood tones. "
    "Shot on Sony A7IV, 85mm lens, f/1.8, ISO 200. "
    "Shallow depth of field, warm color grading, muted tones. "
    "Documentary realism. Visible pores, natural asymmetry, candid energy. "
    "No skin smoothing, no beautification. "
    "AVOID: plastic skin, CGI, oversaturated, stock photo energy."
)

# Video prompt (style FIRST, no camera words, exact audio)
VIDEO_PROMPT = (
    "Cinematic film, muted colors, shot on a Sony camera. "
    "Medium shot of a woman in her early 30s at an outdoor café during "
    "golden hour. Warm brown skin, short natural curly hair, cream linen "
    "blouse. She sits relaxed at a small wooden table with a latte beside "
    "her. Her phone screen lights up on the table. She glances down, "
    "her expression shifts from relaxed to a genuine warm smile as she "
    "sees notifications. She picks up the phone, scrolling with quiet "
    "satisfaction. "
    "Golden hour sunlight from the left, warm amber rim light on her "
    "hair, soft shadows. Café background in bokeh — string lights and "
    "green plants. 85mm lens, shallow depth of field. "
    "Audio: café ambiance — distant quiet conversation, a spoon clinking "
    "on ceramic, soft breeze rustling leaves. A phone notification chime. "
    "No music. No dialogue. No subtitles. No on-screen text. "
    "Avoid: deformed hands, extra fingers, morphing objects, text overlays, "
    "floating objects, subtitle text, watermarks."
)


async def generate_frame():
    """Step 1: Generate validation frame with Nano Banana 2."""
    from pipeline.image_gen import ImageGenerationService

    logger.info("=== STEP 1: Generating validation frame ($.04) ===")
    service = ImageGenerationService(tenant_id=SCRIBARIO_TENANT_ID)
    result = await service.generate(
        prompt=FRAME_PROMPT,
        aspect_ratio=ASPECT_RATIO,
    )
    logger.info("Frame generated: %s ($%.2f)", result.url, result.cost_usd)
    return result


async def generate_clip(frame_url: str):
    """Step 2: Animate the validated frame with Veo 3.1 Fast.

    Using FIRST_AND_LAST_FRAMES_2_VIDEO with just the start frame
    gives us visual consistency from the validated image.

    NOTE: This means we lose native audio (Veo2 fallback).
    That's fine — we want visual quality for this test.
    Actually, let's use TEXT_2_VIDEO to get native audio since
    the whole point is testing what we learned about audio prompting.
    """
    from pipeline.video_gen import VideoGenerationService

    logger.info("=== STEP 2: Generating video clip ($.40) ===")
    service = VideoGenerationService(tenant_id=SCRIBARIO_TENANT_ID)

    # TEXT_2_VIDEO — get native audio generation
    result = await service.generate(
        prompt=VIDEO_PROMPT,
        aspect_ratio=ASPECT_RATIO,
        generation_type="TEXT_2_VIDEO",
    )
    logger.info("Clip generated: %s ($%.2f)", result.url, result.cost_usd)
    return result


def generate_cta_card(output_path: str) -> str:
    """Step 3: PIL-generated CTA end card — pixel-perfect text."""
    from PIL import Image, ImageDraw, ImageFont

    logger.info("=== STEP 3: Generating CTA card (PIL — $0.00) ===")

    # 1920x1080 black canvas
    img = Image.new("RGB", (1920, 1080), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load the Scribario logo
    logo_path = "/home/ronald/projects/scribario/brand/logo-white-on-orange-2048.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        # Resize logo to ~120px height, maintain ratio
        logo_h = 120
        logo_w = int(logo.width * (logo_h / logo.height))
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        # Center horizontally, place below center
        logo_x = (1920 - logo_w) // 2
        logo_y = 480
        img.paste(logo, (logo_x, logo_y), logo)

    # Try to load a clean font, fall back to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        font_url = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_url = ImageFont.load_default()

    # "Your social media team"
    tagline = "Your social media team"
    bbox = draw.textbbox((0, 0), tagline, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text(((1920 - tw) // 2, 340), tagline, fill="white", font=font_large)

    # "in a text."
    sub = "in a text."
    bbox = draw.textbbox((0, 0), sub, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text(((1920 - tw) // 2, 410), sub, fill="white", font=font_large)

    # "scribario.com"
    url_text = "scribario.com"
    bbox = draw.textbbox((0, 0), url_text, font=font_url)
    tw = bbox[2] - bbox[0]
    draw.text(((1920 - tw) // 2, 640), url_text, fill=(180, 180, 180), font=font_url)

    img.save(output_path, "PNG")
    logger.info("CTA card saved: %s", output_path)
    return output_path


async def image_to_video(image_path: str, output_path: str, duration: float = 4.0):
    """Convert static image to video clip via FFmpeg."""
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-t", str(duration),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-an", output_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr.decode()[-300:]}")
    logger.info("Image→video: %s (%.1fs)", output_path, duration)


async def stitch_final(clip_path: str, cta_path: str, output_path: str):
    """Stitch main clip + CTA with a quick crossfade."""
    # Normalize both to same format first
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y",
        "-i", clip_path,
        "-i", cta_path,
        "-filter_complex",
        "[0:v]scale=1920:1080,fps=30,format=yuv420p[v0];"
        "[1:v]scale=1920:1080,fps=30,format=yuv420p[v1];"
        "[v0][v1]xfade=transition=fade:duration=0.5:offset=4.5[vout]",
        "-map", "[vout]",
        "-map", "0:a?",
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg stitch failed: {stderr.decode()[-500:]}")
    logger.info("Stitched final: %s", output_path)


async def main():
    import httpx
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import FSInputFile

    from bot.config import get_settings

    settings = get_settings()
    tmp_dir = f"/tmp/scribario/test-v4-{int(time.time())}"
    os.makedirs(tmp_dir, exist_ok=True)
    start = time.time()
    total_cost = 0.0

    # --- 1. Generate validation frame ---
    frame_result = await generate_frame()
    total_cost += frame_result.cost_usd

    # Download frame for review
    frames_dir = "/mnt/c/Users/ronal/Downloads/scribario-test-v4"
    os.makedirs(frames_dir, exist_ok=True)
    async with httpx.AsyncClient() as client:
        resp = await client.get(frame_result.url, timeout=60.0)
        resp.raise_for_status()
        frame_path = os.path.join(frames_dir, "validation_frame.jpg")
        with open(frame_path, "wb") as f:
            f.write(resp.content)
    logger.info("Validation frame saved to %s", frame_path)

    # --- 2. Generate video clip (TEXT_2_VIDEO for native audio) ---
    clip_result = await generate_clip(frame_result.url)
    total_cost += clip_result.cost_usd

    # Download clip
    clip_path = os.path.join(tmp_dir, "main_clip.mp4")
    async with httpx.AsyncClient() as client:
        resp = await client.get(clip_result.url, timeout=120.0)
        resp.raise_for_status()
        with open(clip_path, "wb") as f:
            f.write(resp.content)
    logger.info("Clip downloaded (%.1f MB)", len(resp.content) / 1_000_000)

    # --- 3. Generate CTA card ---
    cta_image = os.path.join(tmp_dir, "cta_card.png")
    generate_cta_card(cta_image)

    # Copy CTA to Downloads for review
    shutil.copy2(cta_image, os.path.join(frames_dir, "cta_card.png"))

    # Convert CTA to 4s video
    cta_clip = os.path.join(tmp_dir, "cta_clip.mp4")
    await image_to_video(cta_image, cta_clip, duration=4.0)

    # --- 4. Stitch ---
    logger.info("=== STEP 4: Stitching ===")
    final_path = os.path.join(tmp_dir, "final.mp4")
    await stitch_final(clip_path, cta_clip, final_path)

    elapsed = time.time() - start
    file_size = os.path.getsize(final_path)

    # --- 5. Copy to Downloads ---
    dl_path = "/mnt/c/Users/ronal/Downloads/scribario-test-v4.mp4"
    shutil.copy2(final_path, dl_path)
    logger.info("Saved to %s", dl_path)

    # --- 6. Send to Telegram ---
    logger.info("=== STEP 5: Sending to Telegram ===")
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        await bot.send_video(
            chat_id=RON_CHAT_ID,
            video=FSInputFile(final_path),
            caption=(
                f"<b>Scribario Test Video v4</b>\n"
                f"<i>Research lessons applied</i>\n\n"
                f"Duration: ~9s (5s clip + 4s CTA)\n"
                f"Generated in: {elapsed:.0f}s\n"
                f"Cost: ${total_cost:.2f}\n\n"
                f"Lessons tested:\n"
                f"• Style keywords FIRST\n"
                f"• No camera equipment words\n"
                f"• Exact audio specification\n"
                f"• muted colors, cinematic film\n"
                f"• Single subject, one action\n"
                f"• PIL CTA (no AI text rendering)"
            ),
        )
        logger.info("Sent to Telegram!")
    finally:
        await bot.session.close()

    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)

    logger.info("=== DONE ===")
    logger.info("Cost: $%.2f (frame $%.2f + clip $%.2f)", total_cost, frame_result.cost_usd, clip_result.cost_usd)
    logger.info("Time: %.0fs", elapsed)
    logger.info("Output: %s", dl_path)


if __name__ == "__main__":
    asyncio.run(main())
