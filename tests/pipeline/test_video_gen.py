"""Tests for pipeline.video_gen module."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from pipeline.video_gen import (
    KieAiVeoProvider,
    VideoGenerationService,
    VideoProvider,
    VideoResult,
)


class FakeVideoProvider(VideoProvider):
    """Fake provider for testing."""

    def __init__(self, name: str = "fake", should_fail: bool = False) -> None:
        self._name = name
        self._should_fail = should_fail
        self.call_count = 0

    @property
    def name(self) -> str:
        return self._name

    async def generate(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        generation_type: str = "TEXT_2_VIDEO",
        image_urls: list[str] | None = None,
    ) -> VideoResult:
        self.call_count += 1
        if self._should_fail:
            raise RuntimeError(f"{self._name} failed")
        return VideoResult(
            url=f"https://fake.com/{self._name}/{self.call_count}.mp4",
            provider=self._name,
            cost_usd=0.40,
            metadata={"prompt": prompt, "aspect_ratio": aspect_ratio},
        )


class TestVideoResult:
    def test_dataclass_fields(self):
        result = VideoResult(
            url="https://example.com/video.mp4",
            provider="kie_ai_veo",
            cost_usd=0.40,
            metadata={"task_id": "abc"},
        )
        assert result.url == "https://example.com/video.mp4"
        assert result.provider == "kie_ai_veo"
        assert result.cost_usd == 0.40
        assert result.metadata == {"task_id": "abc"}


class TestVideoGenerationService:
    @pytest.mark.asyncio
    async def test_uses_first_provider(self):
        primary = FakeVideoProvider("primary")
        fallback = FakeVideoProvider("fallback")
        service = VideoGenerationService(providers=[primary, fallback])

        result = await service.generate("test prompt")

        assert result.provider == "primary"
        assert primary.call_count == 1
        assert fallback.call_count == 0

    @pytest.mark.asyncio
    async def test_falls_back_on_failure(self):
        primary = FakeVideoProvider("primary", should_fail=True)
        fallback = FakeVideoProvider("fallback")
        service = VideoGenerationService(providers=[primary, fallback])

        result = await service.generate("test prompt")

        assert result.provider == "fallback"
        assert primary.call_count == 1
        assert fallback.call_count == 1

    @pytest.mark.asyncio
    async def test_all_providers_fail_raises(self):
        p1 = FakeVideoProvider("p1", should_fail=True)
        p2 = FakeVideoProvider("p2", should_fail=True)
        service = VideoGenerationService(providers=[p1, p2])

        with pytest.raises(RuntimeError, match="All video providers failed"):
            await service.generate("test prompt")

    @pytest.mark.asyncio
    async def test_no_providers_raises(self):
        service = VideoGenerationService(providers=[])

        with pytest.raises(RuntimeError, match="No video generation providers configured"):
            await service.generate("test prompt")

    @pytest.mark.asyncio
    async def test_aspect_ratio_passed_through(self):
        provider = FakeVideoProvider("test")
        service = VideoGenerationService(providers=[provider])

        result = await service.generate("test", aspect_ratio="9:16")

        assert result.metadata["aspect_ratio"] == "9:16"

    @pytest.mark.asyncio
    async def test_generation_type_passed_through(self):
        provider = FakeVideoProvider("test")
        service = VideoGenerationService(providers=[provider])

        result = await service.generate(
            "test", generation_type="REFERENCE_2_VIDEO", image_urls=["https://img.com/1.jpg"]
        )

        assert result.provider == "test"


class TestKieAiVeoProvider:
    """Tests for the Kie.ai Veo provider with mocked HTTP."""

    @pytest.mark.asyncio
    async def test_name(self):
        provider = KieAiVeoProvider(api_key="test-key")
        assert provider.name == "kie_ai_veo"

    @pytest.mark.asyncio
    async def test_generate_text_to_video_success(self):
        provider = KieAiVeoProvider(api_key="test-key")

        create_response = MagicMock()
        create_response.json.return_value = {"code": 200, "data": {"taskId": "task-123"}}
        create_response.raise_for_status = MagicMock()

        poll_response = MagicMock()
        poll_response.json.return_value = {
            "code": 200,
            "data": {
                "successFlag": 1,
                "response": {"resultUrls": ["https://cdn.kie.ai/video-123.mp4"]},
            },
        }
        poll_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=create_response)
        mock_client.get = AsyncMock(return_value=poll_response)

        provider._client = mock_client

        result = await provider.generate("a dancing cat")

        assert result.url == "https://cdn.kie.ai/video-123.mp4"
        assert result.provider == "kie_ai_veo"
        assert result.cost_usd == 0.40
        assert result.metadata["task_id"] == "task-123"

    @pytest.mark.asyncio
    async def test_generate_reference_to_video(self):
        provider = KieAiVeoProvider(api_key="test-key")

        create_response = MagicMock()
        create_response.json.return_value = {"code": 200, "data": {"taskId": "task-ref"}}
        create_response.raise_for_status = MagicMock()

        poll_response = MagicMock()
        poll_response.json.return_value = {
            "code": 200,
            "data": {
                "successFlag": 1,
                "response": {"resultUrls": ["https://cdn.kie.ai/ref-video.mp4"]},
            },
        }
        poll_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=create_response)
        mock_client.get = AsyncMock(return_value=poll_response)

        provider._client = mock_client

        result = await provider.generate(
            "product showcase",
            generation_type="REFERENCE_2_VIDEO",
            image_urls=["https://img.com/product.jpg"],
        )

        # Verify the POST payload included imageUrls
        call_kwargs = mock_client.post.call_args
        sent_json = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert sent_json["generationType"] == "REFERENCE_2_VIDEO"
        assert sent_json["imageUrls"] == ["https://img.com/product.jpg"]
        assert result.url == "https://cdn.kie.ai/ref-video.mp4"

    @pytest.mark.asyncio
    async def test_create_task_api_error_raises(self):
        provider = KieAiVeoProvider(api_key="test-key")

        create_response = MagicMock()
        create_response.json.return_value = {"code": 400, "msg": "Bad prompt"}
        create_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=create_response)

        provider._client = mock_client

        with pytest.raises(RuntimeError, match="Kie.ai Veo createTask failed"):
            await provider.generate("bad prompt")

    @pytest.mark.asyncio
    async def test_poll_failure_raises(self):
        provider = KieAiVeoProvider(api_key="test-key")

        create_response = MagicMock()
        create_response.json.return_value = {"code": 200, "data": {"taskId": "task-fail"}}
        create_response.raise_for_status = MagicMock()

        poll_response = MagicMock()
        poll_response.json.return_value = {
            "code": 200,
            "data": {
                "successFlag": 2,
            },
        }
        poll_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=create_response)
        mock_client.get = AsyncMock(return_value=poll_response)

        provider._client = mock_client

        with pytest.raises(RuntimeError, match="Kie.ai Veo generation failed"):
            await provider.generate("failing prompt")

    @pytest.mark.asyncio
    async def test_poll_timeout_raises(self):
        """Timeout after MAX_POLL_ATTEMPTS with successFlag=0."""
        provider = KieAiVeoProvider(api_key="test-key")

        create_response = MagicMock()
        create_response.json.return_value = {"code": 200, "data": {"taskId": "task-slow"}}
        create_response.raise_for_status = MagicMock()

        poll_response = MagicMock()
        poll_response.json.return_value = {
            "code": 200,
            "data": {"successFlag": 0},
        }
        poll_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=create_response)
        mock_client.get = AsyncMock(return_value=poll_response)

        provider._client = mock_client

        # Patch sleep to avoid waiting, and reduce max attempts
        with patch("pipeline.video_gen.MAX_POLL_ATTEMPTS", 3), \
             patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(TimeoutError, match="timed out"):
                await provider.generate("slow prompt")

    @pytest.mark.asyncio
    async def test_no_video_url_in_response_raises(self):
        provider = KieAiVeoProvider(api_key="test-key")

        create_response = MagicMock()
        create_response.json.return_value = {"code": 200, "data": {"taskId": "task-empty"}}
        create_response.raise_for_status = MagicMock()

        poll_response = MagicMock()
        poll_response.json.return_value = {
            "code": 200,
            "data": {
                "successFlag": 1,
                "response": {"resultUrls": []},
            },
        }
        poll_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=create_response)
        mock_client.get = AsyncMock(return_value=poll_response)

        provider._client = mock_client

        with pytest.raises(RuntimeError, match="no video URL"):
            await provider.generate("empty result")

    @pytest.mark.asyncio
    async def test_aspect_ratio_9_16(self):
        provider = KieAiVeoProvider(api_key="test-key")

        create_response = MagicMock()
        create_response.json.return_value = {"code": 200, "data": {"taskId": "task-vert"}}
        create_response.raise_for_status = MagicMock()

        poll_response = MagicMock()
        poll_response.json.return_value = {
            "code": 200,
            "data": {
                "successFlag": 1,
                "response": {"resultUrls": ["https://cdn.kie.ai/vert.mp4"]},
            },
        }
        poll_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=create_response)
        mock_client.get = AsyncMock(return_value=poll_response)

        provider._client = mock_client

        await provider.generate("vertical video", aspect_ratio="9:16")

        call_kwargs = mock_client.post.call_args
        sent_json = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert sent_json["aspect_ratio"] == "9:16"
