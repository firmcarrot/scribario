"""Generate website assets via Kie.ai Nano Banana 2 API."""

import asyncio
import json
import os
import sys

import httpx

API_KEY = os.environ["KIE_AI_API_KEY"]
BASE_URL = "https://api.kie.ai"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


async def create_task(client: httpx.AsyncClient, prompt: str, aspect_ratio: str, resolution: str = "2K", output_format: str = "png") -> str:
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "output_format": output_format,
        },
    }
    resp = await client.post(f"{BASE_URL}/api/v1/jobs/createTask", headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"createTask failed: {data}")
    task_id = data["data"]["taskId"]
    print(f"  Task created: {task_id}")
    return task_id


async def poll_task(client: httpx.AsyncClient, task_id: str, label: str) -> str:
    for attempt in range(90):  # 180s max
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
                raise RuntimeError(f"No URLs in result for {label}")
            print(f"  [{label}] Done! URL: {urls[0][:80]}...")
            return urls[0]
        if state in ("failed", "error"):
            raise RuntimeError(f"[{label}] Failed: {task_data.get('failMsg', 'unknown')}")
        if attempt % 10 == 0:
            print(f"  [{label}] Polling... attempt {attempt + 1}, state={state}")
        await asyncio.sleep(2)
    raise TimeoutError(f"[{label}] Timed out")


async def download(client: httpx.AsyncClient, url: str, path: str):
    resp = await client.get(url)
    resp.raise_for_status()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(resp.content)
    size_kb = len(resp.content) / 1024
    print(f"  Saved: {path} ({size_kb:.0f} KB)")


async def main():
    hand_phone_prompt = (
        "Photorealistic product-style photograph of a large right human hand casually holding "
        "an iPhone 15 Pro in natural titanium color from below, phone screen facing directly toward "
        "camera at a slight upward angle — similar to showing someone your screen. "
        "The phone screen is pure solid white (#FFFFFF), completely blank with no content whatsoever. "
        "The phone has thin black bezels and a Dynamic Island notch visible at the top. "
        "The hand is large and prominent in frame, natural skin texture with visible pores, "
        "knuckle creases, subtle nail ridges, and natural skin tone variation. "
        "CRITICAL: The background must be completely transparent — no background at all, "
        "just the hand and phone floating with alpha transparency. PNG with transparent background. "
        "Professional product photography, 85mm lens, f/4.0, ISO 100, softbox lighting from "
        "above-left creating subtle natural shadows on the hand. The phone has subtle reflections "
        "on its titanium frame edges. "
        "Do not add any content to the phone screen — it must be pure white. "
        "Do not beautify the hand. No AI smoothing. No background elements."
    )

    icons_prompt = (
        "A clean 3x2 grid of 6 minimal premium line-art icons on a transparent background. "
        "Each icon is drawn in coral-orange (#FF6B4A) with thin elegant strokes. "
        "Top row left to right: (1) Restaurant — elegant fork and knife crossed, "
        "(2) Agency — rising bar chart with upward arrow, "
        "(3) Local Shop — simple storefront with awning. "
        "Bottom row left to right: (4) Salon — elegant scissors, "
        "(5) Gym — minimalist dumbbell, (6) Real Estate — simple house outline with chimney. "
        "Each icon is centered in its grid cell with generous padding. "
        "The style is premium, minimal, consistent stroke width throughout. "
        "Similar to Stripe or Linear app icon design language. "
        "Clean vector-style outlines, no gradients, no solid fills, just thin line outlines. "
        "PNG with transparent background."
    )

    output_dir = "/home/ronald/projects/scribario-web/public/images"

    async with httpx.AsyncClient(timeout=180.0) as client:
        # Launch both tasks in parallel
        print("Creating tasks...")
        task1_id, task2_id = await asyncio.gather(
            create_task(client, hand_phone_prompt, "3:4", "2K", "png"),
            create_task(client, icons_prompt, "3:2", "2K", "png"),
        )

        # Poll both in parallel
        print("\nPolling for results...")
        url1, url2 = await asyncio.gather(
            poll_task(client, task1_id, "hand-phone"),
            poll_task(client, task2_id, "icons-grid"),
        )

        # Download both
        print("\nDownloading...")
        await asyncio.gather(
            download(client, url1, f"{output_dir}/hand-phone.png"),
            download(client, url2, f"{output_dir}/icons/icons-grid.png"),
        )

    print("\nDone! Both images saved.")


if __name__ == "__main__":
    asyncio.run(main())
