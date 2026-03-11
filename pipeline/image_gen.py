"""Image generation — provider-abstracted wrapper.

Primary: Kie.ai (Nano Banana 2)
Fallback: Google Gemini (Imagen 3) — Phase 2
Emergency: Replicate (Flux.1) — Phase 2
"""

from __future__ import annotations

import abc
import asyncio
import json
import logging
from dataclasses import dataclass

import httpx

from bot.config import get_settings

logger = logging.getLogger(__name__)

# Polling config for async task completion
MAX_POLL_ATTEMPTS = 60  # 60 * 2s = 120s max wait
POLL_INTERVAL_SECONDS = 2


@dataclass
class ImageResult:
    """Result from image generation."""

    url: str
    provider: str
    cost_usd: float
    metadata: dict


class ImageProvider(abc.ABC):
    """Abstract base for image generation providers."""

    @abc.abstractmethod
    async def generate(self, prompt: str, aspect_ratio: str = "1:1") -> ImageResult:
        """Generate an image from a text prompt."""
        ...

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Provider name for logging and cost tracking."""
        ...


class KieAiProvider(ImageProvider):
    """Kie.ai / Nano Banana 2 image generation.

    Async flow: createTask → poll recordInfo until state=success → extract image URL.
    """

    BASE_URL = "https://api.kie.ai"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @property
    def name(self) -> str:
        return "kie_ai"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def _create_task(self, prompt: str, aspect_ratio: str) -> str:
        """Submit image generation task. Returns taskId."""
        payload = {
            "model": "nano-banana-2",
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": "1K",
                "output_format": "png",
            },
        }

        response = await self._get_client().post(
            f"{self.BASE_URL}/api/v1/jobs/createTask",
            headers=self._headers(),
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 200:
            raise RuntimeError(f"Kie.ai createTask failed: {data.get('msg', 'unknown error')}")

        task_id = data["data"]["taskId"]
        logger.info("Kie.ai task created", extra={"task_id": task_id})
        return task_id

    async def _poll_task(self, task_id: str) -> dict:
        """Poll task status until complete. Returns result data."""
        for attempt in range(MAX_POLL_ATTEMPTS):
            response = await self._get_client().get(
                f"{self.BASE_URL}/api/v1/jobs/recordInfo",
                headers=self._headers(),
                params={"taskId": task_id},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 200:
                raise RuntimeError(f"Kie.ai poll failed: {data.get('msg')}")

            task_data = data["data"]
            state = task_data.get("state", "")

            if state == "success":
                logger.info(
                    "Kie.ai task complete",
                    extra={"task_id": task_id, "cost_time": task_data.get("costTime")},
                )
                return task_data

            if state in ("failed", "error"):
                raise RuntimeError(
                    f"Kie.ai generation failed: {task_data.get('failMsg', 'unknown')}"
                )

            # Still processing — wait and retry
            if attempt < MAX_POLL_ATTEMPTS - 1:
                await asyncio.sleep(POLL_INTERVAL_SECONDS)

        raise TimeoutError(f"Kie.ai task {task_id} timed out after {MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS}s")

    async def generate(self, prompt: str, aspect_ratio: str = "1:1") -> ImageResult:
        """Generate image via Kie.ai Nano Banana 2 API.

        1. Create async task
        2. Poll until complete
        3. Extract image URL from resultJson
        """
        task_id = await self._create_task(prompt, aspect_ratio)
        task_data = await self._poll_task(task_id)

        # Extract image URL from resultJson (it's a JSON string inside the response)
        result_json_str = task_data.get("resultJson", "{}")
        result_json = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
        result_urls = result_json.get("resultUrls", [])

        if not result_urls:
            raise RuntimeError(f"Kie.ai returned no image URLs for task {task_id}")

        image_url = result_urls[0]

        return ImageResult(
            url=image_url,
            provider=self.name,
            cost_usd=0.04,  # $0.04 for 1K resolution per docs
            metadata={"task_id": task_id, "result_json": result_json},
        )


class ImageGenerationService:
    """Provider-abstracted image generation with automatic fallback."""

    def __init__(self, providers: list[ImageProvider] | None = None) -> None:
        if providers is None:
            # Default: Kie.ai only for MVP
            providers = []
            if get_settings().kie_ai_api_key:
                providers.append(KieAiProvider(get_settings().kie_ai_api_key))

        self._providers = providers

    async def generate(self, prompt: str, aspect_ratio: str = "1:1") -> ImageResult:
        """Generate image, trying providers in order until one succeeds."""
        if not self._providers:
            raise RuntimeError("No image generation providers configured")

        last_error: Exception | None = None
        for provider in self._providers:
            try:
                result = await provider.generate(prompt, aspect_ratio)
                logger.info(
                    "Image generated",
                    extra={"provider": provider.name, "cost": result.cost_usd},
                )
                return result
            except Exception as e:
                logger.warning(
                    "Image provider failed, trying next",
                    extra={"provider": provider.name, "error": str(e)},
                )
                last_error = e

        raise RuntimeError(f"All image providers failed. Last error: {last_error}")

    async def generate_batch(
        self, prompts: list[str], aspect_ratio: str = "1:1"
    ) -> list[ImageResult]:
        """Generate multiple images. Sequential to respect rate limits."""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, aspect_ratio)
            results.append(result)
        return results
