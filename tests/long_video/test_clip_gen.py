"""Tests for video clip generation with 3-level fallback chain."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from pipeline.long_video.clip_gen import generate_all_clips, generate_scene_clip
from pipeline.long_video.models import SceneAssets
from pipeline.video_gen import VideoGenerationService, VideoResult

SILENT_SUFFIX = " No music, no sound effects, no dialogue."


def _make_assets(
    index: int = 0,
    start_frame: str | None = "https://img.test/start.png",
    end_frame: str | None = "https://img.test/end.png",
    vo_duration: float = 8.0,
) -> SceneAssets:
    return SceneAssets(
        scene_index=index,
        start_frame_url=start_frame,
        end_frame_url=end_frame,
        voiceover_duration_seconds=vo_duration,
    )


def _ok_result(url: str = "https://video.test/clip.mp4") -> VideoResult:
    return VideoResult(url=url, provider="kie_ai_veo", cost_usd=0.40, metadata={})


# ---------------------------------------------------------------------------
# 1. Primary: FIRST_AND_LAST_FRAMES_2_VIDEO
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_scene_clip_uses_first_and_last_frames() -> None:
    """Primary path: both frames available -> FIRST_AND_LAST_FRAMES_2_VIDEO."""
    svc = AsyncMock(spec=VideoGenerationService)
    svc.generate = AsyncMock(return_value=_ok_result())
    assets = _make_assets()
    prompt = "A shrimp boat at sunset"

    result = await generate_scene_clip(assets, prompt, svc)

    svc.generate.assert_called_once_with(
        prompt=prompt + SILENT_SUFFIX,
        aspect_ratio="16:9",
        generation_type="FIRST_AND_LAST_FRAMES_2_VIDEO",
        image_urls=["https://img.test/start.png", "https://img.test/end.png"],
    )
    assert result.video_clip_url == "https://video.test/clip.mp4"
    assert result.cost_usd == 0.40


# ---------------------------------------------------------------------------
# 2. Fallback to REFERENCE_2_VIDEO
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fallback_to_reference_2_video() -> None:
    """When primary fails, fall back to REFERENCE_2_VIDEO with start frame."""
    svc = AsyncMock(spec=VideoGenerationService)
    svc.generate = AsyncMock(
        side_effect=[
            RuntimeError("FIRST_AND_LAST failed"),
            _ok_result("https://video.test/ref.mp4"),
        ]
    )
    assets = _make_assets()
    prompt = "Spicy sauce close-up"

    result = await generate_scene_clip(assets, prompt, svc)

    assert svc.generate.call_count == 2
    second_call = svc.generate.call_args_list[1]
    assert second_call.kwargs["generation_type"] == "REFERENCE_2_VIDEO"
    assert second_call.kwargs["image_urls"] == ["https://img.test/start.png"]
    assert result.video_clip_url == "https://video.test/ref.mp4"


# ---------------------------------------------------------------------------
# 3. Fallback to TEXT_2_VIDEO
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fallback_to_text_2_video() -> None:
    """When both frame-based methods fail, fall back to TEXT_2_VIDEO."""
    svc = AsyncMock(spec=VideoGenerationService)
    svc.generate = AsyncMock(
        side_effect=[
            RuntimeError("FIRST_AND_LAST failed"),
            RuntimeError("REFERENCE failed"),
            _ok_result("https://video.test/txt.mp4"),
        ]
    )
    assets = _make_assets()
    prompt = "Ocean waves"

    result = await generate_scene_clip(assets, prompt, svc)

    assert svc.generate.call_count == 3
    third_call = svc.generate.call_args_list[2]
    assert third_call.kwargs["generation_type"] == "TEXT_2_VIDEO"
    assert third_call.kwargs["image_urls"] is None
    assert result.video_clip_url == "https://video.test/txt.mp4"


# ---------------------------------------------------------------------------
# 4. Parallel generation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_all_clips_runs_in_parallel() -> None:
    """All clips should be generated (parallel), each getting its own result."""
    svc = AsyncMock(spec=VideoGenerationService)
    svc.generate = AsyncMock(
        side_effect=[
            _ok_result("https://video.test/c0.mp4"),
            _ok_result("https://video.test/c1.mp4"),
            _ok_result("https://video.test/c2.mp4"),
        ]
    )
    assets_list = [_make_assets(i) for i in range(3)]
    prompts = ["scene zero", "scene one", "scene two"]

    results = await generate_all_clips(assets_list, prompts, svc)

    assert len(results) == 3
    assert results[0].video_clip_url == "https://video.test/c0.mp4"
    assert results[1].video_clip_url == "https://video.test/c1.mp4"
    assert results[2].video_clip_url == "https://video.test/c2.mp4"


# ---------------------------------------------------------------------------
# 5. All three methods fail -> video_clip_url stays None
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_all_methods_fail_returns_none_video() -> None:
    """When every fallback fails, video_clip_url remains None."""
    svc = AsyncMock(spec=VideoGenerationService)
    svc.generate = AsyncMock(side_effect=RuntimeError("always fails"))
    assets = _make_assets()
    prompt = "Impossible scene"

    result = await generate_scene_clip(assets, prompt, svc)

    assert result.video_clip_url is None
    assert result.cost_usd == 0.0


# ---------------------------------------------------------------------------
# 6. Missing frames skip frame-based methods
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_frames_skips_to_text_2_video() -> None:
    """No start/end frames -> go straight to TEXT_2_VIDEO."""
    svc = AsyncMock(spec=VideoGenerationService)
    svc.generate = AsyncMock(return_value=_ok_result())
    assets = _make_assets(start_frame=None, end_frame=None)
    prompt = "Abstract visuals"

    result = await generate_scene_clip(assets, prompt, svc)

    svc.generate.assert_called_once()
    call = svc.generate.call_args
    assert call.kwargs["generation_type"] == "TEXT_2_VIDEO"
    assert call.kwargs["image_urls"] is None
    assert result.video_clip_url == "https://video.test/clip.mp4"


@pytest.mark.asyncio
async def test_only_start_frame_skips_first_and_last() -> None:
    """Only start frame -> skip FIRST_AND_LAST, go to REFERENCE_2_VIDEO."""
    svc = AsyncMock(spec=VideoGenerationService)
    svc.generate = AsyncMock(return_value=_ok_result())
    assets = _make_assets(end_frame=None)
    prompt = "Partial frames"

    result = await generate_scene_clip(assets, prompt, svc)

    svc.generate.assert_called_once()
    call = svc.generate.call_args
    assert call.kwargs["generation_type"] == "REFERENCE_2_VIDEO"
    assert call.kwargs["image_urls"] == ["https://img.test/start.png"]
