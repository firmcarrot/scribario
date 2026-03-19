#!/usr/bin/env python3
"""Stitch hero video + CTA logo reveal end card.

Takes the hero video and appends a 4-second logo reveal CTA:
1. PIL: dark-to-orange gradient bg + Scribario logo + tagline + URL
2. FFmpeg: stitch video + CTA card with crossfade

Usage:
    cd /home/ronald/projects/scribario
    python3 -m scripts.stitch_hero_cta
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("hero-stitch")

from PIL import Image, ImageDraw, ImageFont

RON_CHAT_ID = 7560539974

HERO_VIDEO = "/mnt/c/Users/ronal/Downloads/2ba3328b11e8f525accbaa6e70988990_1773700115_k1f2lypr.mp4"
LOGO_PATH = "/mnt/c/Users/ronal/Downloads/scribario-logo/scribario-logo-full-1920x1080.png"

# Video dimensions (960x960, 1:1)
W, H = 960, 960


def create_cta_card(output_path: str) -> None:
    """Create logo reveal CTA card — dark bg with orange logo + white text."""
    logger.info("Creating CTA card with PIL...")

    # Dark background matching the video's warm tones
    bg = Image.new("RGBA", (W, H), (20, 15, 10, 255))

    # Subtle radial warm glow in center
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    cx, cy = W // 2, H // 2
    for r in range(400, 0, -2):
        alpha = int(40 * (r / 400))
        draw_ov.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(255, 107, 43, alpha),
        )
    bg = Image.alpha_composite(bg, overlay)

    draw = ImageDraw.Draw(bg)

    # Load fonts
    try:
        font_large = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48
        )
        font_medium = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28
        )
        font_url = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
        )
    except OSError:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_url = ImageFont.load_default()

    # Logo — centered, prominent
    logo = Image.open(LOGO_PATH).convert("RGBA")
    # Logo is 1920x1080, crop to the S icon area (center square-ish)
    # Scale to fit nicely in 960x960
    logo_h = 300
    logo_w = int(logo.width * (logo_h / logo.height))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    logo_x = (W - logo_w) // 2
    logo_y = 200
    bg.paste(logo, (logo_x, logo_y), logo)

    # Re-create draw after paste
    draw = ImageDraw.Draw(bg)

    # Tagline — centered below logo
    tagline = "The Future of Content Creation"
    bbox = draw.textbbox((0, 0), tagline, font=font_large)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    y = 540
    draw.text((x, y), tagline, fill=(255, 255, 255, 255), font=font_large)

    # Subtitle
    subtitle = "Your social media team in a text."
    bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    y = 610
    draw.text((x, y), subtitle, fill=(200, 200, 200, 230), font=font_medium)

    # URL
    url_text = "scribario.com"
    bbox = draw.textbbox((0, 0), url_text, font=font_url)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    y = 700
    draw.text((x, y), url_text, fill=(255, 107, 43, 255), font=font_url)

    # Save as RGB
    bg_rgb = bg.convert("RGB")
    bg_rgb.save(output_path, quality=95)
    logger.info("CTA card saved: %s", output_path)


def main():
    import time

    start = time.time()

    # 1. Create CTA card
    logger.info("=== STEP 1: Create CTA card ===")
    cta_image = "/tmp/cta_card.jpg"
    create_cta_card(cta_image)

    # 2. Convert CTA image to 4s video with silent audio
    logger.info("=== STEP 2: Convert CTA to video ===")
    cta_video = "/tmp/cta_video.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", cta_image,
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-c:v", "libx264", "-t", "4", "-pix_fmt", "yuv420p",
            "-vf", f"scale={W}:{H}", "-r", "24",
            "-c:a", "aac", "-b:a", "128k", "-shortest",
            cta_video,
        ],
        capture_output=True,
    )
    logger.info("CTA video created: 4s")

    # 3. Normalize hero video
    logger.info("=== STEP 3: Normalize hero video ===")
    hero_norm = "/tmp/hero_normalized.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", HERO_VIDEO,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-vf", f"scale={W}:{H}", "-r", "24",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
            hero_norm,
        ],
        capture_output=True,
    )
    logger.info("Hero normalized")

    # 4. Get hero duration for crossfade offset
    probe = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", hero_norm,
        ],
        capture_output=True, text=True,
    )
    hero_duration = float(probe.stdout.strip())
    fade_duration = 0.8
    fade_start = hero_duration - fade_duration
    logger.info("Hero: %.1fs, fade at %.1fs", hero_duration, fade_start)

    # 5. Stitch with crossfade
    logger.info("=== STEP 4: Stitch with crossfade ===")
    final_path = "/tmp/scribario_hero_final.mp4"
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", hero_norm, "-i", cta_video,
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={fade_start}[v];"
            f"[0:a][1:a]acrossfade=d={fade_duration}[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "128k",
            final_path,
        ],
        capture_output=True, text=True,
    )

    if result.returncode != 0 or not os.path.exists(final_path) or os.path.getsize(final_path) < 1000:
        logger.warning("Crossfade failed (%s), using simple concat...", result.stderr[-200:] if result.stderr else "unknown")
        concat_file = "/tmp/concat_list.txt"
        with open(concat_file, "w") as f:
            f.write(f"file '{hero_norm}'\n")
            f.write(f"file '{cta_video}'\n")
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_file, "-c", "copy", final_path,
            ],
            capture_output=True,
        )

    size_mb = os.path.getsize(final_path) / 1e6
    logger.info("Final video: %.1f MB", size_mb)

    elapsed = time.time() - start

    # 6. Save to Downloads
    dl_dir = "/mnt/c/Users/ronal/Downloads/scribario-hero-video"
    os.makedirs(dl_dir, exist_ok=True)
    final_dl = os.path.join(dl_dir, "hero_final_with_cta.mp4")
    shutil.copy2(final_path, final_dl)
    shutil.copy2(final_path, "/mnt/c/Users/ronal/Downloads/scribario-hero-final.mp4")
    shutil.copy2(cta_image, os.path.join(dl_dir, "cta_card.jpg"))

    logger.info("=== DONE in %.0fs ===", elapsed)
    logger.info("Output: %s", final_dl)
    logger.info("Also: /mnt/c/Users/ronal/Downloads/scribario-hero-final.mp4")

    # Cleanup temp files
    for f in [cta_image, cta_video, hero_norm, final_path]:
        try:
            os.remove(f)
        except OSError:
            pass


if __name__ == "__main__":
    main()
