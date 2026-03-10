"""Tests for pipeline.image_gen module."""

from __future__ import annotations

import pytest

from pipeline.image_gen import ImageGenerationService, ImageProvider, ImageResult


class FakeProvider(ImageProvider):
    """Fake provider for testing."""

    def __init__(self, name: str = "fake", should_fail: bool = False) -> None:
        self._name = name
        self._should_fail = should_fail
        self.call_count = 0

    @property
    def name(self) -> str:
        return self._name

    async def generate(self, prompt: str, aspect_ratio: str = "1:1") -> ImageResult:
        self.call_count += 1
        if self._should_fail:
            raise RuntimeError(f"{self._name} failed")
        return ImageResult(
            url=f"https://fake.com/{self._name}/{self.call_count}.png",
            provider=self._name,
            cost_usd=0.005,
            metadata={"prompt": prompt, "aspect_ratio": aspect_ratio},
        )


class TestImageGenerationService:
    @pytest.mark.asyncio
    async def test_uses_first_provider(self):
        primary = FakeProvider("primary")
        fallback = FakeProvider("fallback")
        service = ImageGenerationService(providers=[primary, fallback])

        result = await service.generate("test prompt")

        assert result.provider == "primary"
        assert primary.call_count == 1
        assert fallback.call_count == 0

    @pytest.mark.asyncio
    async def test_falls_back_on_failure(self):
        primary = FakeProvider("primary", should_fail=True)
        fallback = FakeProvider("fallback")
        service = ImageGenerationService(providers=[primary, fallback])

        result = await service.generate("test prompt")

        assert result.provider == "fallback"
        assert primary.call_count == 1
        assert fallback.call_count == 1

    @pytest.mark.asyncio
    async def test_all_providers_fail_raises(self):
        p1 = FakeProvider("p1", should_fail=True)
        p2 = FakeProvider("p2", should_fail=True)
        service = ImageGenerationService(providers=[p1, p2])

        with pytest.raises(RuntimeError, match="All image providers failed"):
            await service.generate("test prompt")

    @pytest.mark.asyncio
    async def test_no_providers_raises(self):
        service = ImageGenerationService(providers=[])

        with pytest.raises(RuntimeError, match="No image generation providers configured"):
            await service.generate("test prompt")

    @pytest.mark.asyncio
    async def test_generate_batch(self):
        provider = FakeProvider("batch")
        service = ImageGenerationService(providers=[provider])

        results = await service.generate_batch(["prompt1", "prompt2", "prompt3"])

        assert len(results) == 3
        assert provider.call_count == 3
        assert all(r.provider == "batch" for r in results)

    @pytest.mark.asyncio
    async def test_result_contains_url(self):
        provider = FakeProvider("test")
        service = ImageGenerationService(providers=[provider])

        result = await service.generate("a beautiful sunset")

        assert result.url.startswith("https://")
        assert result.cost_usd == 0.005

    @pytest.mark.asyncio
    async def test_aspect_ratio_passed_through(self):
        provider = FakeProvider("test")
        service = ImageGenerationService(providers=[provider])

        result = await service.generate("test", aspect_ratio="9:16")

        assert result.metadata["aspect_ratio"] == "9:16"
