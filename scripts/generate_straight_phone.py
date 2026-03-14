"""Generate perfectly straight-on hand holding iPhone on green screen."""

import asyncio
import json
import os
import shutil
import numpy as np
from PIL import Image
import httpx

API_KEY = os.environ["KIE_AI_API_KEY"]
BASE_URL = "https://api.kie.ai"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

PROMPT = (
    "Photorealistic photograph of a right human hand holding an iPhone 15 Pro perfectly "
    "straight and vertical, screen facing directly at the camera with ZERO angle, ZERO tilt, "
    "ZERO perspective distortion. The phone screen edges are perfectly parallel vertical and "
    "horizontal lines forming a perfect flat rectangle. "
    "The phone screen is solid bright green (#00FF00), completely uniform with no reflections "
    "or glare. The entire background behind the hand and phone is also solid bright green "
    "(#00FF00) — a perfectly uniform chroma key green screen with zero variation. "
    "The hand grips naturally from the bottom-right, fingers wrapped around the sides and back, "
    "thumb on the right side. The hand does NOT cover any of the screen area. "
    "iPhone 15 Pro with Dynamic Island notch at top, thin black bezels, metallic titanium "
    "frame edges visible. The phone takes up approximately 65% of the image height. "
    "Soft natural lighting from above-left, subtle shadow from the hand onto the phone body. "
    "No harsh reflections on the screen. Real skin texture on the hand — visible pores, "
    "knuckle creases, natural nail ridges, subtle skin tone variation. "
    "85mm lens, f/4.0, ISO 100. Professional product photography. "
    "Do not tilt the phone. Do not angle the phone. Do not rotate the phone. "
    "The screen must be a perfect rectangle with parallel edges. "
    "Do not add any UI, app content, or reflections to the green screen. "
    "Do not beautify or smooth the hand. No AI smoothing."
)

NEGATIVE = (
    "tilted phone, angled perspective, rotated device, transparent background, "
    "checkered pattern, black background, white background, screen reflections, "
    "screen glare, UI on screen, app content on screen, text on screen, "
    "plastic skin, CGI hand, cartoon, illustration, blurry, soft focus, "
    "skin smoothing, airbrushed, beautification"
)


async def main():
    out_dir = "/home/ronald/projects/scribario-web/public/images"
    os.makedirs(out_dir, exist_ok=True)

    async with httpx.AsyncClient(timeout=300.0) as client:
        # Create task
        payload = {
            "model": "nano-banana-2",
            "input": {
                "prompt": PROMPT,
                "negative_prompt": NEGATIVE,
                "aspect_ratio": "3:4",
                "resolution": "4K",
                "output_format": "png",
            },
        }
        print("Creating task...")
        resp = await client.post(f"{BASE_URL}/api/v1/jobs/createTask", headers=HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 200:
            raise RuntimeError(f"createTask failed: {data}")
        task_id = data["data"]["taskId"]
        print(f"Task: {task_id}")

        # Poll
        for attempt in range(120):
            resp = await client.get(f"{BASE_URL}/api/v1/jobs/recordInfo", headers=HEADERS, params={"taskId": task_id})
            resp.raise_for_status()
            td = resp.json()["data"]
            state = td.get("state", "")
            if state == "success":
                rj = json.loads(td.get("resultJson", "{}"))
                urls = rj.get("resultUrls", [])
                if not urls:
                    raise RuntimeError("No URLs")
                print(f"Done! Downloading...")
                url = urls[0]
                break
            if state in ("failed", "error"):
                raise RuntimeError(f"Failed: {td.get('failMsg')}")
            if attempt % 10 == 0:
                print(f"Generating... {attempt * 2}s, state={state}")
            await asyncio.sleep(2)
        else:
            raise TimeoutError("Timed out")

        # Download
        for att in range(5):
            try:
                resp = await client.get(url, timeout=120.0)
                resp.raise_for_status()
                raw_path = f"{out_dir}/hand-phone-greenscreen-v2.png"
                with open(raw_path, "wb") as f:
                    f.write(resp.content)
                print(f"Downloaded: {raw_path} ({len(resp.content)/1024:.0f} KB)")
                break
            except Exception as e:
                print(f"Download retry {att+1}: {e}")
                await asyncio.sleep(5)

    # Chroma-key green → transparent
    print("Chroma-keying green to transparent...")
    img = Image.open(raw_path).convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:,:,0].astype(int), data[:,:,1].astype(int), data[:,:,2].astype(int), data[:,:,3]

    # Green detection — generous threshold
    green_mask = (g > 150) & (g - r > 40) & (g - b > 40)
    data[green_mask] = [0, 0, 0, 0]

    # Edge softening
    from scipy.ndimage import binary_dilation
    edge = binary_dilation(green_mask, iterations=2) & ~green_mask
    # Reduce green spill in edge pixels
    green_strength = np.clip((data[edge, 1].astype(float) - np.maximum(data[edge, 0], data[edge, 2]).astype(float)) / 80.0, 0, 1)
    data[edge, 3] = np.clip((1.0 - green_strength * 0.7) * 255, 0, 255).astype(np.uint8)
    data[edge, 1] = np.minimum(
        data[edge, 1],
        ((data[edge, 0].astype(int) + data[edge, 2].astype(int)) // 2).astype(np.uint8),
    )

    result = Image.fromarray(data)
    final_path = f"{out_dir}/hand-phone.png"
    result.save(final_path, optimize=True)

    # Check stats
    alpha = np.array(result)[:,:,3]
    total = alpha.size
    print(f"Transparent: {(alpha==0).sum()/total*100:.1f}%")
    print(f"Saved: {final_path}")

    # Also save green-screen version (other Claude might want it)
    shutil.copy(raw_path, f"{out_dir}/hand-phone-greenscreen.png")

    # Copy both to Downloads
    shutil.copy(final_path, "/mnt/c/Users/ronal/Downloads/hand-phone-straight.png")
    shutil.copy(raw_path, "/mnt/c/Users/ronal/Downloads/hand-phone-greenscreen.png")
    print("Copied to Downloads: hand-phone-straight.png + hand-phone-greenscreen.png")


if __name__ == "__main__":
    asyncio.run(main())
