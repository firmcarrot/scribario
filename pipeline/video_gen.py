"""Video generation — provider-abstracted wrapper.

Primary: Kie.ai (Veo 3.1 Fast)
"""

from __future__ import annotations

import abc
import asyncio
import logging
from dataclasses import dataclass

import httpx

from bot.config import get_settings

logger = logging.getLogger(__name__)

# Polling config — videos take longer than images
MAX_POLL_ATTEMPTS = 120  # 120 * 10s = 20 min max wait
POLL_INTERVAL_SECONDS = 10


@dataclass
class VideoResult:
    """Result from video generation."""

    url: str
    provider: str
    cost_usd: float
    metadata: dict


class VideoProvider(abc.ABC):
    """Abstract base for video generation providers."""

    @abc.abstractmethod
    async def generate(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        generation_type: str = "TEXT_2_VIDEO",
        image_urls: list[str] | None = None,
    ) -> VideoResult:
        """Generate a video from a text prompt."""
        ...

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Provider name for logging and cost tracking."""
        ...


class KieAiVeoProvider(VideoProvider):
    """Kie.ai Veo 3.1 video generation.

    Async flow: POST /veo/generate → poll /veo/record-info until successFlag=1.
    """

    BASE_URL = "https://api.kie.ai"
    DEFAULT_MODEL = "veo3_fast"
    MODEL_COSTS = {"veo3_fast": 0.40, "veo3": 2.00}

    def __init__(self, api_key: str, model: str | None = None) -> None:
        self._api_key = api_key
        self._model = model or self.DEFAULT_MODEL
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
        return "kie_ai_veo"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def _create_task(
        self,
        prompt: str,
        aspect_ratio: str,
        generation_type: str,
        image_urls: list[str] | None = None,
    ) -> str:
        """Submit video generation task. Returns taskId."""
        payload: dict = {
            "prompt": prompt,
            "model": self._model,
            "generationType": generation_type,
            "imageUrls": image_urls or [],
            "aspect_ratio": aspect_ratio,
            "callBackUrl": "",
        }

        response = await self._get_client().post(
            f"{self.BASE_URL}/api/v1/veo/generate",
            headers=self._headers(),
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 200:
            raise RuntimeError(
                f"Kie.ai Veo createTask failed: {data.get('msg', 'unknown error')}"
            )

        task_id = data.get("data", {}).get("taskId") or data.get("taskId")
        if not task_id:
            raise RuntimeError(f"Kie.ai Veo returned no taskId: {data}")
        logger.info("Kie.ai Veo task created", extra={"task_id": task_id})
        return task_id

    async def _poll_task(self, task_id: str) -> dict:
        """Poll task status until complete. Returns result data."""
        for attempt in range(MAX_POLL_ATTEMPTS):
            response = await self._get_client().get(
                f"{self.BASE_URL}/api/v1/veo/record-info",
                headers=self._headers(),
                params={"taskId": task_id},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 200:
                raise RuntimeError(f"Kie.ai Veo poll failed: {data.get('msg')}")

            task_data = data["data"]
            success_flag = task_data.get("successFlag", 0)

            if success_flag == 1:
                logger.info("Kie.ai Veo task complete", extra={"task_id": task_id})
                return task_data

            if success_flag in (2, 3):
                raise RuntimeError("Kie.ai Veo generation failed")

            # Still generating (successFlag=0) — wait and retry
            if attempt < MAX_POLL_ATTEMPTS - 1:
                await asyncio.sleep(POLL_INTERVAL_SECONDS)

        raise TimeoutError(
            f"Kie.ai Veo task {task_id} timed out after "
            f"{MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS}s"
        )

    async def generate(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        generation_type: str = "TEXT_2_VIDEO",
        image_urls: list[str] | None = None,
    ) -> VideoResult:
        """Generate video via Kie.ai Veo 3.1 Fast API.

        1. Create async task
        2. Poll until complete
        3. Extract video URL from works[0].resource.resource
        """
        task_id = await self._create_task(prompt, aspect_ratio, generation_type, image_urls)
        task_data = await self._poll_task(task_id)

        # Extract video URL — check response.resultUrls first, then works array
        video_url = ""
        response_data = task_data.get("response", {})
        result_urls = response_data.get("resultUrls", [])

        if result_urls:
            video_url = result_urls[0]
        else:
            # Fallback: check works array structure
            works = task_data.get("works", [])
            if works:
                resource_obj = works[0].get("resource", {})
                video_url = resource_obj.get("resource", "")

        if not video_url:
            raise RuntimeError(f"Kie.ai Veo returned no video URL for task {task_id}")

        return VideoResult(
            url=video_url,
            provider=self.name,
            cost_usd=self.MODEL_COSTS.get(self._model, 0.40),
            metadata={"task_id": task_id, "model": self._model, "response": response_data},
        )


class VideoGenerationService:
    """Provider-abstracted video generation with automatic fallback.

    When tenant_id is provided, every successful generation is automatically
    logged to the usage_events table. This ensures cost tracking is complete
    regardless of which script or pipeline triggers the generation.
    """

    def __init__(
        self,
        providers: list[VideoProvider] | None = None,
        tenant_id: str | None = None,
    ) -> None:
        if providers is None:
            providers = []
            if get_settings().kie_ai_api_key:
                providers.append(KieAiVeoProvider(get_settings().kie_ai_api_key))

        self._providers = providers
        self._tenant_id = tenant_id

    async def _log_usage(self, result: VideoResult, prompt: str) -> None:
        """Log usage event to Supabase if tenant_id is set."""
        if self._tenant_id is None:
            return
        try:
            from bot.db import log_usage_event

            await log_usage_event(
                tenant_id=self._tenant_id,
                event_type="video_generation",
                provider=result.provider,
                cost_usd=result.cost_usd,
                metadata={
                    "prompt": prompt[:100],
                    "task_id": result.metadata.get("task_id", ""),
                    "model": result.metadata.get("model", ""),
                },
            )
        except Exception:
            logger.error("Failed to log video usage event", exc_info=True)

    async def generate(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        generation_type: str = "TEXT_2_VIDEO",
        image_urls: list[str] | None = None,
    ) -> VideoResult:
        """Generate video, trying providers in order until one succeeds."""
        if not self._providers:
            raise RuntimeError("No video generation providers configured")

        last_error: Exception | None = None
        for provider in self._providers:
            try:
                result = await provider.generate(
                    prompt, aspect_ratio, generation_type, image_urls
                )
                logger.info(
                    "Video generated",
                    extra={"provider": provider.name, "cost": result.cost_usd},
                )
                await self._log_usage(result, prompt)
                return result
            except Exception as e:
                logger.warning(
                    "Video provider failed, trying next",
                    extra={"provider": provider.name, "error": str(e)},
                )
                last_error = e

        raise RuntimeError(f"All video providers failed. Last error: {last_error}")
