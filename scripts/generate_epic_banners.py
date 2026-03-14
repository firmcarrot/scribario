"""Generate 3 EPIC Facebook banners for Scribario using proper Nano Banana 2 prompting.

Dense Narrative Format with camera math, material physics, lighting behavior.
No more generic corporate garbage.
"""

import asyncio
import json
import os
import shutil

import httpx

API_KEY = os.environ["KIE_AI_API_KEY"]
BASE_URL = "https://api.kie.ai"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
OUT_DIR = "/home/ronald/projects/scribario/brand/fb-banners-epic"

# === EPIC PROMPT 1: "The Command Center" ===
# Cinematic overhead shot of a creative workspace with social media exploding out of a phone
PROMPT_1 = (
    "Cinematic wide-angle photograph shot from a dramatic low angle looking up at a massive "
    "glowing smartphone floating vertically in the center of frame, surrounded by an explosive "
    "burst of colorful social media content — vibrant Instagram posts, Facebook cards, TikTok "
    "videos, LinkedIn articles — all flying outward from the phone screen like a supernova of "
    "content. Each piece of floating content is a sharp, detailed miniature social media post "
    "with vivid food photography, lifestyle shots, and product images. The phone screen glows "
    "bright coral-orange (#FF6B4A) casting volumetric light rays through the scene. "
    "Deep navy (#1A1A2E) background fading to black at edges. Dramatic rim lighting on each "
    "floating content card creating depth. Tiny glowing particles and light streaks connecting "
    "the phone to each content piece like energy trails. "
    "Shot with a 24mm wide-angle lens, f/2.8, ISO 200. Cinematic color grading with teal "
    "shadows and warm coral highlights. Volumetric fog catching the light from the phone. "
    "The scene feels like a moment frozen in time — content exploding outward with motion blur "
    "on the edges of each card. Ultra-sharp center focus with progressive bokeh toward edges. "
    "Premium 3D render quality mixed with photorealistic lighting. No text anywhere in the image. "
    "No people. No hands. The phone is the hero."
)

# === EPIC PROMPT 2: "The Neon Social Galaxy" ===
# Abstract cosmic scene — social media icons as constellations, phone as the sun
PROMPT_2 = (
    "Hyper-detailed cinematic photograph of an abstract cosmic scene where a glowing smartphone "
    "sits at the center like a sun, radiating brilliant coral-orange (#FF6B4A) light. "
    "Orbiting around it are luminous social media platform icons — Instagram camera, Facebook F, "
    "TikTok music note, LinkedIn in — each rendered as glowing neon holograms floating in "
    "deep space. Between the orbiting icons, streams of light connect them like a constellation "
    "map or neural network. Tiny thumbnails of social media posts float like stars in the "
    "background — food photos, product shots, lifestyle images — each sharp and colorful but "
    "small, creating a galaxy of content. "
    "The deep navy (#1A1A2E) space background has subtle nebula clouds in coral and teal. "
    "Lens flare from the central phone glow. Volumetric light beams radiating outward. "
    "Shot with a 35mm lens, f/1.4, ISO 100. Anamorphic lens flare stretching horizontally. "
    "Cinematic aspect ratio composition with the phone slightly left of center for dynamic balance. "
    "Every surface has realistic light interaction — the neon icons cast colored reflections "
    "on nearby floating content cards. Subtle chromatic aberration at the extreme edges. "
    "The overall feeling is epic, vast, and powerful — like commanding an entire social media "
    "universe from one device. No text. No people."
)

