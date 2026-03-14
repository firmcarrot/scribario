"""Generate 3 FB banner variations for Scribario.

Strategy: Generate background images with Kie.ai, then composite text with PIL
for guaranteed sharp, readable text in the FB safe zone.

FB Banner specs:
- Upload: high-res (we'll do 2460x936 = 3x of 820x312)
- Safe zone: center 640x312 at display res = center 1920x936 at 3x
- Left 200px (600px at 3x) covered by profile pic on desktop
- Text must be in safe zone
"""

import asyncio
import json
import os
import shutil

import httpx

API_KEY = os.environ["KIE_AI_API_KEY"]
BASE_URL = "https://api.kie.ai"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

PROMPTS = {
    "variation_a": (
        "Professional dark navy blue (#1A1A2E) background for a social media banner. "
        "Subtle gradient from deep navy to slightly lighter navy. "
        "Abstract flowing coral-orange (#FF6B4A) light streaks and gentle glowing particles "
        "scattered across the background, like digital fireflies. "
        "Clean, modern, premium tech aesthetic. Minimal and sophisticated. "
        "The center area should be relatively clean for text overlay. "
        "No text, no logos, no people, no phones. Just the abstract background. "
        "Wide panoramic composition. Studio-quality gradient lighting."
    ),
    "variation_b": (
        "Professional dark background for a tech company social media banner. "
        "Deep navy (#1A1A2E) base with a subtle radial glow of coral-orange (#FF6B4A) "
        "emanating from the center, creating a warm spotlight effect. "
        "Floating translucent social media icons (Instagram, Facebook, TikTok, LinkedIn logos) "
        "scattered lightly around the edges, semi-transparent, like floating holograms. "
        "Clean modern aesthetic, no text. Premium SaaS feel. "
        "Wide panoramic composition. The center must be clean and uncluttered for text overlay."
    ),
    "variation_c": (
        "Professional dark navy (#1A1A2E) banner background with a sleek modern aesthetic. "
        "Left side has subtle coral-orange (#FF6B4A) geometric mesh/network lines connecting dots, "
        "like a constellation or neural network pattern. Right side fades to clean dark space. "
        "A few bright coral-orange accent dots glowing softly. "
        "Minimal, sophisticated, tech-forward but warm. "
        "No text, no logos, no people. Just the abstract background pattern. "
        "Wide panoramic composition. Center area clean for text overlay."
    ),
}


async def create_and_poll(client, prompt, label):
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "21:9",
            "resolution": "2K",
            "output_format": "jpg",
        },
    }
    resp = await client.post(f"{BASE_URL}/api/v1/jobs/createTask", headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"[{label}] createTask failed: {data}")
    task_id = data["data"]["taskId"]
    print(f"[{label}] Task: {task_id}")

    for attempt in range(90):
        resp = await client.get(f"{BASE_URL}/api/v1/jobs/recordInfo", headers=HEADERS, params={"taskId": task_id})
        resp.raise_for_status()
        td = resp.json()["data"]
        state = td.get("state", "")
        if state == "success":
            result_json = json.loads(td.get("resultJson", "{}"))
            urls = result_json.get("resultUrls", [])
            if not urls:
                raise RuntimeError(f"[{label}] No URLs")
            print(f"[{label}] Done!")
            return urls[0]
        if state in ("failed", "error"):
            raise RuntimeError(f"[{label}] Failed: {td.get('failMsg')}")
        if attempt % 10 == 0:
            print(f"[{label}] Waiting... {attempt * 2}s")
        await asyncio.sleep(2)
    raise TimeoutError(f"[{label}] Timed out")


async def download(client, url, path):
    for attempt in range(3):
        try:
            resp = await client.get(url, timeout=60.0)
            resp.raise_for_status()
            with open(path, "wb") as f:
                f.write(resp.content)
            print(f"Downloaded: {path} ({len(resp.content)/1024:.0f} KB)")
            return
        except Exception as e:
            print(f"Download retry {attempt+1}: {e}")
            await asyncio.sleep(3)
    raise RuntimeError(f"Failed to download {url}")


async def main():
    out_dir = "/home/ronald/projects/scribario/brand/fb-banners"
    os.makedirs(out_dir, exist_ok=True)

    async with httpx.AsyncClient(timeout=300.0) as client:
        # Launch all 3 in parallel
        print("Generating 3 background variations...")
        tasks = {
            label: create_and_poll(client, prompt, label)
            for label, prompt in PROMPTS.items()
        }
        urls = {}
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        for label, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                print(f"[{label}] ERROR: {result}")
            else:
                urls[label] = result

        # Download all
        print("\nDownloading backgrounds...")
        for label, url in urls.items():
            await download(client, url, f"{out_dir}/{label}_bg.jpg")

    # Now composite text on each
    print("\nCompositing text...")
    composite_banners(out_dir)
    print("\nDone! Check Downloads for all 3 variations.")


