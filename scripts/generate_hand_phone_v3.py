"""Generate hand-phone on green screen — fast download, then chroma-key."""

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
OUTPUT_DIR = "/home/ronald/projects/scribario-web/public/images"


async def main():
    prompt = (
        "Photorealistic product-style photograph of a large right human hand casually holding "
        "an iPhone 15 Pro in natural titanium color from below, phone screen facing directly toward "
        "camera at a slight upward angle — like showing someone your screen. "
        "The phone screen is pure solid white (#FFFFFF), completely blank with no content. "
        "The phone has thin black bezels and a Dynamic Island notch visible at the top. "
        "The hand is large and prominent in frame, natural skin texture with visible pores, "
        "knuckle creases, subtle nail ridges, and natural skin tone variation. "
        "CRITICAL: The entire background behind the hand and phone must be solid bright green "
        "(#00FF00) — a perfectly uniform chroma key green screen. Pure flat #00FF00 everywhere "
        "except the hand and phone. No gradient, no shadow on the green areas. "
        "Professional product photography, 85mm lens, f/4.0, ISO 100, softbox lighting. "
        "Do not add any content to the phone screen. Do not beautify the hand."
    )

    async with httpx.AsyncClient(timeout=300.0) as client:
        # Create task
        payload = {
            "model": "nano-banana-2",
            "input": {
                "prompt": prompt,
                "aspect_ratio": "3:4",
                "resolution": "2K",
                "output_format": "jpg",  # jpg downloads faster than png from their CDN
            },
        }
        resp = await client.post(f"{BASE_URL}/api/v1/jobs/createTask", headers=HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 200:
            raise RuntimeError(f"createTask failed: {data}")
        task_id = data["data"]["taskId"]
        print(f"Task: {task_id}")

        # Poll
        for attempt in range(90):
            resp = await client.get(
                f"{BASE_URL}/api/v1/jobs/recordInfo",
                headers=HEADERS,
                params={"taskId": task_id},
            )
            resp.raise_for_status()
            data = resp.json()["data"]
            state = data.get("state", "")
            if state == "success":
                result_json = json.loads(data.get("resultJson", "{}"))
                urls = result_json.get("resultUrls", [])
                if not urls:
                    raise RuntimeError("No URLs")
                url = urls[0]
                print(f"Ready: {url[:80]}...")
                break
            if state in ("failed", "error"):
                raise RuntimeError(f"Failed: {data.get('failMsg')}")
            if attempt % 10 == 0:
                print(f"Waiting... {attempt * 2}s, state={state}")
            await asyncio.sleep(2)
        else:
            raise TimeoutError("Timed out after 180s")

        # Download immediately — don't let the temp URL expire
        print("Downloading (attempt 1)...")
        for dl_attempt in range(5):
            try:
                resp = await client.get(url, timeout=120.0)
                resp.raise_for_status()
                raw_path = f"{OUTPUT_DIR}/hand-phone-raw.jpg"
                with open(raw_path, "wb") as f:
                    f.write(resp.content)
                print(f"Downloaded: {len(resp.content) / 1024:.0f} KB")
                break
            except Exception as e:
                print(f"Download attempt {dl_attempt + 1} failed: {e}")
                if dl_attempt < 4:
                    await asyncio.sleep(3)
        else:
            raise RuntimeError("All download attempts failed")

    # Chroma-key green → transparent
    print("Chroma-keying...")
    import numpy as np
    from PIL import Image

    img = Image.open(raw_path).convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

    # Pure green detection
    green_mask = (g.astype(int) - r.astype(int) > 50) & (g.astype(int) - b.astype(int) > 50) & (g > 150)
    data[green_mask] = [0, 0, 0, 0]

    # Edge softening — partial green spill near subject edges
    from scipy.ndimage import binary_dilation
    edge_zone = binary_dilation(green_mask, iterations=3) & ~green_mask
    green_strength = np.clip((g.astype(float) - np.maximum(r, b).astype(float)) / 100.0, 0, 1)
    data[edge_zone, 3] = np.clip(
        (1.0 - green_strength[edge_zone] * 0.8) * 255, 0, 255
    ).astype(np.uint8)
    # Despill — reduce green channel in edge pixels
    data[edge_zone, 1] = np.minimum(
        data[edge_zone, 1],
        ((data[edge_zone, 0].astype(int) + data[edge_zone, 2].astype(int)) // 2).astype(np.uint8),
    )

    result = Image.fromarray(data)
    final_path = f"{OUTPUT_DIR}/hand-phone.png"
    result.save(final_path, optimize=True)
    print(f"Saved: {final_path}")

    shutil.copy(final_path, "/mnt/c/Users/ronal/Downloads/hand-phone.png")
    print("Copied to Downloads")


if __name__ == "__main__":
    asyncio.run(main())