# === EPIC PROMPT 3: "The Creative Explosion" ===
# A phone cracking open with creative energy pouring out — paint, photos, light
PROMPT_3 = (
    "Explosive cinematic photograph of a smartphone in the center of frame with its screen "
    "shattering outward in slow motion, but instead of glass, what's erupting from the screen "
    "is pure creative energy — streams of vivid coral-orange (#FF6B4A) liquid light, "
    "sharp photographs of food and products tumbling outward, colorful social media post "
    "mockups spinning through the air, paint splashes in coral and teal, golden sparkles "
    "and lens flares. The eruption is symmetrical and beautiful, like a controlled explosion "
    "of creativity. "
    "The phone itself is sleek titanium, reflecting the colorful chaos around it. "
    "Deep navy (#1A1A2E) background provides maximum contrast. The flying content pieces "
    "include recognizable social media post formats — square Instagram posts with vivid food "
    "photography, landscape Facebook posts with lifestyle images, vertical TikTok frames. "
    "Each piece is tack-sharp with its own micro-lighting. "
    "Shot with a 50mm lens, f/2.0, ISO 200. High-speed photography freeze-frame aesthetic — "
    "individual droplets of coral light suspended in air, each catching light. "
    "Subtle motion trails on the outer elements. Center phone razor sharp. "
    "Professional product photography lighting from above creating defined shadows. "
    "Harold Edgerton-inspired high-speed photography meets modern CGI. "
    "No text anywhere. No hands. No people. Pure visual spectacle."
)

PROMPTS = {"epic_1": PROMPT_1, "epic_2": PROMPT_2, "epic_3": PROMPT_3}

NEGATIVE = (
    "text, words, letters, typography, watermark, logo, blurry, soft focus, "
    "low resolution, pixelated, cartoon, illustration, flat design, clip art, "
    "corporate stock photo, generic, boring, template, plain background, "
    "skin smoothing, plastic skin, AI artifacts, deformed objects, "
    "ugly, amateur, cheap looking, dark muddy colors"
)


async def create_and_poll(client, prompt, neg, label):
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "negative_prompt": neg,
            "aspect_ratio": "21:9",
            "resolution": "4K",
            "output_format": "png",
        },
    }
    resp = await client.post(f"{BASE_URL}/api/v1/jobs/createTask", headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"[{label}] createTask failed: {data}")
    task_id = data["data"]["taskId"]
    print(f"[{label}] Task: {task_id}")

    for attempt in range(120):  # 4 min max for 4K
        resp = await client.get(
            f"{BASE_URL}/api/v1/jobs/recordInfo",
            headers=HEADERS,
            params={"taskId": task_id},
        )
        resp.raise_for_status()
        td = resp.json()["data"]
        state = td.get("state", "")
        if state == "success":
            rj = json.loads(td.get("resultJson", "{}"))
            urls = rj.get("resultUrls", [])
            if not urls:
                raise RuntimeError(f"[{label}] No URLs")
            print(f"[{label}] DONE!")
            return urls[0]
        if state in ("failed", "error"):
            raise RuntimeError(f"[{label}] Failed: {td.get('failMsg')}")
        if attempt % 15 == 0:
            print(f"[{label}] Generating... {attempt * 2}s")
        await asyncio.sleep(2)
    raise TimeoutError(f"[{label}] Timed out")


async def download(client, url, path):
    for att in range(5):
        try:
            resp = await client.get(url, timeout=120.0)
            resp.raise_for_status()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(resp.content)
            print(f"  Saved: {path} ({len(resp.content)/1024:.0f} KB)")
            return
        except Exception as e:
            print(f"  Download retry {att+1}: {e}")
            await asyncio.sleep(5)
    raise RuntimeError(f"Failed all downloads for {url}")


async def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    async with httpx.AsyncClient(timeout=300.0) as client:
        print("=== GENERATING 3 EPIC BANNERS (4K, 21:9) ===\n")

        # Launch all 3 in parallel
        coros = {
            label: create_and_poll(client, prompt, NEGATIVE, label)
            for label, prompt in PROMPTS.items()
        }
        results = await asyncio.gather(*coros.values(), return_exceptions=True)

        urls = {}
        for label, result in zip(coros.keys(), results):
            if isinstance(result, Exception):
                print(f"[{label}] ERROR: {result}")
            else:
                urls[label] = result

        print(f"\n=== DOWNLOADING {len(urls)} IMAGES ===\n")
        for label, url in urls.items():
            path = f"{OUT_DIR}/{label}.png"
            await download(client, url, path)
            # Also copy to Downloads
            num = label.split("_")[1]
            dl_path = f"/mnt/c/Users/ronal/Downloads/scribario-banner-{num}.png"
            shutil.copy(path, dl_path)
            print(f"  -> Copied to Downloads: scribario-banner-{num}.png")

    print("\n=== ALL DONE — CHECK YOUR DOWNLOADS ===")


if __name__ == "__main__":
    asyncio.run(main())
