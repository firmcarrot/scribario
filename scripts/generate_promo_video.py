#!/usr/bin/env python3
"""Generate Scribario hero promo video — "The Text That Changed Everything."

9 scenes × ~5s each = ~45s hero video for scribario.com.
Hand-crafted prompts tuned for Nano Banana 2 (frames) + Veo 3.1 Fast (~5s clips).
More scenes = more runtime, since Veo clips are ~5s regardless of model.
Bypasses script_gen.py for full creative control.

Usage:
    cd /home/ronald/projects/scribario
    python -m scripts.generate_promo_video
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
logger = logging.getLogger("scribario-hero-promo")

SCRIBARIO_TENANT_ID = "90f86df4-6ac4-418b-8c2b-508de8d50b53"
PROJECT_ID = f"scribario-hero-{int(time.time())}"
RON_CHAT_ID = 7560539974
ASPECT_RATIO = "16:9"

# ElevenLabs "Adam" — warm, confident male narrator
VOICE_ID = "pNInz6obpgDQGcFmaJgB"

# Character bible — pasted verbatim into every scene prompt for consistency
CHARACTER = (
    "CHARACTER: Marco — early 40s, short dark hair with touches of grey at "
    "temples, warm brown skin, slight stubble, tired but kind dark brown eyes. "
    "Wearing a dark navy henley shirt with sleeves pushed up to forearms, "
    "simple silver watch on left wrist. Restaurant owner — hands show he works "
    "with them. Do not alter hair length, do not change clothing, no wardrobe "
    "change between frames."
)


def build_script():
    """Construct the hand-crafted LongVideoScript with 5 scenes.

    Every prompt follows the Veo 3.1 / Nano Banana 2 skill guidelines:
    - Narrative prose, not keywords
    - Physical light sources named (not "dramatic lighting")
    - Camera math: exact lens, aperture, ISO
    - Max 2 camera movements per clip, described physically
    - Character bible pasted verbatim
    - Standard negative block on every prompt
    - Audio direction in visual_description (shapes Veo's audio gen)
    - 100-150 words per visual prompt
    """
    from pipeline.long_video.models import LongVideoScript, Scene, SceneType

    # Standard negative block for every frame prompt
    NEG = (
        "No skin smoothing, no beautification. "
        "Avoid: deformed hands, extra fingers, blurry faces, text overlays, "
        "subtitles, watermarks, morphing objects, floating objects, duplicate "
        "subjects, background shift, CGI quality, oversaturated colors."
    )

    scenes = [
        # ================================================================
        # SCENE 1: THE PAIN (0-8s)
        # Emotion: isolation, exhaustion, "this isn't what I signed up for"
        # ================================================================
        Scene(
            index=0,
            scene_type=SceneType.A_ROLL,
            voiceover_text=(
                "You didn't start a business to spend your nights "
                "writing Instagram captions."
            ),
            visual_description=(
                f"Medium shot of a tired restaurant owner alone at a small desk "
                f"in the back of his closed restaurant, late at night. {CHARACTER} "
                f"He stares at a laptop showing a blank social media post editor, "
                f"rubbing his left temple with one hand. Half-eaten takeout "
                f"container and cold coffee on the desk. The restaurant behind "
                f"him is dark and empty — chairs stacked on tables. "
                f"Key light: laptop screen casting cool blue on his face. "
                f"Single warm practical overhead bulb far above, creating pools "
                f"of shadow. 3:1 key-to-fill ratio, deep shadows. "
                f"Camera is locked off on a tripod, no movement, slight natural "
                f"handheld micro-sway. "
                f"Faint hum of a refrigerator. A clock ticking on the wall. "
                f"No music. No dialogue."
            ),
            start_frame_prompt=(
                f"A candid photo of a tired restaurant owner sitting alone at a "
                f"small cluttered desk in the back of his closed restaurant at "
                f"night. {CHARACTER} He is staring at an open laptop, expression "
                f"exhausted and frustrated, one hand resting on his temple. "
                f"The laptop screen casts cool blue light across his face. "
                f"A single warm overhead bulb hangs far above, creating deep "
                f"shadow pools. Behind him the restaurant is dark — chairs "
                f"stacked on tables, empty dining room. Half-eaten takeout "
                f"container and a cold coffee cup on the desk. "
                f"Shot on Sony A7IV, 35mm lens, f/2.0, ISO 400. "
                f"Documentary realism. Muted desaturated tones, visible pores, "
                f"natural asymmetry, unretouched skin texture. "
                f"{NEG}"
            ),
            end_frame_prompt=(
                f"A candid photo of a tired restaurant owner leaning back in his "
                f"chair, both hands covering his face in exhaustion. {CHARACTER} "
                f"The laptop screen still glows blue in front of him. A phone on "
                f"the desk shows 11:47 PM. Papers and sticky notes scattered "
                f"across the desk. The dark empty restaurant visible behind him. "
                f"Key light: laptop screen, cool blue. Single warm overhead bulb "
                f"creates rim light on his shoulders. Deep chiaroscuro shadows. "
                f"Shot on Sony A7IV, 50mm lens, f/1.8, ISO 200. "
                f"Documentary realism. Slight asymmetry in composition. "
                f"Muted color palette, desaturated tones. "
                f"{NEG}"
            ),
            camera_direction="Locked-off tripod, no camera motion, slight natural micro-sway",
            sfx_description="Faint refrigerator hum, wall clock ticking, a tired exhale",
        ),

        # ================================================================
        # SCENE 2: THE COST (8-16s)
        # Emotion: frustration building, "enough is enough"
        # ================================================================
        Scene(
            index=1,
            scene_type=SceneType.B_ROLL,
            voiceover_text=(
                "Agencies want two grand a month. DIY takes your whole "
                "weekend. There has to be a better way."
            ),
            visual_description=(
                f"Close-up on a desk surface. {CHARACTER} Marco's hands flip "
                f"through papers — we see an agency proposal with a visible "
                f"price tag, then his hand pushes it aside to reveal a wall "
                f"calendar with weekends crossed out. His other hand reaches "
                f"for a smartphone on the desk. "
                f"Key light: warm desk lamp camera-right casting harsh directional "
                f"shadows across the paperwork. No fill light. 4:1 key-to-fill. "
                f"Camera slowly tilts upward from the desk surface toward Marco's "
                f"hand as he picks up the phone. "
                f"Paper shuffling sounds. A subtle frustrated sigh. "
                f"No music. No dialogue."
            ),
            start_frame_prompt=(
                f"A documentary-style overhead flat-lay photograph of a cluttered "
                f"desk surface at night. Scattered papers include a printed agency "
                f"proposal, a wall calendar pinned flat with red X marks across "
                f"weekends, a smartphone lying face-up showing a social media "
                f"feed, a half-empty coffee mug, and crumpled receipts. "
                f"A warm desk lamp off-frame camera-right casts harsh directional "
                f"light, creating long shadows across the paper edges. "
                f"Muted color palette with a single pop of red on the calendar "
                f"markings. "
                f"Shot on Canon R5, 24mm lens, f/8, ISO 100. Overhead angle, "
                f"editorial documentary style. Slight imperfection in arrangement "
                f"— not styled, authentic mess. "
                f"{NEG}"
            ),
            end_frame_prompt=(
                f"A close-up photograph of a man's hand reaching for a smartphone "
                f"on a messy desk. {CHARACTER} The agency proposal paper is pushed "
                f"to the side, slightly crumpled. The phone screen shows a simple "
                f"text messaging app, ready to type. The desk lamp casts warm "
                f"directional light from camera-right, creating long sharp shadows. "
                f"Shallow depth of field with the phone in sharp focus and the "
                f"scattered papers in soft bokeh behind. "
                f"Shot on Canon R5, 85mm lens, f/2.0, ISO 200. "
                f"Warm amber tones from the desk lamp. Documentary editorial "
                f"style. Natural imperfect framing. "
                f"{NEG}"
            ),
            camera_direction="Camera slowly tilts upward from desk surface to hand level",
            sfx_description="Paper shuffling and sliding, a quiet frustrated exhale",
        ),

        # ================================================================
        # SCENE 3: THE MAGIC MOMENT (16-24s)
        # Emotion: curiosity → wonder → delight
        # The product demo disguised as a story beat
        # ================================================================
        Scene(
            index=2,
            scene_type=SceneType.A_ROLL,
            voiceover_text=(
                "What if you could text one message... and your entire "
                "week of content was done?"
            ),
            visual_description=(
                f"Medium close-up of Marco's face lit by his phone screen. "
                f"{CHARACTER} He types a text message, expression shifting from "
                f"tired to curious. He hits send. A beat of silence. Then his "
                f"face softens into a genuine smile as the phone screen glows "
                f"warm orange — content previews appearing. "
                f"Key light: phone screen — warm orange glow replacing the cold "
                f"blue from Scene 1. This is the visual turning point. "
                f"Soft fill from the overhead practical, 2:1 key-to-fill. "
                f"Camera locked off, no movement. Subject centered in frame. "
                f"Phone whoosh send sound. A beat of quiet. Then a gentle "
                f"notification chime. Then another. "
                f"No music. No dialogue."
            ),
            start_frame_prompt=(
                f"A candid medium close-up photograph of a man looking down at "
                f"his smartphone, face lit by the phone screen's glow. "
                f"{CHARACTER} His expression is tired but curious — brow slightly "
                f"furrowed, lips parted, focused on the screen. He holds the "
                f"phone with both hands at chest level. "
                f"The phone screen casts a warm orange-amber glow on his face "
                f"and under-chin. A soft warm overhead practical light provides "
                f"gentle fill. Dark restaurant background in soft bokeh behind "
                f"him. 2:1 key-to-fill ratio. "
                f"Shot on Sony A7IV, 85mm lens, f/1.8, ISO 200. "
                f"Cinematic shallow depth of field. Warm color grading with "
                f"amber and orange tones. Documentary realism, visible pores, "
                f"natural skin texture. Subject centered in frame. "
                f"{NEG}"
            ),
            end_frame_prompt=(
                f"A candid medium close-up photograph of the same man now "
                f"smiling genuinely, eyes crinkled with relief, looking at his "
                f"phone screen. {CHARACTER} The phone screen casts strong warm "
                f"orange light on his face — a clear visual shift from the cold "
                f"blue of earlier. His whole posture has relaxed, shoulders "
                f"dropped, head tilted slightly. "
                f"Warm orange phone glow as key light. Soft overhead fill. "
                f"Dark restaurant bokeh background with warm string lights "
                f"visible far behind. "
                f"Shot on Sony A7IV, 85mm lens, f/1.8, ISO 200. "
                f"Warm rich color grading. Genuine human emotion captured mid- "
                f"moment. Documentary realism, not posed. "
                f"{NEG}"
            ),
            camera_direction="Locked-off tripod, no camera motion. Subject centered.",
            sfx_description=(
                "Phone screen tap, a whoosh send sound, two seconds of quiet, "
                "then a soft notification chime, then a second chime"
            ),
        ),

        # ================================================================
        # SCENE 3B: THE SEND (interstitial ~5s)
        # Emotion: anticipation — the phone lights up with results
        # ================================================================
        Scene(
            index=3,
            scene_type=SceneType.B_ROLL,
            voiceover_text="Images. Captions. Hashtags. Done.",
            visual_description=(
                f"Extreme close-up of a smartphone screen showing three social "
                f"media post previews appearing one by one in a vertical feed. "
                f"Each preview has a vibrant food photo with a polished caption "
                f"below it. The screen glows warm orange. A thumb scrolls down "
                f"slowly through the previews. "
                f"Key light: phone screen casting warm orange upward. "
                f"Dark background, all attention on the screen content. "
                f"Camera is static, locked on the screen. "
                f"Gentle notification chime sounds. "
                f"No music. No dialogue."
            ),
            start_frame_prompt=(
                f"An extreme close-up photograph of a smartphone screen showing "
                f"a vertical feed of three social media post previews. Each "
                f"preview has a vibrant professional food photograph — a pasta "
                f"dish, a cocktail, a dessert — with polished caption text "
                f"below each image. The screen background is warm orange tinted. "
                f"The phone is held at a slight angle, a thumb visible at the "
                f"bottom of frame. Dark black background behind the phone. "
                f"Phone screen glow as the only light source. "
                f"Shot on Sony A7IV, 90mm macro lens, f/2.8, ISO 200. "
                f"Product photography style, crisp focus on screen content. "
                f"{NEG}"
            ),
            end_frame_prompt=(
                f"An extreme close-up photograph of a smartphone screen showing "
                f"a social media post preview with a green checkmark and the "
                f"word 'Approved' overlaid on a vibrant food photograph. Two "
                f"more posts visible below it in the feed, ready to go. The "
                f"screen glows warm amber-orange. Thumb hovering near a button. "
                f"Dark background, phone screen is the only light source. "
                f"Shot on Sony A7IV, 90mm macro lens, f/2.8, ISO 200. "
                f"Product photography, ultra-crisp screen content. "
                f"{NEG}"
            ),
            camera_direction="Static lock-off on phone screen, no movement",
            sfx_description="Soft notification chime, then a second chime, gentle whoosh",
        ),

        # ================================================================
        # SCENE 4: THE TRANSFORMATION (24-32s)
        # Emotion: satisfaction, "it's working" — content going live
        # ================================================================
        Scene(
            index=4,
            scene_type=SceneType.B_ROLL,
            voiceover_text=(
                "Professional posts. Real images. Your voice. "
                "Posting automatically while you run your business."
            ),
            visual_description=(
                f"Close-up of a smartphone screen showing a beautiful social "
                f"media feed — three polished food photography posts visible in "
                f"a grid, each with hearts and comments. {CHARACTER} Marco's "
                f"thumb scrolls through the feed. The phone is held in one hand "
                f"at a natural angle. Behind the phone in soft bokeh, the "
                f"restaurant kitchen is alive — staff moving, flames on the "
                f"stove, steam rising from plates. "
                f"Key light: warm overhead kitchen light camera-left. Phone "
                f"screen provides secondary fill on his hand. "
                f"Camera slowly racks focus from phone screen to the busy "
                f"kitchen behind. "
                f"Kitchen sounds — sizzling, clanking pans, someone calling "
                f"'order up' in the distance. "
                f"No music. No dialogue."
            ),
            start_frame_prompt=(
                f"A close-up photograph of a man's hand holding a smartphone "
                f"showing a polished social media feed with three beautiful food "
                f"photography posts in a grid layout, each with red heart icons "
                f"and comment counts visible. {CHARACTER} The phone is held "
                f"naturally at a slight angle. Behind the phone in soft bokeh, "
                f"a busy restaurant kitchen — stainless steel surfaces, warm "
                f"overhead light, movement blur of kitchen staff. "
                f"Warm overhead kitchen light as key, phone screen glow as fill "
                f"on the hand. Natural warm color palette. "
                f"Shot on Sony A7IV, 50mm lens, f/2.0, ISO 400. "
                f"Documentary realism. Authentic moment, slightly imperfect "
                f"framing. "
                f"{NEG}"
            ),
            end_frame_prompt=(
                f"A medium shot photograph of a busy restaurant kitchen with "
                f"a man in the foreground putting his phone into his back pocket "
                f"with one hand, his other hand reaching for a plate of food "
                f"on the pass. {CHARACTER} His expression is focused and "
                f"confident — he is back to running his restaurant. Kitchen "
                f"staff visible behind him. Warm overhead lighting, steam "
                f"rising from fresh plates. Deep warm color grading. "
                f"Shot on Sony A7IV, 35mm lens, f/2.8, ISO 400. "
                f"Candid documentary realism. Motion energy, busy kitchen "
                f"atmosphere. "
                f"{NEG}"
            ),
            camera_direction="Slow rack focus from phone screen to kitchen behind",
            sfx_description=(
                "Kitchen sounds — sizzling oil, clanking pans, someone calling "
                "'order up' faintly"
            ),
        ),

        # ================================================================
        # SCENE 5B: THE CONTRAST (interstitial ~5s)
        # Emotion: juxtaposition — we see the content posting while he works
        # ================================================================
        Scene(
            index=5,
            scene_type=SceneType.B_ROLL,
            voiceover_text="Your content posts itself... while you do what you love.",
            visual_description=(
                f"Split visual: in the foreground, Marco's hands plate a "
                f"beautiful dish in the kitchen, garnishing with fresh herbs. "
                f"In the soft focus background, a wall-mounted tablet shows "
                f"a social media dashboard with scheduled posts going live, "
                f"green checkmarks appearing. The kitchen is alive with warm "
                f"light and steam. "
                f"Key light: warm overhead kitchen light. Secondary: tablet "
                f"glow in background. "
                f"Camera slowly racks focus from hands in foreground to tablet "
                f"in background. "
                f"Kitchen sounds — sizzling, a plate being set down. "
                f"No music. No dialogue."
            ),
            start_frame_prompt=(
                f"A close-up photograph of a chef's hands carefully plating a "
                f"beautiful pasta dish, adding fresh basil garnish with "
                f"precision. {CHARACTER} Warm overhead kitchen light illuminates "
                f"the dish — steam rising, vibrant colors of the food. In the "
                f"soft bokeh background, a wall-mounted tablet glows showing "
                f"a social media scheduling dashboard. Stainless steel kitchen "
                f"surfaces. Rich warm color palette. "
                f"Shot on Sony A7IV, 50mm lens, f/2.0, ISO 400. "
                f"Food photography meets documentary realism. Shallow depth "
                f"of field, hands in sharp focus, background soft. "
                f"{NEG}"
            ),
            end_frame_prompt=(
                f"A medium shot photograph of a wall-mounted tablet screen in "
                f"a restaurant kitchen showing a social media dashboard with "
                f"three posts marked 'Published' with green checkmarks. In the "
                f"foreground in soft bokeh, a chef's hands visible moving. "
                f"{CHARACTER} The tablet screen glows warmly. Kitchen "
                f"background with stainless steel and warm lighting. "
                f"Shot on Sony A7IV, 50mm lens, f/2.8, ISO 400. "
                f"Rack focus composition — tablet sharp, foreground soft. "
                f"{NEG}"
            ),
            camera_direction="Slow rack focus from foreground hands to background tablet",
            sfx_description="Sizzling pan, a plate being placed on counter, faint kitchen bustle",
        ),

        # ================================================================
        # SCENE 6: THE FREEDOM (36-44s)
        # Emotion: freedom, joy — complete contrast to Scene 1's isolation
        # ================================================================
        Scene(
            index=6,
            scene_type=SceneType.A_ROLL,
            voiceover_text=(
                "No agency. No weekend grind. "
                "Just one text... and you're done."
            ),
            visual_description=(
                f"Wide shot of a bustling restaurant during golden hour, full of "
                f"customers. {CHARACTER} Marco stands near the front greeting a "
                f"couple at the door with a warm genuine smile. His phone is in "
                f"his back pocket — he is not checking it. Warm string lights "
                f"hang across the ceiling, candles on tables, the restaurant is "
                f"alive and thriving. Golden sunset light pours through the front "
                f"windows. "
                f"Key light: golden hour sunlight through windows, warm amber, "
                f"casting long golden shadows. Practicals: string lights and "
                f"candle flames. Rich warm color palette — complete visual "
                f"opposite of Scene 1's cold blue isolation. "
                f"Camera slowly pans left, natural handheld breathing. "
                f"Restaurant ambiance — conversation murmur, clinking glasses, "
                f"distant laughter. Warm and alive. "
                f"No music. No dialogue."
            ),
            start_frame_prompt=(
                f"A candid wide shot photograph of a bustling restaurant during "
                f"golden hour. {CHARACTER} Marco stands near the front entrance "
                f"greeting a couple with a warm genuine smile, his body language "
                f"relaxed and confident, phone nowhere visible. The restaurant "
                f"is full of happy customers — couples at tables, warm string "
                f"lights draped across the ceiling, candles flickering on tables. "
                f"Golden hour sunlight pours through large front windows, casting "
                f"long warm amber shadows across the room. Rich warm color "
                f"palette — deep oranges, golden yellows, warm wood tones. "
                f"Shot on Sony A7IV, 24mm lens, f/2.8, ISO 400. "
                f"Lifestyle documentary style. Slight motion energy, candid "
                f"not posed. Natural imperfect framing. "
                f"{NEG}"
            ),
            end_frame_prompt=(
                f"A candid medium shot photograph of a restaurant owner laughing "
                f"with a customer at a table, completely relaxed and present. "
                f"{CHARACTER} Marco is mid-laugh, eyes crinkled, one hand "
                f"gesturing while talking. His phone lies face-down on the table "
                f"— he does not need it. Through the window behind them, a "
                f"beautiful orange sunset. The restaurant is full and alive. "
                f"Golden hour window light as key, warm string light practicals "
                f"as fill. Shallow depth of field isolating this genuine human "
                f"moment. Warm rich color grading, subtle 35mm film grain. "
                f"Shot on Sony A7IV, 50mm lens, f/2.0, ISO 400. "
                f"Documentary realism. Authentic moment, not posed. "
                f"{NEG}"
            ),
            camera_direction="Camera slowly pans left, natural handheld breathing and micro-sway",
            sfx_description=(
                "Warm restaurant ambiance — conversation murmur, silverware "
                "clinking, distant genuine laughter, a glass being set down"
            ),
        ),

        # ================================================================
        # SCENE 8: THE REVEAL + CTA (44-52s)
        # Emotion: confidence, mic drop, "wait — THIS was made by Scribario?"
        # Static image held via FFmpeg — NOT sent through Veo
        # ================================================================
        Scene(
            index=7,
            scene_type=SceneType.A_ROLL,
            voiceover_text=(
                "This video was proudly made using only Scribario. "
                "Your social media team... in a text. "
                "scribario dot com."
            ),
            visual_description=(
                "Clean branded end card. Warm orange background with white "
                "Scribario logo centered. Static, no camera movement. "
                "Confident, clean, minimal. Let the brand breathe. "
                "A single low confident bass note. Then silence."
            ),
            start_frame_prompt=(
                "A minimalist brand identity card. Solid warm orange background "
                "with hex color FF6B2B. A bold white stylized letter S centered "
                "in the frame with generous negative space on all sides. "
                "Subtle radial gradient — slightly darker orange at the edges, "
                "brighter at center. No shadows, no texture, no patterns. "
                "Ultra-clean flat design. Geometric precision. "
                "Perfect exposure, perfectly centered composition. "
                "Avoid: noise, grain, texture, shadows, gradients that are too "
                "strong, anything distracting from the logo."
            ),
            end_frame_prompt=(
                "A minimalist branded end card. Solid warm orange background "
                "with hex color FF6B2B. Bold white text centered in the frame "
                "reading 'scribario.com' in a clean modern sans-serif font. "
                "Below it in smaller lighter weight white text: 'Your social "
                "media team in a text.' The white S logo mark sits small in "
                "the upper-left corner. Clean professional layout with generous "
                "whitespace. Subtle radial gradient adding depth. "
                "Avoid: noise, grain, texture, extra decorations, borders."
            ),
            camera_direction="Static lock-off, absolutely no movement",
            sfx_description="A single confident low bass tone that resolves cleanly",
        ),
    ]

    return LongVideoScript(
        title="The Text That Changed Everything — Scribario Hero",
        voice_style="Warm, confident male narrator. Conversational, not corporate.",
        scenes=scenes,
    )


async def _image_to_video(image_path: str, output_path: str, duration: float = 8.0) -> None:
    """Create a static video from an image using FFmpeg. No Veo needed."""
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
    from pipeline.long_video.tts import generate_voiceover
    from pipeline.video_gen import VideoGenerationService

    settings = get_settings()
    tmp_dir = f"/tmp/scribario/{PROJECT_ID}"
    os.makedirs(tmp_dir, exist_ok=True)
    start = time.time()

    # --- 1. Build hand-crafted script (no Claude call) ---
    logger.info("=== STEP 1: Hand-Crafted Script ===")
    script = build_script()
    # Last scene is the CTA — we'll handle it separately (static image, no Veo)
    cta_scene = script.scenes[-1]
    video_scenes = script.scenes[:-1]
    logger.info("Script: %s (%d scenes, last is static CTA)", script.title, script.total_scenes)
    for s in script.scenes:
        logger.info("  Scene %d [%s]: %s", s.index, s.scene_type, s.voiceover_text[:60])

    # --- 2. TTS + SFX (parallel, ALL scenes including CTA) ---
    logger.info("=== STEP 2: TTS + SFX ===")

    async def do_tts():
        results = []
        for scene in script.scenes:
            r = await generate_voiceover(scene.voiceover_text, VOICE_ID, tmp_dir)
            logger.info("  TTS scene %d: %.1fs", scene.index, r.duration_seconds)
            results.append(r)
        return results

    async def do_sfx():
        descs = [
            {"description": s.sfx_description, "duration_seconds": 3.0}
            for s in script.scenes
        ]
        return await generate_sfx_batch(descs, output_dir=tmp_dir)

    tts_results, sfx_results = await asyncio.gather(do_tts(), do_sfx())

    # --- 3. Frames (Nano Banana 2) — ALL scenes including CTA ---
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

    # Snapshot frame costs before clip gen mutates SceneAssets in-place
    frame_cost_snapshot = sum(a.cost_usd for a in frame_assets)

    # Separate CTA frame assets from video scene assets
    cta_frame_assets = frame_assets[-1]
    video_frame_assets = frame_assets[:-1]

    # --- 4. Clips (Veo 3.1 Fast — video scenes only, CTA is static) ---
    logger.info("=== STEP 4: Clip Generation (Veo 3.1 Fast — %d video scenes) ===", len(video_scenes))
    video_service = VideoGenerationService(tenant_id=SCRIBARIO_TENANT_ID)
    video_prompts = [s.visual_description for s in video_scenes]
    clip_assets = await generate_all_clips(
        video_frame_assets, video_prompts, video_service=video_service, aspect_ratio=ASPECT_RATIO,
    )
    for ca in clip_assets:
        logger.info(
            "  Scene %d: clip=%s",
            ca.scene_index,
            "OK" if ca.video_clip_url else "FAILED",
        )

    # --- 5. Download remote clips + create CTA static video ---
    logger.info("=== STEP 5: Download Clips + Create CTA Video ===")
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

    # CTA: download the logo frame image and convert to 8s static video
    cta_image_url = cta_frame_assets.start_frame_url
    if cta_image_url:
        cta_image_path = os.path.join(tmp_dir, "cta_logo.jpg")
        async with httpx.AsyncClient() as client:
            resp = await client.get(cta_image_url, timeout=60.0)
            resp.raise_for_status()
            with open(cta_image_path, "wb") as f:
                f.write(resp.content)

        # Use TTS duration for CTA scene to ensure voiceover fits
        cta_tts_duration = tts_results[-1].duration_seconds
        cta_clip_duration = max(cta_tts_duration + 1.5, 8.0)  # At least 8s, or TTS + padding

        cta_clip_path = os.path.join(tmp_dir, f"clip_{len(local_clips)}.mp4")
        await _image_to_video(cta_image_path, cta_clip_path, duration=cta_clip_duration)
        local_clips.append(cta_clip_path)
        logger.info("  CTA static video created (%.1fs from logo frame)", cta_clip_duration)
    else:
        logger.warning("  CTA frame missing — no end card!")

    if not local_clips:
        logger.error("No clips — cannot stitch. Aborting.")
        return

    # --- 6. Stitch (FFmpeg) ---
    logger.info("=== STEP 6: FFmpeg Stitch ===")
    voiceover_paths = [r.audio_url for r in tts_results[:len(local_clips)]]
    sfx_paths = [
        r.audio_path for r in sfx_results[:len(local_clips)] if r is not None
    ]

    spec = StitchSpec(
        project_id=PROJECT_ID,
        scene_clips=local_clips,
        scene_voiceovers=voiceover_paths,
        aspect_ratio=ASPECT_RATIO,
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
    final_path = os.path.join(output_dir, "promo-hero-v3.mp4")
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
        tts_cost = sum(r.cost_usd for r in tts_results)
        clip_cost = sum(a.cost_usd for a in clip_assets)
        sfx_cost = sum(r.cost_usd for r in sfx_results if r is not None)
        total_cost = tts_cost + frame_cost_snapshot + clip_cost + sfx_cost

        await bot.send_video(
            chat_id=RON_CHAT_ID,
            video=video_file,
            caption=(
                f"<b>Scribario Hero Promo v3</b>\n"
                f"<i>\"The Text That Changed Everything\"</i>\n\n"
                f"Scenes: {script.total_scenes}\n"
                f"Duration: {result.duration_seconds:.1f}s\n"
                f"Generated in: {elapsed:.0f}s\n"
                f"Cost: ${total_cost:.2f} "
                f"(TTS ${tts_cost:.2f} + Frames ${frame_cost_snapshot:.2f} "
                f"+ Clips ${clip_cost:.2f} + SFX ${sfx_cost:.2f})\n\n"
                f"CTA end card: static logo frame (no Veo).\n"
                f"This video was proudly made using only Scribario."
            ),
            parse_mode=ParseMode.HTML,
        )
        logger.info("Video sent to Telegram chat %d", RON_CHAT_ID)
    finally:
        await bot.session.close()

    # Also copy to Windows Downloads
    dl_path = "/mnt/c/Users/ronal/Downloads/scribario-hero-promo-v3.mp4"
    try:
        shutil.copy2(final_path, dl_path)
        logger.info("Also saved to %s", dl_path)
    except OSError:
        logger.warning("Could not copy to Windows Downloads (WSL mount unavailable?)")

    # Save individual frames to Downloads for review
    frames_dir = "/mnt/c/Users/ronal/Downloads/scribario-frames-v3"
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
    logger.info("Frames saved to %s", frames_dir)

    # Cost summary
    logger.info("=== COST SUMMARY ===")
    logger.info("  TTS:    $%.2f", tts_cost)
    logger.info("  Frames: $%.2f", frame_cost_snapshot)
    logger.info("  Clips:  $%.2f (Veo 3.1 Fast × %d scenes)", clip_cost, len(video_scenes))
    logger.info("  SFX:    $%.2f", sfx_cost)
    logger.info("  CTA:    $0.00 (static image → FFmpeg)")
    logger.info("  TOTAL:  $%.2f", total_cost)

    # Clean up intermediate files
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.info("Cleaned up %s", tmp_dir)

    print(f"\nDONE! Video at {final_path}")
    print(f"Also sent to Telegram and saved to Downloads.")


if __name__ == "__main__":
    asyncio.run(main())
