"""Generate hand-phone on green screen, then chroma-key to real transparency."""

import asyncio
import json
import os

import httpx

API_KEY = os.environ["KIE_AI_API_KEY"]
BASE_URL = "https://api.kie.ai"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


async def create_task(client: httpx.AsyncClient, prompt: str, aspect_ratio: str) -> str:
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": "2K",
            "output_format": "png",
        },
    }
    resp = await client.post(f"{BASE_URL}/api/v1/jobs/createTask", headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"createTask failed: {data}")
    task_id = data["data"]["taskId"]
    print(f"Task created: {task_id}")
    return task_id


async def poll_task(client: httpx.AsyncClient, task_id: str) -> str:
    for attempt in range(90):
        resp = await client.get(f"{BASE_URL}/api/v1/jobs/recordInfo", headers=HEADERS, params={"taskId": task_id})
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 200:
            raise RuntimeError(f"poll failed: {data}")
        task_data = data["data"]
        state = task_data.get("state", "")
        if state == "success":
            result_json = json.loads(task_data.get("resultJson", "{}"))
            urls = result_json.get("resultUrls", [])
            if not urls:
                raise RuntimeError("No URLs in result")
            print(f"Done! URL: {urls[0][:80]}...")
            return urls[0]
        if state in ("failed", "error"):
            raise RuntimeError(f"Failed: {task_data.get('failMsg', 'unknown')}")
        if attempt % 10 == 0:
            print(f"Polling... attempt {attempt + 1}, state={state}")
        await asyncio.sleep(2)
    raise TimeoutError("Timed out")


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
        "(#00FF00) — a perfectly uniform green screen with no variation, no gradient, no shadow "
        "on the green. Pure flat #00FF00 everywhere except the hand and phone. "
        "Professional product photography, 85mm lens, f/4.0, ISO 100, softbox lighting. "
        "Do not add any content to the phone screen. Do not beautify the hand. No AI smoothing."
    )

    output_dir = "/home/ronald/projects/scribario-web/public/images"

    async with httpx.AsyncClient(timeout=180.0) as client:
        task_id = await create_task(client, prompt, "3:4")
        url = await poll_task(client, task_id)

        # Download raw green-screen version
        resp = await client.get(url)
        resp.raise_for_status()
        raw_path = f"{output_dir}/hand-phone-greenscreen.png"
        with open(raw_path, "wb") as f:
            f.write(resp.content)
        print(f"Saved green-screen: {raw_path} ({len(resp.content) / 1024:.0f} KB)")

    # Now chroma-key the green out
    print("\nRemoving green screen...")
    import numpy as np
    from PIL import Image

    img = Image.open(raw_path).convert("RGBA")
    data = np.array(img)

    # Green screen detection: high G, low R, low B
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    green_mask = (g > 180) & (r < 150) & (b < 150)

    # Set green pixels to fully transparent
    data[green_mask] = [0, 0, 0, 0]

    # Anti-alias: pixels near the edge that have green spill — reduce alpha proportionally
    # Soften the boundary by checking partial green
    partial_green = (g > 100) & (r < 180) & (b < 180) & ~green_mask
    green_ratio = g[partial_green].astype(float) / (r[partial_green].astype(float) + g[partial_green].astype(float) + b[partial_green].astype(float) + 1)
    # If green dominates (ratio > 0.5), reduce alpha
    new_alpha = np.clip((1.0 - (green_ratio - 0.33) * 3.0) * 255, 0, 255).astype(np.uint8)
    data[partial_green, 3] = np.minimum(data[partial_green, 3], new_alpha)

    result = Image.fromarray(data)
    final_path = f"{output_dir}/hand-phone.png"
    result.save(final_path)
    print(f"Saved final: {final_path}")

    # Also copy to Downloads
    import shutil
    shutil.copy(final_path, "/mnt/c/Users/ronal/Downloads/hand-phone.png")
    print("Copied to Downloads")


if __name__ == "__main__":
    asyncio.run(main())
