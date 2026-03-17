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


MAX_IMAGE_INPUTS = 14  # Nano Banana 2 supports up to 14 reference images


class ImageProvider(abc.ABC):
    """Abstract base for image generation providers."""

    @abc.abstractmethod
    async def generate(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        reference_image_urls: list[str] | None = None,
    ) -> ImageResult:
        """Generate an image from a text prompt, optionally with reference images."""
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

    async def _create_task(
        self,
        prompt: str,
        aspect_ratio: str,
        reference_image_urls: list[str] | None = None,
    ) -> str:
        """Submit image generation task. Returns taskId."""
        input_data: dict = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": "1K",
            "output_format": "jpg",
        }
        # Add reference images if provided (Nano Banana 2 supports up to 14)
        if reference_image_urls:
            input_data["image_input"] = reference_image_urls

        payload = {
            "model": "nano-banana-2",
            "input": input_data,
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

    async def generate(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        reference_image_urls: list[str] | None = None,
    ) -> ImageResult:
        """Generate image via Kie.ai Nano Banana 2 API.

        1. Create async task (with optional reference images)
        2. Poll until complete
        3. Extract image URL from resultJson

        Args:
            prompt: Text description of what to generate.
            aspect_ratio: Output aspect ratio.
            reference_image_urls: Optional list of signed HTTPS URLs for reference photos.
                Nano Banana 2 uses these for subject/style consistency. Max 14.
        """
        task_id = await self._create_task(prompt, aspect_ratio, reference_image_urls)
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
    """Provider-abstracted image generation with automatic fallback.

    When tenant_id is provided, every successful generation is automatically
    logged to the usage_events table. This ensures cost tracking is complete
    regardless of which script or pipeline triggers the generation.
    """

    def __init__(
        self,
        providers: list[ImageProvider] | None = None,
        tenant_id: str | None = None,
    ) -> None:
        if providers is None:
            # Default: Kie.ai only for MVP
            providers = []
            if get_settings().kie_ai_api_key:
                providers.append(KieAiProvider(get_settings().kie_ai_api_key))

        self._providers = providers
        self._tenant_id = tenant_id

    async def _log_usage(self, result: ImageResult, prompt: str) -> None:
        """Log usage event to Supabase if tenant_id is set."""
        if self._tenant_id is None:
            return
        try:
            from bot.db import log_usage_event

            await log_usage_event(
                tenant_id=self._tenant_id,
                event_type="image_generation",
                provider=result.provider,
                cost_usd=result.cost_usd,
                metadata={
                    "prompt": prompt[:100],
                    "task_id": result.metadata.get("task_id", ""),
                },
            )
        except Exception:
            logger.error("Failed to log image usage event", exc_info=True)

    async def generate(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        reference_image_urls: list[str] | None = None,
    ) -> ImageResult:
        """Generate image, trying providers in order until one succeeds."""
        if not self._providers:
            raise RuntimeError("No image generation providers configured")

        last_error: Exception | None = None
        for provider in self._providers:
            try:
                result = await provider.generate(prompt, aspect_ratio, reference_image_urls)
                logger.info(
                    "Image generated",
                    extra={"provider": provider.name, "cost": result.cost_usd},
                )
                await self._log_usage(result, prompt)
                return result
            except Exception as e:
                logger.warning(
                    "Image provider failed, trying next",
                    extra={"provider": provider.name, "error": str(e)},
                )
                last_error = e

        raise RuntimeError(f"All image providers failed. Last error: {last_error}")

    async def generate_batch(
        self,
        prompts: list[str],
        aspect_ratio: str = "1:1",
        reference_image_urls: list[str] | None = None,
    ) -> list[ImageResult]:
        """Generate multiple images. Sequential to respect rate limits.

        Args:
            prompts: One prompt per image to generate.
            aspect_ratio: Output aspect ratio.
            reference_image_urls: Reference photos passed to every generation in the batch.
        """
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, aspect_ratio, reference_image_urls)
            results.append(result)
        return results


def build_image_input_array(
    new_photo_urls: list[str],
    default_ref_urls: list[str],
    return_truncated: bool = False,
) -> list[str] | tuple[list[str], bool]:
    """Build the image_input array for Kie.ai, respecting the 14-image limit.

    Priority: new photos (user just sent) > saved defaults (oldest dropped first).
    New photos always get slots first so the user's explicit intent is always honored.

    Args:
        new_photo_urls: Photos attached in the current message (signed URLs).
        default_ref_urls: Saved default reference photos (signed URLs), newest first.
        return_truncated: If True, return (urls, was_truncated) tuple.

    Returns:
        List of image URLs to pass to image_input, capped at MAX_IMAGE_INPUTS.
        If return_truncated=True, returns (list, bool) where bool indicates defaults were dropped.
    """
    # New photos take all available slots first
    selected_new = new_photo_urls[:MAX_IMAGE_INPUTS]
    remaining_slots = MAX_IMAGE_INPUTS - len(selected_new)

    selected_defaults = default_ref_urls[:remaining_slots]
    truncated = len(default_ref_urls) > remaining_slots

    result = selected_new + selected_defaults

    if return_truncated:
        return result, truncated
    return result
