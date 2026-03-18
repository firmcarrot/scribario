#!/usr/bin/env python3
"""Generate Scribario hero video — "The Future" (Chariot vs Hovercraft).

3 Veo clips + 1 PIL CTA card = ~18s silent autoplay loop for scribario.com hero.
No voiceover — SFX only. Fast cuts, warm golden palette, cinematic.

Usage:
    cd /home/ronald/projects/scribario
    python3 -m scripts.generate_hero_future
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
logger = logging.getLogger("scribario-hero-future")

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
PROJECT_ID = f"scribario-hero-future-{int(time.time())}"
RON_CHAT_ID = 7560539974
ASPECT_RATIO = "16:9"

# Brand assets
BRAND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "brand")
LOGO_PATH = os.path.join(BRAND_DIR, "logo-orange-on-transparent-2048.png")
FONT_BOLD = os.path.join(BRAND_DIR, "fonts", "Inter-Bold.ttf")
FONT_MEDIUM = os.path.join(BRAND_DIR, "fonts", "Inter-Medium.ttf")
FONT_REGULAR = os.path.join(BRAND_DIR, "fonts", "Inter-Regular.ttf")
SCRIBARIO_ORANGE = "#FF6B2B"

# Hovercraft design bible — pasted into every prompt for consistency
HOVERCRAFT = (
    "HOVERCRAFT DESIGN: A sleek futuristic hovercraft with a matte black body. "
    "Glowing orange (#FF6B2B) accent lines run along the sides and edges. "
    "Chrome details on the front grille and mirror housings. Bright orange "
    "exhaust glow pulsing underneath the vehicle as it hovers. Futuristic "
    "aerodynamic curves, low-slung profile, no visible wheels. The design "
    "language is premium automotive meets sci-fi — think Cybertruck meets "
    "Blade Runner spinner."
)

# Standard negative block for Nano Banana 2 frames
NEG = (
    "No skin smoothing, no beautification. "
    "Avoid: deformed hands, extra fingers, blurry faces, text overlays, "
    "subtitles, watermarks, morphing objects, floating objects, duplicate "
    "subjects, background shift, CGI quality, oversaturated colors, "
    "readable text on any surface, license plates with text."
)


def build_script():
    """Construct the 3-scene video script + CTA beat.

    Every prompt follows Nano Banana 2 (frames) + Veo 3.1 Fast (clips) skills:
    - Narrative prose, not keywords
    - Physical light sources named
    - Camera math: exact lens, aperture, ISO
    - Max 2 camera movements per clip
    - Design bible pasted verbatim
    - Anti-slop negatives
    - Audio direction in visual_description (shapes Veo audio gen)
    - 100-150 words per visual prompt
    """
    from pipeline.long_video.models import LongVideoScript, Scene, SceneType

    scenes = [
        # ================================================================
        # BEAT 1: THE OLD WORLD (~5s Veo)
        # Wide cinematic. Chariot on desert road. WHOOSH — blur streaks past.
        # ================================================================
        Scene(
            index=0,
            scene_type=SceneType.A_ROLL,
            voiceover_text="",  # No voiceover — silent hero
            visual_description=(
                f"Wide cinematic shot of a dusty golden-hour desert road stretching "
                f"to the horizon. An old weathered wooden chariot pulled by a brown "
                f"horse trots slowly along, kicking up billowing dust clouds. A "
                f"weathered old-timer in dusty tan clothes and a wide-brimmed hat "
                f"cracks leather reins. Warm sepia golden tones, low sun casting "
                f"long shadows. Then — WHOOSH — a blur of matte black and glowing "
                f"orange STREAKS past frame-right at incredible speed. The horse "
                f"rears up in shock, the old timer grabs his hat, jaw dropped, dust "
                f"exploding outward in the wake. "
                f"Key light: golden hour sun low on the horizon, warm amber, casting "
                f"long golden shadows across the desert floor. "
                f"Camera is static wide shot on a tripod, the action plays out in "
                f"frame. Slight natural lens shake from the hovercraft wake. "
                f"Horse hooves on dirt, leather creak, then a massive whoosh with "
                f"bass rumble, horse whinny, dust billowing."
            ),
            start_frame_prompt=(
                f"A wide cinematic photograph of a dusty golden-hour desert road "
                f"stretching to the horizon. An old weathered wooden chariot with "
                f"large spoked wheels is pulled by a brown horse, trotting slowly. "
                f"A weathered old-timer in dusty tan clothes and a wide-brimmed hat "
                f"holds leather reins. Billowing dust clouds behind the chariot. "
                f"Golden hour sunlight from camera-left casting long warm shadows "
                f"across the cracked desert floor. Warm sepia tones, vast open sky. "
                f"Shot on ARRI Alexa Mini, 35mm lens, f/4, ISO 800. "
                f"Cinematic widescreen composition, rule of thirds, chariot in "
                f"left third moving right. Documentary realism, visible dust "
                f"particles in the golden light. "
                f"{NEG}"
            ),
            end_frame_prompt=(
                f"A wide cinematic photograph of a desert road at golden hour. The "
                f"brown horse is rearing up on its hind legs in shock, the wooden "
                f"chariot tilted behind it. The weathered old-timer is grabbing his "
                f"wide-brimmed hat with one hand, mouth open in astonishment, "
                f"looking right. A massive dust cloud billows from left to right "
                f"across the frame — the wake of something that just passed at "
                f"incredible speed. Orange-tinted motion blur streaks visible in "
                f"the dust. Golden hour light, warm amber tones. "
                f"Shot on ARRI Alexa Mini, 35mm lens, f/4, ISO 800. "
                f"Cinematic widescreen. Action frozen mid-moment, dynamic energy. "
                f"{NEG}"
            ),
            camera_direction="Static wide shot, slight natural lens shake from hovercraft wake",
            sfx_description=(
                "Horse hooves trotting on packed dirt, leather creak and jingle, "
                "then a massive deep whoosh with bass rumble passing left to right, "
                "horse whinny, dust explosion sound"
            ),
        ),

        # ================================================================
        # BEAT 2: THE REVEAL (~5s Veo)
        # Hovercraft decelerates to hover-stop. Camera orbits. Desert sunset.
        # ================================================================
        Scene(
            index=1,
            scene_type=SceneType.A_ROLL,
            voiceover_text="",
            visual_description=(
                f"The sleek hovercraft decelerates to a hovering stop on the "
                f"desert road ahead. {HOVERCRAFT} Orange accent lines pulse as "
                f"the exhaust glow underneath brightens. Dust settles around the "
                f"machine. Camera slowly orbits from rear-quarter to side profile, "
                f"revealing futuristic curves against the desert sunset. The machine "
                f"hovers two feet off the ground, sand dancing in the orange exhaust. "
                f"Key light: golden hour sun behind creating rim light with warm "
                f"orange sunset sky. Camera orbits clockwise from 7 to 3 o'clock. "
                f"Descending engine hum resolving to a hovering pulse, wind whisper."
            ),
            start_frame_prompt=(
                f"A cinematic photograph of a sleek futuristic hovercraft stopped "
                f"on a desert road, hovering two feet above the ground. {HOVERCRAFT} "
                f"Shot from the rear-quarter angle showing the back and side of the "
                f"vehicle. Orange exhaust glow underneath illuminates swirling dust "
                f"and sand particles. Desert sunset behind, sky gradient from warm "
                f"orange to deep purple. The road stretches behind into the golden "
                f"desert landscape. "
                f"Key light: sunset behind creating dramatic rim light on the "
                f"vehicle's edges. Orange accent lines glowing. "
                f"Shot on ARRI Alexa Mini, 50mm lens, f/2.8, ISO 400. "
                f"Automotive photography meets sci-fi. Rich warm color grading, "
                f"premium product shot feel. "
                f"{NEG}"
            ),
            end_frame_prompt=(
                f"A cinematic side-profile photograph of a sleek futuristic "
                f"hovercraft hovering on a desert road. {HOVERCRAFT} "
                f"Full side view showing the complete aerodynamic profile. Orange "
                f"accent lines glow along the entire length. Bright orange exhaust "
                f"pulses underneath. Desert sunset sky behind — warm orange, amber, "
                f"and deep blue. The settled dust creates a golden haze around the "
                f"machine. Sand particles float in the warm light. "
                f"Shot on ARRI Alexa Mini, 85mm lens, f/2.0, ISO 400. "
                f"Premium automotive reveal shot. Cinematic color grading, rich "
                f"warm tones, aspirational and powerful. "
                f"{NEG}"
            ),
            camera_direction="Slow clockwise orbit from rear-quarter to side profile",
            sfx_description=(
                "Descending engine hum from high pitch to deep bass, resolving "
                "to a low hovering pulse, gentle wind whisper, subtle sand "
                "particles clicking"
            ),
        ),

        # ================================================================
        # BEAT 3: THE DRIVER (~5s Veo)
        # Close-up chrome rearview mirror — confident driver. Pull back to
        # reveal full rear of hovercraft. Orange glow, golden light.
        # ================================================================
        Scene(
            index=2,
            scene_type=SceneType.A_ROLL,
            voiceover_text="",
            visual_description=(
                f"Close-up of a chrome rearview mirror on the hovercraft. In the "
                f"reflection, a confident young man with dark aviator sunglasses "
                f"smiles knowingly, desert behind him. Chrome catches golden light. "
                f"Camera slowly pulls back to reveal the full rear — {HOVERCRAFT} "
                f"Orange exhaust pulses underneath. The machine hovers, powerful "
                f"and still against the vast desert. Warm golden light. "
                f"Key light: golden hour sun camera-left, warm amber. Chrome mirror "
                f"reflects sky. Camera: extreme close-up of mirror, pulls back to "
                f"medium-wide rear view. Subtle bass pulse, warm wind, engine hum."
            ),
            start_frame_prompt=(
                f"An extreme close-up photograph of a chrome side-view mirror on a "
                f"sleek futuristic vehicle. In the mirror's reflection, a confident "
                f"young man wearing dark aviator sunglasses smiles, desert landscape "
                f"visible behind him in the reflection. The chrome mirror housing is "
                f"polished and catches warm golden sunset light, creating bright "
                f"highlights. Matte black vehicle body visible around the mirror. "
                f"Orange accent line visible along the door edge. "
                f"Shot on ARRI Alexa Mini, 100mm macro lens, f/2.0, ISO 200. "
                f"Automotive detail photography. Ultra-sharp focus on the mirror, "
                f"shallow depth of field blurring the vehicle body. Rich warm tones. "
                f"{NEG}"
            ),
            end_frame_prompt=(
                f"A medium-wide cinematic photograph of the rear view of a sleek "
                f"futuristic hovercraft hovering on a desert road at golden hour. "
                f"{HOVERCRAFT} Full rear visible — angular tail design, chrome "
                f"details, orange accent lines running across the back. Bright "
                f"orange exhaust glow underneath. The vast desert stretches behind "
                f"with golden sunset sky. Warm golden light, premium automotive "
                f"photography feel. The machine is powerful and still. "
                f"Shot on ARRI Alexa Mini, 35mm lens, f/4, ISO 400. "
                f"Cinematic automotive hero shot. Rich warm color grading. "
                f"{NEG}"
            ),
            camera_direction="Start extreme close-up on mirror, slow pull-back to medium-wide rear view",
            sfx_description=(
                "Subtle building bass pulse, warm desert wind, faint confident "
                "engine idle hum"
            ),
        ),
    ]

    return LongVideoScript(
        title="The Future — Scribario Hero",
        voice_style="",  # No voiceover
        scenes=scenes,
    )


def generate_cta_card(output_path: str) -> str:
    """Generate the CTA end card using PIL.

    Black 1920x1080 canvas with:
    - "The Future of Content Creation" — bold white, centered
    - "Your social media team in a text." — lighter, below
    - Orange S logo — center-bottom area
    - "scribario.com" — white, bottom center

    Returns path to the generated PNG.
    """
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_headline = ImageFont.truetype(FONT_BOLD, 64)
    font_subhead = ImageFont.truetype(FONT_MEDIUM, 32)
    font_url = ImageFont.truetype(FONT_REGULAR, 26)

    # Headline: "The Future of Content Creation"
    headline = "The Future of Content Creation"
    bbox = draw.textbbox((0, 0), headline, font=font_headline)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 340), headline, fill="white", font=font_headline)

    # Subheadline: "Your social media team in a text."
    subhead = "Your social media team in a text."
    bbox = draw.textbbox((0, 0), subhead, font=font_subhead)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 430), subhead, fill=(200, 200, 200), font=font_subhead)

    # Orange S logo — load and resize, place center-bottom
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        # Resize logo to ~120px height
        logo_h = 120
        logo_w = int(logo.width * (logo_h / logo.height))
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        # Center horizontally, place below subhead
        logo_x = (W - logo_w) // 2
        logo_y = 530
        img.paste(logo, (logo_x, logo_y), logo)
    else:
        # Fallback: draw an orange circle with S
        logger.warning("Logo not found at %s — using fallback", LOGO_PATH)
        draw.ellipse([(W // 2 - 50, 530), (W // 2 + 50, 630)], fill=SCRIBARIO_ORANGE)
        s_font = ImageFont.truetype(FONT_BOLD, 56)
        bbox = draw.textbbox((0, 0), "S", font=s_font)
        sw = bbox[2] - bbox[0]
        draw.text(((W - sw) / 2, 548), "S", fill="white", font=s_font)

    # URL: "scribario.com"
    url = "scribario.com"
    bbox = draw.textbbox((0, 0), url, font=font_url)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 680), url, fill=(180, 180, 180), font=font_url)

    img.save(output_path, "PNG")
    logger.info("CTA card generated: %s", output_path)
    return output_path


async def _image_to_video(image_path: str, output_path: str, duration: float = 4.0) -> None:
    """Create a static video from an image using FFmpeg."""
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
        raise RuntimeError(f"FFmpeg image→video failed: {stderr.decode()[-300:]}")


async def main():
    import httpx
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import FSInputFile

    from bot.config import get_settings
    from pipeline.image_gen import ImageGenerationService
    from pipeline.long_video.clip_gen import generate_all_clips
    from pipeline.long_video.frame_gen import generate_all_frames
    from pipeline.long_video.models import StitchSpec
    from pipeline.long_video.sfx import generate_sfx_batch
    from pipeline.long_video.stitcher import stitch
    from pipeline.video_gen import VideoGenerationService

    settings = get_settings()
    tmp_dir = f"/tmp/scribario/{PROJECT_ID}"
    os.makedirs(tmp_dir, exist_ok=True)
    start = time.time()

    # --- 1. Build hand-crafted script (3 Veo scenes, no CTA scene) ---
    logger.info("=== STEP 1: Hand-Crafted Script (The Future) ===")
    script = build_script()
    logger.info("Script: %s (%d scenes)", script.title, script.total_scenes)
    for s in script.scenes:
        logger.info("  Scene %d [%s]: %s", s.index, s.scene_type, s.sfx_description[:60])

    # --- 2. SFX only (no TTS — silent hero video) ---
    logger.info("=== STEP 2: SFX Generation ===")
    sfx_descs = [
        {"description": s.sfx_description, "duration_seconds": 5.0}
        for s in script.scenes
    ]
    sfx_results = await generate_sfx_batch(sfx_descs, output_dir=tmp_dir)
    for i, r in enumerate(sfx_results):
        if r:
            logger.info("  SFX %d: %s", i, r.audio_path)
        else:
            logger.warning("  SFX %d: FAILED", i)

    # --- 3. Frames (Nano Banana 2) ---
    logger.info("=== STEP 3: Frame Generation (Nano Banana 2) ===")
    image_service = ImageGenerationService(tenant_id=SCRIBARIO_TENANT_ID)
    frame_assets = await generate_all_frames(
        script.scenes, image_service=image_service, aspect_ratio=ASPECT_RATIO,
    )
    for a in frame_assets:
        logger.info(
            "  Scene %d: start=%s end=%s",
            a.scene_index,
            "OK" if a.start_frame_url else "FAIL",
            "OK" if a.end_frame_url else "FAIL",
        )
    frame_cost = sum(a.cost_usd for a in frame_assets)

    # --- 4. Clips (Veo 3.1 Fast — all 3 scenes) ---
    logger.info("=== STEP 4: Clip Generation (Veo 3.1 Fast × %d scenes) ===", len(script.scenes))
    video_service = VideoGenerationService(tenant_id=SCRIBARIO_TENANT_ID)
    video_prompts = [s.visual_description for s in script.scenes]
    clip_assets = await generate_all_clips(
        frame_assets, video_prompts, video_service=video_service, aspect_ratio=ASPECT_RATIO,
    )
    for ca in clip_assets:
        logger.info(
            "  Scene %d: clip=%s",
            ca.scene_index,
            "OK" if ca.video_clip_url else "FAILED",
        )

    # --- 5. Download clips + generate PIL CTA card ---
    logger.info("=== STEP 5: Download Clips + Generate CTA Card ===")
    local_clips = []
    async with httpx.AsyncClient() as client:
        for i, ca in enumerate(clip_assets):
            if ca.video_clip_url and ca.video_clip_url.startswith("http"):
                local_path = os.path.join(tmp_dir, f"clip_{i}.mp4")
                resp = await client.get(ca.video_clip_url, timeout=120.0)
                resp.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                local_clips.append(local_path)
                logger.info("  Downloaded clip %d (%.1f MB)", i, len(resp.content) / 1_000_000)
            else:
                logger.warning("  Scene %d: no clip URL, skipping", i)

    # CTA: PIL-generated end card → 4s static video
    cta_image_path = os.path.join(tmp_dir, "cta_card.png")
    generate_cta_card(cta_image_path)
    cta_clip_path = os.path.join(tmp_dir, f"clip_{len(local_clips)}.mp4")
    await _image_to_video(cta_image_path, cta_clip_path, duration=4.0)
    local_clips.append(cta_clip_path)
    logger.info("  CTA card video created (4s from PIL)")

    if not local_clips:
        logger.error("No clips — cannot stitch. Aborting.")
        return

    # --- 6. Stitch (FFmpeg) — SFX only, no voiceovers ---
    logger.info("=== STEP 6: FFmpeg Stitch (SFX only, no voiceover) ===")
    # Add a silent SFX entry for the CTA beat (bass note then silence)
    # The CTA card gets a simple low bass SFX
    cta_sfx_desc = [{"description": "A single deep confident bass tone that resolves cleanly into silence", "duration_seconds": 3.0}]
    cta_sfx_results = await generate_sfx_batch(cta_sfx_desc, output_dir=tmp_dir)
    all_sfx = sfx_results + cta_sfx_results

    sfx_paths = [r.audio_path for r in all_sfx if r is not None]
    failed_sfx = len(all_sfx) - len(sfx_paths)
    if failed_sfx > 0:
        logger.warning("%d/%d SFX failed — audio track will be incomplete", failed_sfx, len(all_sfx))
    if not sfx_paths:
        logger.error("All SFX failed — video will have no audio track")

    spec = StitchSpec(
        project_id=PROJECT_ID,
        scene_clips=local_clips,
        scene_voiceovers=[],  # No voiceover — SFX-only hero
        aspect_ratio=ASPECT_RATIO,
        transition_duration=0.3,  # Fast cuts
        sfx_volume=0.8,  # SFX is the whole audio track
        scene_sfx=sfx_paths,
    )
    result = await stitch(spec)
    logger.info(
        "Final: %s (%.1fs, %.1f MB)",
        result.output_path,
        result.duration_seconds,
        result.file_size_bytes / 1_000_000,
    )

    # Copy to output directory
    output_dir = "/tmp/scribario-output"
    os.makedirs(output_dir, exist_ok=True)
    final_path = os.path.join(output_dir, "hero-future.mp4")
    shutil.copy2(result.output_path, final_path)

    elapsed = time.time() - start
    logger.info("Pipeline complete in %.0f seconds", elapsed)
    logger.info("Output: %s", final_path)

    # --- 7. Send via Telegram ---
    logger.info("=== STEP 7: Send to Telegram ===")
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        video_file = FSInputFile(final_path)
        clip_cost = sum(a.cost_usd for a in clip_assets)
        sfx_cost = sum(r.cost_usd for r in all_sfx if r is not None)
        total_cost = frame_cost + clip_cost + sfx_cost

        await bot.send_video(
            chat_id=RON_CHAT_ID,
            video=video_file,
            caption=(
                f"<b>Scribario Hero — \"The Future\"</b>\n"
                f"<i>Chariot vs Hovercraft (silent autoplay loop)</i>\n\n"
                f"Beats: 3 Veo + 1 PIL CTA\n"
                f"Duration: {result.duration_seconds:.1f}s\n"
                f"Generated in: {elapsed:.0f}s\n"
                f"Cost: ${total_cost:.2f} "
                f"(Frames ${frame_cost:.2f} + Clips ${clip_cost:.2f} "
                f"+ SFX ${sfx_cost:.2f})\n\n"
                f"No voiceover. SFX-only. Designed as hero <code>&lt;video loop&gt;</code>."
            ),
            parse_mode=ParseMode.HTML,
        )
        logger.info("Video sent to Telegram chat %d", RON_CHAT_ID)
    finally:
        await bot.session.close()

    # Copy to Windows Downloads
    dl_path = "/mnt/c/Users/ronal/Downloads/scribario-hero-future.mp4"
    try:
        shutil.copy2(final_path, dl_path)
        logger.info("Saved to %s", dl_path)
    except OSError:
        logger.warning("Could not copy to Windows Downloads (WSL mount unavailable?)")

    # Save frames to Downloads for review
    frames_dir = "/mnt/c/Users/ronal/Downloads/scribario-frames-future"
    os.makedirs(frames_dir, exist_ok=True)
    async with httpx.AsyncClient() as client:
        for a in frame_assets:
            for label, url in [("start", a.start_frame_url), ("end", a.end_frame_url)]:
                if url:
                    try:
                        resp = await client.get(url, timeout=60.0)
                        resp.raise_for_status()
                        path = os.path.join(frames_dir, f"scene{a.scene_index}_{label}.jpg")
                        with open(path, "wb") as f:
                            f.write(resp.content)
                    except Exception:
                        pass

    # Also save the CTA card PNG
    try:
        shutil.copy2(cta_image_path, os.path.join(frames_dir, "cta_card.png"))
    except Exception:
        pass
    logger.info("Frames saved to %s", frames_dir)

    # Cost summary
    logger.info("=== COST SUMMARY ===")
    logger.info("  Frames: $%.2f (6 images: 3 scenes × start+end)", frame_cost)
    logger.info("  Clips:  $%.2f (Veo 3.1 Fast × %d scenes)", clip_cost, len(script.scenes))
    logger.info("  SFX:    $%.2f (4 beats)", sfx_cost)
    logger.info("  CTA:    $0.00 (PIL → FFmpeg)")
    logger.info("  TOTAL:  $%.2f", total_cost)

    # Clean up intermediate files
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.info("Cleaned up %s", tmp_dir)

    print(f"\nDONE! Video at {final_path}")
    print(f"Also sent to Telegram and saved to Downloads.")


if __name__ == "__main__":
    asyncio.run(main())
