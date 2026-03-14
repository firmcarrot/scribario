"""FB Banner v3 — Properly designed. Phone center image + PIL text compositing.

3 variations with different phone/center images.
All text rendered in PIL with Inter Bold for guaranteed sharpness.
"""

import asyncio
import json
import os
import shutil

import httpx
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation, label

API_KEY = os.environ["KIE_AI_API_KEY"]
BASE_URL = "https://api.kie.ai"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
OUT_DIR = "/home/ronald/projects/scribario/brand/fb-banners-v3"
FONTS = "/home/ronald/projects/scribario/brand/fonts"

# Banner dimensions (3x for sharpness, FB displays at 820x312)
W, H = 2460, 936

# Colors
NAVY = (26, 26, 46)
CORAL = (255, 107, 74)
WHITE = (255, 255, 255)
NEAR_BLACK = (15, 15, 35)

# 3 phone variations
PHONE_PROMPTS = {
    "A": (
        "A single iPhone 15 Pro floating straight upright against a solid deep navy blue "
        "(#1A1A2E) background. The phone screen shows a Telegram chat conversation with "
        "blue and white message bubbles, including a preview of a social media post with "
        "a food photo and caption text. The phone is perfectly centered and facing the camera "
        "straight-on. Clean, sharp product photography. Subtle glow from the screen illuminating "
        "the area around the phone. No hands. No tilting. Phone perfectly vertical and centered."
    ),
    "B": (
        "A single iPhone 15 Pro floating upright against solid deep navy (#1A1A2E) background. "
        "The screen shows a social media dashboard with colorful post cards — one with a food "
        "photo, one with a landscape photo, each with AI-generated captions below them and "
        "approve/reject buttons. Bright vivid screen colors contrasting the dark background. "
        "Clean product photography. Phone centered, straight-on view. No hands. Subtle warm "
        "orange glow around the phone edges."
    ),
    "C": (
        "A single iPhone 15 Pro floating upright against solid deep navy (#1A1A2E) background. "
        "The screen shows a chat app with a conversation: a user's text message at top, then "
        "an AI response showing 3 generated social media image options in a row with colorful "
        "photos and approval buttons below. The interface is clean and modern. Phone centered, "
        "perfectly vertical, facing camera. Clean product photography. No hands. "
        "Subtle coral-orange (#FF6B4A) light reflections on the phone frame."
    ),
}


