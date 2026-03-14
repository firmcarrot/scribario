"""Tests for frame generation — start+end frame pairs per scene."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from pipeline.image_gen import ImageResult
from pipeline.long_video.frame_gen import (
    FRAME_COST_USD,
    generate_all_frames,
    generate_scene_frames,
)
from pipeline.long_video.models import Scene, SceneAssets, SceneType


def _make_scene(index: int = 0) -> Scene:
    return Scene(
        index=index,
        scene_type=SceneType.A_ROLL,
        voiceover_text=f"Voiceover for scene {index}",
        visual_description=f"Visual {index}",
        start_frame_prompt=f"Start frame prompt {index}",
        end_frame_prompt=f"End frame prompt {index}",
        camera_direction="push-in",
        sfx_description="whoosh",
    )


def _make_image_result(url: str) -> ImageResult:
    return ImageResult(
        url=url,
        provider="kie_ai",
        cost_usd=FRAME_COST_USD,
        metadata={"task_id": "test-task"},
    )


class TestGenerateSceneFrames:
    async def test_calls_image_gen_with_correct_prompts(self) -> None:
        scene = _make_scene(0)
        mock_service = AsyncMock()
        mock_service.generate = AsyncMock(
            side_effect=[
                _make_image_result("https://cdn.kie.ai/start_0.jpg"),
                _make_image_result("https://cdn.kie.ai/end_0.jpg"),
            ]
        )

        await generate_scene_frames(scene, mock_service)

        assert mock_service.generate.call_count == 2
        calls = mock_service.generate.call_args_list
        assert calls[0].args[0] == "Start frame prompt 0"
        assert calls[1].args[0] == "End frame prompt 0"

    async def test_returns_scene_assets_with_frame_urls(self) -> None:
        scene = _make_scene(2)
        mock_service = AsyncMock()
        mock_service.generate = AsyncMock(
            side_effect=[
                _make_image_result("https://cdn.kie.ai/start_2.jpg"),
                _make_image_result("https://cdn.kie.ai/end_2.jpg"),
            ]
        )

        assets = await generate_scene_frames(scene, mock_service)

        assert isinstance(assets, SceneAssets)
        assert assets.scene_index == 2
        assert assets.start_frame_url == "https://cdn.kie.ai/start_2.jpg"
        assert assets.end_frame_url == "https://cdn.kie.ai/end_2.jpg"

    async def test_cost_is_two_frames(self) -> None:
        scene = _make_scene(0)
        mock_service = AsyncMock()
        mock_service.generate = AsyncMock(
            return_value=_make_image_result("https://cdn.kie.ai/frame.jpg")
        )

        assets = await generate_scene_frames(scene, mock_service)

        assert assets.cost_usd == pytest.approx(2 * FRAME_COST_USD)

    async def test_passes_aspect_ratio(self) -> None:
        scene = _make_scene(0)
        mock_service = AsyncMock()
        mock_service.generate = AsyncMock(
            return_value=_make_image_result("https://cdn.kie.ai/frame.jpg")
        )

        await generate_scene_frames(scene, mock_service, aspect_ratio="9:16")

        for call in mock_service.generate.call_args_list:
            assert call.args[1] == "9:16"


class TestGenerateAllFrames:
    async def test_generates_frames_for_all_scenes(self) -> None:
        scenes = [_make_scene(i) for i in range(3)]
        mock_service = AsyncMock()
        mock_service.generate = AsyncMock(
            return_value=_make_image_result("https://cdn.kie.ai/frame.jpg")
        )

        results = await generate_all_frames(scenes, mock_service)

        assert len(results) == 3
        assert all(isinstance(r, SceneAssets) for r in results)
        assert [r.scene_index for r in results] == [0, 1, 2]

    async def test_parallel_execution_limited_by_semaphore(self) -> None:
        """Verify semaphore limits concurrent calls to 4."""
        import asyncio

        max_concurrent = 0
        current_concurrent = 0
        lock = asyncio.Lock()

        async def _tracked_generate(prompt: str, aspect_ratio: str = "16:9") -> ImageResult:
            nonlocal max_concurrent, current_concurrent
            async with lock:
                current_concurrent += 1
                if current_concurrent > max_concurrent:
                    max_concurrent = current_concurrent
            await asyncio.sleep(0.01)  # Simulate API call
            async with lock:
                current_concurrent -= 1
            return _make_image_result(f"https://cdn.kie.ai/{prompt}.jpg")

        scenes = [_make_scene(i) for i in range(8)]
        mock_service = AsyncMock()
        mock_service.generate = AsyncMock(side_effect=_tracked_generate)

        await generate_all_frames(scenes, mock_service)

        # 8 scenes * 2 frames = 16 calls, but semaphore(4) limits concurrency
        # Each scene acquires semaphore ONCE, then runs 2 generates concurrently inside
        # So max concurrent generate calls should be <= 8 (4 scenes * 2 frames each)
        assert max_concurrent <= 8
        assert mock_service.generate.call_count == 16

    async def test_failed_scene_does_not_crash_batch(self) -> None:
        scenes = [_make_scene(i) for i in range(3)]
        call_count = 0

        async def _fail_on_scene_1(prompt: str, aspect_ratio: str = "16:9") -> ImageResult:
            nonlocal call_count
            call_count += 1
            if "prompt 1" in prompt:
                raise RuntimeError("Kie.ai API error")
            return _make_image_result(f"https://cdn.kie.ai/{prompt}.jpg")

        mock_service = AsyncMock()
        mock_service.generate = AsyncMock(side_effect=_fail_on_scene_1)

        results = await generate_all_frames(scenes, mock_service)

        assert len(results) == 3
        # Scene 0 and 2 should have URLs
        assert results[0].start_frame_url is not None
        assert results[2].start_frame_url is not None
        # Scene 1 failed — URLs should be None
        assert results[1].scene_index == 1
        assert results[1].start_frame_url is None
        assert results[1].end_frame_url is None

    async def test_creates_default_image_service_when_none(self) -> None:
        scenes = [_make_scene(0)]

        with patch(
            "pipeline.long_video.frame_gen.ImageGenerationService"
        ) as MockService:
            mock_instance = AsyncMock()
            mock_instance.generate = AsyncMock(
                return_value=_make_image_result("https://cdn.kie.ai/frame.jpg")
            )
            MockService.return_value = mock_instance

            results = await generate_all_frames(scenes)

            MockService.assert_called_once()
            assert len(results) == 1