def composite_banners(out_dir):
    from PIL import Image, ImageDraw, ImageFont

    # Target: 2460x936 (3x of 820x312)
    TARGET_W, TARGET_H = 2460, 936

    # Load logo
    logo = Image.open("/home/ronald/projects/scribario/brand/logo-white-on-orange-2048.png").convert("RGBA")

    # Try to load a good font, fall back to default
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
    ]
    font_path = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_path = fp
            break

    regular_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Regular.ttf",
    ]
    regular_path = None
    for fp in regular_paths:
        if os.path.exists(fp):
            regular_path = fp
            break

    for variant in ["variation_a", "variation_b", "variation_c"]:
        bg_path = f"{out_dir}/{variant}_bg.jpg"
        if not os.path.exists(bg_path):
            print(f"Skipping {variant} — no background")
            continue

        # Load and resize background to target
        bg = Image.open(bg_path).convert("RGBA")
        bg = bg.resize((TARGET_W, TARGET_H), Image.LANCZOS)

        draw = ImageDraw.Draw(bg)

        # FB safe zone at 3x: center 1920x936
        # Left margin from safe zone: (2460 - 1920) / 2 = 270px
        # But left 600px (200px * 3) is covered by profile pic
        # So text should start at x=700 minimum (safe from profile pic overlap)
        # Right edge of safe zone: 2460 - 270 = 2190

        # Layout:
        # Top area: "SCRIBARIO" brand name (large)
        # Middle: "Your Social Media Team in a Text." tagline
        # Center: Logo
        # Bottom: CTA area

        # === LOGO (centered, moderate size) ===
        logo_size = 200
        logo_resized = logo.resize((logo_size, logo_size), Image.LANCZOS)
        logo_x = (TARGET_W - logo_size) // 2
        logo_y = (TARGET_H - logo_size) // 2 - 30  # slightly above center
        bg.paste(logo_resized, (logo_x, logo_y), logo_resized)

        # === TEXT ===
        # Brand name top
        if font_path:
            font_brand = ImageFont.truetype(font_path, 82)
            font_tagline = ImageFont.truetype(regular_path or font_path, 42)
            font_cta = ImageFont.truetype(font_path, 36)
        else:
            font_brand = ImageFont.load_default()
            font_tagline = font_brand
            font_cta = font_brand

        # "SCRIBARIO" — top, centered in safe zone
        brand_text = "SCRIBARIO"
        bbox = draw.textbbox((0, 0), brand_text, font=font_brand)
        tw = bbox[2] - bbox[0]
        # Center horizontally but offset right to account for profile pic
        text_center_x = (700 + 2190) // 2  # center of usable safe zone
        brand_x = text_center_x - tw // 2
        brand_y = 100
        draw.text((brand_x, brand_y), brand_text, fill="#FFFFFF", font=font_brand)

        # Tagline — below brand name
        tagline = "Your Social Media Team in a Text."
        bbox = draw.textbbox((0, 0), tagline, font=font_tagline)
        tw = bbox[2] - bbox[0]
        tag_x = text_center_x - tw // 2
        tag_y = brand_y + 100
        draw.text((tag_x, tag_y), tagline, fill="#FF6B4A", font=font_tagline)

        # CTA — bottom
        cta_text = "Try it free → @ScribarioBot"
        bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        cta_x = text_center_x - tw // 2
        cta_y = TARGET_H - 120

        # CTA pill background
        pill_pad_x, pill_pad_y = 40, 16
        pill_rect = [
            cta_x - pill_pad_x,
            cta_y - pill_pad_y,
            cta_x + tw + pill_pad_x,
            cta_y + th + pill_pad_y,
        ]
        draw.rounded_rectangle(pill_rect, radius=30, fill="#FF6B4A")
        draw.text((cta_x, cta_y), cta_text, fill="#FFFFFF", font=font_cta)

        # Save
        final = bg.convert("RGB")
        out_path = f"{out_dir}/{variant}_final.png"
        final.save(out_path, quality=95)
        print(f"Saved: {out_path}")

        # Copy to Downloads
        letter = variant[-1].upper()
        shutil.copy(out_path, f"/mnt/c/Users/ronal/Downloads/fb-banner-{letter}.png")


if __name__ == "__main__":
    asyncio.run(main())