async def create_and_poll(client, prompt, label):
    payload = {
        "model": "nano-banana-2",
        "input": {"prompt": prompt, "aspect_ratio": "9:16", "resolution": "2K", "output_format": "png"},
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
            rj = json.loads(td.get("resultJson", "{}"))
            urls = rj.get("resultUrls", [])
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
    for att in range(3):
        try:
            resp = await client.get(url, timeout=60.0)
            resp.raise_for_status()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(resp.content)
            print(f"Downloaded: {path} ({len(resp.content)/1024:.0f} KB)")
            return
        except Exception as e:
            print(f"  retry {att+1}: {e}")
            await asyncio.sleep(3)


def remove_bg(img_path):
    """Remove background from phone image using color-based removal."""
    img = Image.open(img_path).convert("RGBA")
    data = np.array(img)
    r, g, b = data[:, :, 0].astype(int), data[:, :, 1].astype(int), data[:, :, 2].astype(int)

    # Dark navy background
    dark = (r < 50) & (g < 50) & (b < 70)

    # Protect the phone screen (white/bright) and its bezel
    bright = (r > 200) & (g > 200) & (b > 200)
    screen_zone = binary_dilation(bright, iterations=20)
    bezel = dark & screen_zone

    bg = dark & ~bezel

    # Keep largest connected subject
    subject = ~bg
    labeled, _ = label(subject)
    sizes = np.bincount(labeled.ravel())
    sizes[0] = 0
    largest = sizes.argmax()
    final_bg = ~(labeled == largest)

    data[final_bg] = [0, 0, 0, 0]

    # Soft edges
    edge = binary_dilation(final_bg, iterations=2) & ~final_bg
    data[edge, 3] = 200

    return Image.fromarray(data)


def build_banner(phone_img, variant_label):
    """Build the complete banner with PIL."""
    # Create background — gradient from near-black to navy
    banner = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(banner)

    # Gradient background
    for y in range(H):
        t = y / H
        r = int(NEAR_BLACK[0] + (NAVY[0] - NEAR_BLACK[0]) * t)
        g = int(NEAR_BLACK[1] + (NAVY[1] - NEAR_BLACK[1]) * t)
        b = int(NEAR_BLACK[2] + (NAVY[2] - NEAR_BLACK[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Add subtle coral glow in center
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    cx, cy = W // 2, H // 2
    for radius in range(400, 0, -2):
        alpha = int(12 * (1 - radius / 400))
        glow_draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(255, 107, 74, alpha),
        )
    banner = Image.alpha_composite(banner, glow)
    draw = ImageDraw.Draw(banner)

    # === PHONE IMAGE — centered ===
    # Scale phone to fit nicely in center (~60% of banner height)
    phone_h = int(H * 0.78)
    pw, ph = phone_img.size
    scale = phone_h / ph
    phone_w = int(pw * scale)
    phone_resized = phone_img.resize((phone_w, phone_h), Image.LANCZOS)

    # Center the phone, but shift right slightly to account for profile pic overlap
    # Profile pic covers left 600px at 3x, so shift phone center slightly right
    phone_x = (W // 2) - (phone_w // 2) + 80
    phone_y = (H - phone_h) // 2
    banner.paste(phone_resized, (phone_x, phone_y), phone_resized)

    # === TEXT — using Inter Bold ===
    f_brand = ImageFont.truetype(f"{FONTS}/Inter-Bold.ttf", 100)
    f_tagline = ImageFont.truetype(f"{FONTS}/Inter-SemiBold.ttf", 42)
    f_cta = ImageFont.truetype(f"{FONTS}/Inter-Bold.ttf", 34)

    # Text goes to the RIGHT of the phone
    text_left = phone_x + phone_w + 60
    text_right = W - 80
    text_cx = (text_left + text_right) // 2

    # Check if there's enough room on the right
    right_space = text_right - text_left
    if right_space < 500:
        # Not enough room — put text ABOVE and BELOW the phone instead
        # Recenter text to the full safe zone
        text_cx = (650 + 2190) // 2

        # "SCRIBARIO" above phone
        bb = draw.textbbox((0, 0), "SCRIBARIO", font=f_brand)
        bw = bb[2] - bb[0]
        draw.text((text_cx - bw // 2, 40), "SCRIBARIO", fill=WHITE, font=f_brand)

        # Tagline below brand
        tag = "Your Social Media Team in a Text."
        bb = draw.textbbox((0, 0), tag, font=f_tagline)
        tw = bb[2] - bb[0]
        draw.text((text_cx - tw // 2, 155), tag, fill=CORAL, font=f_tagline)

        # CTA at bottom
        cta = "Try it free \u2192 @ScribarioBot"
        bb = draw.textbbox((0, 0), cta, font=f_cta)
        cw, ch = bb[2] - bb[0], bb[3] - bb[1]
        cx = text_cx - cw // 2
        cy = H - 95
        px, py = 45, 16
        draw.rounded_rectangle(
            [cx - px, cy - py, cx + cw + px, cy + ch + py],
            radius=30, fill=CORAL,
        )
        draw.text((cx, cy), cta, fill=WHITE, font=f_cta)
    else:
        # Text on the right side of phone
        # "SCRIBARIO" — vertically centered, right side
        mid_y = H // 2

        bb = draw.textbbox((0, 0), "SCRIBARIO", font=f_brand)
        bw, bh = bb[2] - bb[0], bb[3] - bb[1]
        draw.text((text_cx - bw // 2, mid_y - bh - 60), "SCRIBARIO", fill=WHITE, font=f_brand)

        # Tagline
        tag = "Your Social Media Team\nin a Text."
        bb = draw.textbbox((0, 0), tag, font=f_tagline)
        tw = bb[2] - bb[0]
        draw.text((text_cx - tw // 2, mid_y + 10), tag, fill=CORAL, font=f_tagline)

        # CTA
        cta = "Try it free \u2192 @ScribarioBot"
        bb = draw.textbbox((0, 0), cta, font=f_cta)
        cw, ch = bb[2] - bb[0], bb[3] - bb[1]
        cx = text_cx - cw // 2
        cy = mid_y + 130
        px, py = 40, 14
        draw.rounded_rectangle(
            [cx - px, cy - py, cx + cw + px, cy + ch + py],
            radius=28, fill=CORAL,
        )
        draw.text((cx, cy), cta, fill=WHITE, font=f_cta)

    # Save
    final = banner.convert("RGB")
    path = f"{OUT_DIR}/banner_{variant_label}.png"
    final.save(path, quality=95)
    print(f"Saved: {path}")
    shutil.copy(path, f"/mnt/c/Users/ronal/Downloads/fb-banner-{variant_label}.png")
    return path


async def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    async with httpx.AsyncClient(timeout=300.0) as client:
        print("Generating 3 phone images...")
        tasks = {l: create_and_poll(client, p, l) for l, p in PHONE_PROMPTS.items()}
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        urls = {}
        for label, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                print(f"[{label}] ERROR: {result}")
            else:
                urls[label] = result

        print("\nDownloading...")
        for label, url in urls.items():
            await download(client, url, f"{OUT_DIR}/phone_{label}.png")

    # Process each
    for label in ["A", "B", "C"]:
        phone_path = f"{OUT_DIR}/phone_{label}.png"
        if not os.path.exists(phone_path):
            continue
        print(f"\nProcessing {label}...")
        phone_cutout = remove_bg(phone_path)
        build_banner(phone_cutout, label)

    print("\nAll done! Check Downloads for fb-banner-A/B/C.png")


if __name__ == "__main__":
    asyncio.run(main())
