"""ElevenLabs TTS — voiceover generation per scene."""

from __future__ import annotations

import logging
import os
import tempfile
import uuid
from dataclasses import dataclass

import httpx

from bot.config import get_settings

logger = logging.getLogger(__name__)

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io"
TTS_COST_PER_SCENE = 0.01  # ~$0.01 per scene

# 128kbps MP3: bytes_per_second = 128000 / 8 = 16000
_MP3_128KBPS_BYTES_PER_SECOND = 16000


@dataclass
class TTSResult:
    """Result from TTS generation."""

    audio_url: str  # Local temp file path or remote URL
    duration_seconds: float
    cost_usd: float


async def generate_voiceover(
    text: str,
    voice_id: str,
    output_dir: str | None = None,
) -> TTSResult:
    """Generate voiceover audio for a single scene.

    Calls ElevenLabs /v1/text-to-speech/{voice_id} with the text.
    Saves audio to a temp file. Estimates duration from audio size.

    Args:
        text: Voiceover text for the scene.
        voice_id: ElevenLabs voice ID.
        output_dir: Directory for temp audio files. Defaults to system temp dir.

    Returns:
        TTSResult with local file path, duration, and cost.

    Raises:
        httpx.HTTPStatusError: If the ElevenLabs API returns a non-2xx response.
        httpx.ConnectError: If the API is unreachable.
    """
    settings = get_settings()
    url = f"{ELEVENLABS_BASE_URL}/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
            headers=headers,
            params={"output_format": "mp3_44100_128"},
            timeout=60.0,
        )
        response.raise_for_status()

    # Save audio to file
    audio_bytes = response.content
    file_name = f"tts_{uuid.uuid4().hex[:12]}.mp3"

    if output_dir is not None:
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
    else:
        fd, file_path = tempfile.mkstemp(suffix=".mp3")
        with os.fdopen(fd, "wb") as f:
            f.write(audio_bytes)

    # Estimate duration from file size (128kbps MP3)
    file_size = len(audio_bytes)
    duration_seconds = file_size / _MP3_128KBPS_BYTES_PER_SECOND

    logger.info(
        "Generated voiceover: %s (%.1fs, %d bytes)",
        file_path,
        duration_seconds,
        file_size,
    )

    return TTSResult(
        audio_url=file_path,
        duration_seconds=duration_seconds,
        cost_usd=TTS_COST_PER_SCENE,
    )


async def generate_voiceovers_sequential(
    scenes: list[dict],  # [{text: str, voice_id: str}]
    output_dir: str | None = None,
) -> list[TTSResult]:
    """Generate voiceovers for all scenes sequentially.

    Sequential because timing of each scene determines the next.
    """
    results = []
    for scene in scenes:
        result = await generate_voiceover(
            text=scene["text"],
            voice_id=scene["voice_id"],
            output_dir=output_dir,
        )
        results.append(result)
    return results
