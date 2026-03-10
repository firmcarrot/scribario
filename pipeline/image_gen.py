"""Image generation — provider-abstracted wrapper.

Primary: Kie.ai (Nano Banana 2)
Fallback: Google Gemini (Imagen 3) — Phase 2
Emergency: Replicate (Flux.1) — Phase 2
"""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass

import httpx

from bot.config import get_settings

logger = logging.getLogger(__name__)


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
    """Kie.ai / Nano Banana 2 image generation."""

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

    async def generate(self, prompt: str, aspect_ratio: str = "1:1") -> ImageResult:
        """Generate image via Kie.ai API.

        TODO: Verify exact API endpoint and request format from Kie.ai docs.
        This is a placeholder based on documented Nano Banana 2 capabilities.
        """
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "prompt": prompt,
            "model": "nano-banana-2",
            "aspect_ratio": aspect_ratio,
        }

        response = await self._get_client().post(
            f"{self.BASE_URL}/v1/images/generate",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        return ImageResult(
            url=data.get("url", ""),
            provider=self.name,
            cost_usd=0.005,  # ~$0.005/credit per docs
            metadata=data,
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
