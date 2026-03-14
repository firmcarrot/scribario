"""ElevenLabs sound effects generation."""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
import uuid
from dataclasses import dataclass

import httpx

from bot.config import get_settings

logger = logging.getLogger(__name__)

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io"
SFX_COST_PER_CLIP = 0.01


@dataclass
class SFXResult:
    audio_path: str
    cost_usd: float


async def generate_sfx(
    description: str,
    duration_seconds: float = 3.0,
    output_dir: str | None = None,
) -> SFXResult:
    """Generate a sound effect from a text description.

    POST /v1/sound-generation with:
    - text: description
    - duration_seconds: target duration
    """
    settings = get_settings()
    api_key = settings.elevenlabs_api_key

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="scribario_sfx_")

    os.makedirs(output_dir, exist_ok=True)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ELEVENLABS_BASE_URL}/v1/sound-generation",
            json={
                "text": description,
                "duration_seconds": duration_seconds,
            },
            headers={"xi-api-key": api_key},
            timeout=60.0,
        )
        response.raise_for_status()

    audio_path = os.path.join(output_dir, f"sfx_{uuid.uuid4().hex[:8]}.mp3")
    with open(audio_path, "wb") as f:
        f.write(response.content)

    logger.info("Generated SFX: %s -> %s", description, audio_path)
    return SFXResult(audio_path=audio_path, cost_usd=SFX_COST_PER_CLIP)


async def generate_sfx_batch(
    descriptions: list[dict],
    output_dir: str | None = None,
) -> list[SFXResult | None]:
    """Generate multiple SFX in parallel. Returns None for failed items."""
    tasks = [
        generate_sfx(
            description=item["description"],
            duration_seconds=item.get("duration_seconds", 3.0),
            output_dir=output_dir,
        )
        for item in descriptions
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [
        r if isinstance(r, SFXResult) else None
        for r in results
    ]
