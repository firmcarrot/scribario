"""FB Banner v2 — Phone with app in action, properly centered, sharp text."""

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

# 3 variations of the phone/app center image
PROMPTS = {
    "v1": (
        "Photorealistic iPhone 15 Pro held at a slight angle showing a Telegram chat conversation "
        "on the screen. The phone is centered in frame against a solid deep navy blue (#1A1A2E) "
        "background. The chat shows colorful message bubbles — blue sent messages and white received "
        "messages with social media post previews. The phone screen is bright and glowing, creating "
        "a subtle light bloom on the dark background. Clean product photography, sharp focus, "
        "85mm lens, f/2.8. The phone should be prominent and sharp. No hands. No text outside phone. "
        "Dark navy background must be clean and uniform."
    ),
    "v2": (
        "Photorealistic iPhone 15 Pro floating at center against solid deep navy (#1A1A2E) "
        "background. Screen shows a vibrant social media management interface with colorful "
        "content cards — Instagram posts, Facebook updates, scheduled posts with images. "
        "Subtle coral-orange (#FF6B4A) glow emanating from the phone screen reflecting "
        "onto the dark background. Sharp product photography, centered composition, "
        "clean uniform dark background. No hands, no text outside the phone."
    ),
    "v3": (
        "Photorealistic iPhone 15 Pro centered against deep navy (#1A1A2E) background. "
        "The screen displays a chat interface with message bubbles and an AI-generated "
        "social media post preview — a food photo with caption text visible. "
        "Small floating holographic social media icons (Instagram, Facebook, TikTok) "
        "orbit gently around the phone, semi-transparent. Subtle coral-orange (#FF6B4A) "
        "ambient glow. Sharp professional product photography. No hands. "
        "Clean dark background."
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
    out_dir = "/home/ronald/projects/scribario/brand/fb-banners-v2"
    os.makedirs(out_dir, exist_ok=True)

    async with httpx.AsyncClient(timeout=300.0) as client:
        print("Generating 3 phone variations...")
        tasks = {label: create_and_poll(client, prompt, label) for label, prompt in PROMPTS.items()}
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        urls = {}
        for label, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                print(f"[{label}] ERROR: {result}")
            else:
                urls[label] = result

        print("\nDownloading...")
        for label, url in urls.items():
            await download(client, url, f"{out_dir}/{label}_bg.jpg")

    print("\nCompositing text on all 3...")
    composite_all(out_dir)
    print("\nDone!")


def composite_all(out_dir):
    from PIL import Image, ImageDraw, ImageFont

    # 3x resolution for sharpness: 2460x936
    W, H = 2460, 936

    # FB safe zone: center 1920x936 (640*3 x 312*3)
    # Left 600px (200*3) covered by profile pic
    # Usable text area: x=650 to x=2190 (center of that = 1420)
    # But we want VISUALLY centered on the full banner, offset slightly right
    # True center = 1230, safe center (avoiding profile pic) = ~1420
    # Split difference: put phone at true center, text offset slightly right
    SAFE_LEFT = 650  # right edge of profile pic overlap
    SAFE_RIGHT = 2190
    TEXT_CENTER = (SAFE_LEFT + SAFE_RIGHT) // 2  # 1420

    # Fonts — use the boldest available
    bold_font = None
    regular_font = None
    for fp in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        if os.path.exists(fp):
            bold_font = fp
            break
    for fp in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        if os.path.exists(fp):
            regular_font = fp
            break

    for variant in ["v1", "v2", "v3"]:
        bg_path = f"{out_dir}/{variant}_bg.jpg"
        if not os.path.exists(bg_path):
            continue

        bg = Image.open(bg_path).convert("RGBA")
        bg = bg.resize((W, H), Image.LANCZOS)
        draw = ImageDraw.Draw(bg)

        # Fonts — BIG and BOLD
        f_brand = ImageFont.truetype(bold_font, 96) if bold_font else ImageFont.load_default()
        f_tagline = ImageFont.truetype(bold_font, 44) if bold_font else ImageFont.load_default()
        f_cta = ImageFont.truetype(bold_font, 38) if bold_font else ImageFont.load_default()

        # === TOP: "SCRIBARIO" — big, white, bold ===
        brand = "SCRIBARIO"
        bb = draw.textbbox((0, 0), brand, font=f_brand)
        bw = bb[2] - bb[0]
        draw.text((TEXT_CENTER - bw // 2, 80), brand, fill="#FFFFFF", font=f_brand)

        # === TAGLINE below brand name ===
        tagline = "Your Social Media Team in a Text."
        bb = draw.textbbox((0, 0), tagline, font=f_tagline)
        tw = bb[2] - bb[0]
        draw.text((TEXT_CENTER - tw // 2, 195), tagline, fill="#FF6B4A", font=f_tagline)

        # === BOTTOM CTA pill ===
        cta = "Try it free → @ScribarioBot"
        bb = draw.textbbox((0, 0), cta, font=f_cta)
        cw, ch = bb[2] - bb[0], bb[3] - bb[1]
        cta_x = TEXT_CENTER - cw // 2
        cta_y = H - 110
        px, py = 45, 18
        draw.rounded_rectangle(
            [cta_x - px, cta_y - py, cta_x + cw + px, cta_y + ch + py],
            radius=35,
            fill="#FF6B4A",
        )
        draw.text((cta_x, cta_y), cta, fill="#FFFFFF", font=f_cta)

        # Save
        final = bg.convert("RGB")
        out_path = f"{out_dir}/{variant}_final.png"
        final.save(out_path, quality=95)
        print(f"Saved: {out_path}")

        # Copy to Downloads
        num = variant[-1]
        shutil.copy(out_path, f"/mnt/c/Users/ronal/Downloads/fb-banner-v2-{num}.png")


if __name__ == "__main__":
    asyncio.run(main())
