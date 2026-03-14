"""Tests for the long-form video pipeline orchestrator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.brand_voice import BrandProfile
from pipeline.long_video.models import (
    LongVideoScript,
    Scene,
    SceneAssets,
    SceneType,
    StitchResult,
    StitchSpec,
)
from pipeline.long_video.sfx import SFXResult
from pipeline.long_video.tts import TTSResult
from pipeline.long_video.voice_library import VoiceInfo


def _make_profile(**overrides) -> BrandProfile:
    defaults = {
        "tenant_id": "test-tenant",
        "name": "TestBrand",
        "tone_words": ["bold"],
        "audience_description": "test audience",
        "do_list": ["be cool"],
        "dont_list": ["be boring"],
    }
    defaults.update(overrides)
    return BrandProfile(**defaults)


def _make_scene(index: int) -> Scene:
    return Scene(
        index=index,
        scene_type=SceneType.A_ROLL if index % 2 == 0 else SceneType.B_ROLL,
        voiceover_text=f"Scene {index} voiceover text.",
        visual_description=f"Scene {index} visual",
        start_frame_prompt=f"Start frame {index}",
        end_frame_prompt=f"End frame {index}",
        camera_direction="slow push-in",
        sfx_description=f"ambient sound {index}",
    )


def _make_script(num_scenes: int = 4) -> LongVideoScript:
    return LongVideoScript(
        title="Test Video",
        voice_style="warm narrator",
        scenes=[_make_scene(i) for i in range(num_scenes)],
    )


def _make_tts_result(index: int) -> TTSResult:
    return TTSResult(
        audio_url=f"/tmp/tts_{index}.mp3",
        duration_seconds=7.5,
        cost_usd=0.01,
    )


def _make_scene_assets_with_frames(index: int) -> SceneAssets:
    return SceneAssets(
        scene_index=index,
        start_frame_url=f"https://example.com/start_{index}.png",
        end_frame_url=f"https://example.com/end_{index}.png",
        cost_usd=0.08,
    )


def _make_scene_assets_with_clip(index: int) -> SceneAssets:
    return SceneAssets(
        scene_index=index,
        start_frame_url=f"https://example.com/start_{index}.png",
        end_frame_url=f"https://example.com/end_{index}.png",
        video_clip_url=f"https://example.com/clip_{index}.mp4",
        cost_usd=0.48,
    )


def _make_sfx_result(index: int) -> SFXResult:
    return SFXResult(
        audio_path=f"/tmp/sfx_{index}.mp3",
        cost_usd=0.01,
    )


def _make_stitch_result() -> StitchResult:
    return StitchResult(
        output_path="/tmp/scribario/test-project/final.mp4",
        duration_seconds=30.0,
        file_size_bytes=5_000_000,
    )


# Shared patch targets
_PATCHES = {
    "load_brand_profile": "pipeline.long_video.orchestrator.load_brand_profile",
    "load_few_shot_examples": "pipeline.long_video.orchestrator.load_few_shot_examples",
    "generate_script": "pipeline.long_video.orchestrator.generate_script",
    "get_voice_from_pool_or_create": "pipeline.long_video.voice_library.get_voice_from_pool_or_create",
    "generate_voiceover": "pipeline.long_video.orchestrator.generate_voiceover",
    "generate_all_frames": "pipeline.long_video.orchestrator.generate_all_frames",
    "generate_all_clips": "pipeline.long_video.orchestrator.generate_all_clips",
    "generate_sfx_batch": "pipeline.long_video.orchestrator.generate_sfx_batch",
    "stitch": "pipeline.long_video.orchestrator.stitch",
    "log_usage_event": "pipeline.long_video.orchestrator.log_usage_event",
    "get_settings": "pipeline.long_video.orchestrator.get_settings",
}

# Patch targets for prompt engine (used in orchestrator's auto-plan generation)
_PROMPT_ENGINE_PATCHES = {
    "resolve_assets": "pipeline.prompt_engine.asset_resolver.resolve_assets",
    "generate_plan": "pipeline.prompt_engine.engine.generate_plan",
}


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.long_video_max_cost_usd = 10.0
    return settings


@pytest.fixture
def happy_path_mocks(mock_settings):
    """Set up all mocks for a successful 4-scene pipeline run."""
    script = _make_script(4)

    with (
        patch(_PATCHES["load_brand_profile"], new_callable=AsyncMock) as m_load_brand,
        patch(_PATCHES["load_few_shot_examples"], new_callable=AsyncMock) as m_examples,
        patch(_PATCHES["generate_script"], new_callable=AsyncMock) as m_script,
        patch(_PATCHES["get_voice_from_pool_or_create"], new_callable=AsyncMock) as m_voice,
        patch(_PATCHES["generate_voiceover"], new_callable=AsyncMock) as m_tts,
        patch(_PATCHES["generate_all_frames"], new_callable=AsyncMock) as m_frames,
        patch(_PATCHES["generate_all_clips"], new_callable=AsyncMock) as m_clips,
        patch(_PATCHES["generate_sfx_batch"], new_callable=AsyncMock) as m_sfx,
        patch(_PATCHES["stitch"], new_callable=AsyncMock) as m_stitch,
        patch(_PATCHES["log_usage_event"], new_callable=AsyncMock) as m_log,
        patch(_PATCHES["get_settings"]) as m_settings,
        patch(_PROMPT_ENGINE_PATCHES["resolve_assets"], new_callable=AsyncMock) as m_resolve,
        patch(_PROMPT_ENGINE_PATCHES["generate_plan"], new_callable=AsyncMock) as m_gen_plan,
        patch("pipeline.long_video.orchestrator.shutil.rmtree") as m_rmtree,
        patch("pipeline.long_video.orchestrator.shutil.copy2") as m_copy2,
        patch("pipeline.long_video.orchestrator.os.makedirs") as m_makedirs,
        patch("pipeline.long_video.orchestrator.os.path.exists", return_value=True),
    ):
        m_load_brand.return_value = _make_profile()
        m_examples.return_value = []
        # Prompt engine fails → falls back to legacy generate_script
        m_gen_plan.side_effect = RuntimeError("No API key in test")
        m_script.return_value = script
        m_voice.return_value = VoiceInfo(voice_id="voice-123", name="Brand Voice", is_new=False)
        m_tts.side_effect = [_make_tts_result(i) for i in range(4)]
        m_frames.return_value = [_make_scene_assets_with_frames(i) for i in range(4)]
        m_clips.return_value = [_make_scene_assets_with_clip(i) for i in range(4)]
        m_sfx.return_value = [_make_sfx_result(i) for i in range(4)]
        m_stitch.return_value = _make_stitch_result()
        m_settings.return_value = mock_settings

        yield {
            "load_brand_profile": m_load_brand,
            "load_few_shot_examples": m_examples,
            "generate_script": m_script,
            "generate_plan": m_gen_plan,
            "resolve_assets": m_resolve,
            "get_voice_from_pool_or_create": m_voice,
            "generate_voiceover": m_tts,
            "generate_all_frames": m_frames,
            "generate_all_clips": m_clips,
            "generate_sfx_batch": m_sfx,
            "stitch": m_stitch,
            "log_usage_event": m_log,
            "get_settings": m_settings,
            "rmtree": m_rmtree,
            "copy2": m_copy2,
            "makedirs": m_makedirs,
        }


class TestHappyPath:
    """Test full pipeline happy path with all sub-modules mocked."""

    async def test_returns_pipeline_result(self, happy_path_mocks):
        from pipeline.long_video.orchestrator import PipelineResult, run_pipeline

        result = await run_pipeline(
            tenant_id="test-tenant",
            project_id="test-project",
            intent="Make a cool video about hot sauce",
        )

        assert isinstance(result, PipelineResult)
        assert result.project_id == "test-project"
        assert result.video_path == "/tmp/scribario-output/test-project.mp4"
        assert result.duration_seconds == 30.0
        assert result.scene_count == 4
        assert result.scenes_completed == 4
        assert result.total_cost_usd > 0

    async def test_calls_pipeline_steps_in_order(self, happy_path_mocks):
        from pipeline.long_video.orchestrator import run_pipeline

        await run_pipeline(
            tenant_id="test-tenant",
            project_id="test-project",
            intent="Make a cool video",
        )

        # Script generation
        happy_path_mocks["generate_script"].assert_awaited_once()
        # Voice lookup
        happy_path_mocks["get_voice_from_pool_or_create"].assert_awaited_once()
        # TTS called 4 times (one per scene)
        assert happy_path_mocks["generate_voiceover"].await_count == 4
        # Frame generation
        happy_path_mocks["generate_all_frames"].assert_awaited_once()
        # Clip generation
        happy_path_mocks["generate_all_clips"].assert_awaited_once()
        # SFX generation
        happy_path_mocks["generate_sfx_batch"].assert_awaited_once()
        # Stitching
        happy_path_mocks["stitch"].assert_awaited_once()

    async def test_stitch_receives_correct_spec(self, happy_path_mocks):
        from pipeline.long_video.orchestrator import run_pipeline

        await run_pipeline(
            tenant_id="test-tenant",
            project_id="test-project",
            intent="Make a cool video",
        )

        stitch_call = happy_path_mocks["stitch"].call_args
        spec = stitch_call[0][0]
        assert isinstance(spec, StitchSpec)
        assert spec.project_id == "test-project"
        assert len(spec.scene_clips) == 4
        assert len(spec.scene_voiceovers) == 4
        assert len(spec.scene_sfx) == 4

    async def test_logs_usage_events(self, happy_path_mocks):
        from pipeline.long_video.orchestrator import run_pipeline

        await run_pipeline(
            tenant_id="test-tenant",
            project_id="test-project",
            intent="Make a cool video",
        )

        # Should log usage for script gen, TTS, frames, clips, SFX at minimum
        assert happy_path_mocks["log_usage_event"].await_count >= 1

    async def test_cleans_up_temp_dir(self, happy_path_mocks):
        from pipeline.long_video.orchestrator import run_pipeline

        await run_pipeline(
            tenant_id="test-tenant",
            project_id="test-project",
            intent="Make a cool video",
        )

        happy_path_mocks["rmtree"].assert_called_once()


class TestStatusCallback:
    """Test that status_callback gets called at each stage."""

    async def test_callback_called_at_each_stage(self, happy_path_mocks):
        from pipeline.long_video.orchestrator import run_pipeline

        callback = AsyncMock()

        await run_pipeline(
            tenant_id="test-tenant",
            project_id="test-project",
            intent="Make a cool video",
            status_callback=callback,
        )

        # Extract all status values passed to callback
        statuses = [call.args[0] for call in callback.call_args_list]

        # Should have called back for each major stage
        assert "scripting" in statuses
        assert "tts" in statuses
        assert "generating_frames" in statuses
        assert "generating_clips" in statuses
        assert "stitching" in statuses

    async def test_callback_not_required(self, happy_path_mocks):
        from pipeline.long_video.orchestrator import run_pipeline

        # Should not raise when no callback provided
        result = await run_pipeline(
            tenant_id="test-tenant",
            project_id="test-project",
            intent="Make a cool video",
        )
        assert result is not None


class TestCostLimit:
    """Test cost limit enforcement."""

    async def test_aborts_when_cost_exceeds_limit(self, mock_settings):
        from pipeline.long_video.orchestrator import run_pipeline

        # Set very low cost limit
        mock_settings.long_video_max_cost_usd = 0.01

        script = _make_script(4)

        with (
            patch(_PATCHES["load_brand_profile"], new_callable=AsyncMock) as m_load_brand,
            patch(_PATCHES["load_few_shot_examples"], new_callable=AsyncMock) as m_examples,
            patch(_PATCHES["generate_script"], new_callable=AsyncMock) as m_script,
            patch(_PATCHES["get_voice_from_pool_or_create"], new_callable=AsyncMock) as m_voice,
            patch(_PATCHES["generate_voiceover"], new_callable=AsyncMock) as m_tts,
            patch(_PATCHES["generate_all_frames"], new_callable=AsyncMock) as m_frames,
            patch(_PATCHES["generate_all_clips"], new_callable=AsyncMock) as m_clips,
            patch(_PATCHES["generate_sfx_batch"], new_callable=AsyncMock) as m_sfx,
            patch(_PATCHES["stitch"], new_callable=AsyncMock) as m_stitch,
            patch(_PATCHES["log_usage_event"], new_callable=AsyncMock),
            patch(_PATCHES["get_settings"]) as m_settings,
            patch(_PROMPT_ENGINE_PATCHES["resolve_assets"], new_callable=AsyncMock),
            patch(_PROMPT_ENGINE_PATCHES["generate_plan"], new_callable=AsyncMock, side_effect=RuntimeError("No API key")),
            patch("pipeline.long_video.orchestrator.shutil.rmtree"),
            patch("pipeline.long_video.orchestrator.shutil.copy2"),
            patch("pipeline.long_video.orchestrator.os.makedirs"),
            patch("pipeline.long_video.orchestrator.os.path.exists", return_value=True),
        ):
            m_load_brand.return_value = _make_profile()
            m_examples.return_value = []
            m_script.return_value = script
            m_voice.return_value = VoiceInfo(
                voice_id="voice-123", name="Brand Voice", is_new=False
            )
            # TTS costs add up beyond the $0.01 limit
            m_tts.side_effect = [_make_tts_result(i) for i in range(4)]
            m_frames.return_value = [_make_scene_assets_with_frames(i) for i in range(4)]
            m_clips.return_value = [_make_scene_assets_with_clip(i) for i in range(4)]
            m_sfx.return_value = [_make_sfx_result(i) for i in range(4)]
            m_stitch.return_value = _make_stitch_result()
            m_settings.return_value = mock_settings

            with pytest.raises(RuntimeError, match=r"[Cc]ost"):
                await run_pipeline(
                    tenant_id="test-tenant",
                    project_id="test-project",
                    intent="Make a cool video",
                )


class TestPartialSceneFailure:
    """Test that pipeline continues when some scenes fail."""

    async def test_tts_failure_skips_scene(self, mock_settings):
        """When TTS fails for a scene, that scene is excluded from stitch."""
        from pipeline.long_video.orchestrator import run_pipeline

        script = _make_script(4)

        with (
            patch(_PATCHES["load_brand_profile"], new_callable=AsyncMock) as m_load_brand,
            patch(_PATCHES["load_few_shot_examples"], new_callable=AsyncMock) as m_examples,
            patch(_PATCHES["generate_script"], new_callable=AsyncMock) as m_script,
            patch(_PATCHES["get_voice_from_pool_or_create"], new_callable=AsyncMock) as m_voice,
            patch(_PATCHES["generate_voiceover"], new_callable=AsyncMock) as m_tts,
            patch(_PATCHES["generate_all_frames"], new_callable=AsyncMock) as m_frames,
            patch(_PATCHES["generate_all_clips"], new_callable=AsyncMock) as m_clips,
            patch(_PATCHES["generate_sfx_batch"], new_callable=AsyncMock) as m_sfx,
            patch(_PATCHES["stitch"], new_callable=AsyncMock) as m_stitch,
            patch(_PATCHES["log_usage_event"], new_callable=AsyncMock),
            patch(_PATCHES["get_settings"]) as m_settings,
            patch(_PROMPT_ENGINE_PATCHES["resolve_assets"], new_callable=AsyncMock),
            patch(_PROMPT_ENGINE_PATCHES["generate_plan"], new_callable=AsyncMock, side_effect=RuntimeError("No API key")),
            patch("pipeline.long_video.orchestrator.shutil.rmtree"),
            patch("pipeline.long_video.orchestrator.shutil.copy2"),
            patch("pipeline.long_video.orchestrator.os.makedirs"),
            patch("pipeline.long_video.orchestrator.os.path.exists", return_value=True),
        ):
            m_load_brand.return_value = _make_profile()
            m_examples.return_value = []
            m_script.return_value = script
            m_voice.return_value = VoiceInfo(
                voice_id="voice-123", name="Brand Voice", is_new=False
            )

            # Scene 1 TTS fails
            m_tts.side_effect = [
                _make_tts_result(0),
                Exception("TTS API error"),
                _make_tts_result(2),
                _make_tts_result(3),
            ]

            # Only 3 scenes get frames/clips (scene 1 was filtered out after TTS)
            m_frames.return_value = [
                _make_scene_assets_with_frames(0),
                _make_scene_assets_with_frames(2),
                _make_scene_assets_with_frames(3),
            ]
            m_clips.return_value = [
                _make_scene_assets_with_clip(0),
                _make_scene_assets_with_clip(2),
                _make_scene_assets_with_clip(3),
            ]
            m_sfx.return_value = [
                _make_sfx_result(0),
                _make_sfx_result(2),
                _make_sfx_result(3),
            ]
            m_stitch.return_value = _make_stitch_result()
            m_settings.return_value = mock_settings

            result = await run_pipeline(
                tenant_id="test-tenant",
                project_id="test-project",
                intent="Make a cool video",
            )

            assert result.scenes_completed == 3
            assert result.scene_count == 4

            # Stitch should only receive 3 scenes
            spec = m_stitch.call_args[0][0]
            assert len(spec.scene_clips) == 3
            assert len(spec.scene_voiceovers) == 3

    async def test_clip_gen_failure_skips_scene(self, mock_settings):
        """When clip gen fails for a scene, it's excluded from stitch."""
        from pipeline.long_video.orchestrator import run_pipeline

        script = _make_script(4)

        with (
            patch(_PATCHES["load_brand_profile"], new_callable=AsyncMock) as m_load_brand,
            patch(_PATCHES["load_few_shot_examples"], new_callable=AsyncMock) as m_examples,
            patch(_PATCHES["generate_script"], new_callable=AsyncMock) as m_script,
            patch(_PATCHES["get_voice_from_pool_or_create"], new_callable=AsyncMock) as m_voice,
            patch(_PATCHES["generate_voiceover"], new_callable=AsyncMock) as m_tts,
            patch(_PATCHES["generate_all_frames"], new_callable=AsyncMock) as m_frames,
            patch(_PATCHES["generate_all_clips"], new_callable=AsyncMock) as m_clips,
            patch(_PATCHES["generate_sfx_batch"], new_callable=AsyncMock) as m_sfx,
            patch(_PATCHES["stitch"], new_callable=AsyncMock) as m_stitch,
            patch(_PATCHES["log_usage_event"], new_callable=AsyncMock),
            patch(_PATCHES["get_settings"]) as m_settings,
            patch(_PROMPT_ENGINE_PATCHES["resolve_assets"], new_callable=AsyncMock),
            patch(_PROMPT_ENGINE_PATCHES["generate_plan"], new_callable=AsyncMock, side_effect=RuntimeError("No API key")),
            patch("pipeline.long_video.orchestrator.shutil.rmtree"),
            patch("pipeline.long_video.orchestrator.shutil.copy2"),
            patch("pipeline.long_video.orchestrator.os.makedirs"),
            patch("pipeline.long_video.orchestrator.os.path.exists", return_value=True),
        ):
            m_load_brand.return_value = _make_profile()
            m_examples.return_value = []
            m_script.return_value = script
            m_voice.return_value = VoiceInfo(
                voice_id="voice-123", name="Brand Voice", is_new=False
            )
            m_tts.side_effect = [_make_tts_result(i) for i in range(4)]
            m_frames.return_value = [_make_scene_assets_with_frames(i) for i in range(4)]

            # Scene 2 has no clip (clip gen failed)
            clips = [_make_scene_assets_with_clip(i) for i in range(4)]
            clips[2].video_clip_url = None  # Failed
            m_clips.return_value = clips

            m_sfx.return_value = [_make_sfx_result(i) for i in range(4)]
            m_stitch.return_value = _make_stitch_result()
            m_settings.return_value = mock_settings

            result = await run_pipeline(
                tenant_id="test-tenant",
                project_id="test-project",
                intent="Make a cool video",
            )

            assert result.scenes_completed == 3

            spec = m_stitch.call_args[0][0]
            assert len(spec.scene_clips) == 3


class TestScriptGenFailure:
    """Test that pipeline fails early when script generation fails."""

    async def test_script_gen_error_raises(self, mock_settings):
        from pipeline.long_video.orchestrator import run_pipeline

        with (
            patch(_PATCHES["load_brand_profile"], new_callable=AsyncMock) as m_load_brand,
            patch(_PATCHES["load_few_shot_examples"], new_callable=AsyncMock) as m_examples,
            patch(_PATCHES["generate_script"], new_callable=AsyncMock) as m_script,
            patch(_PATCHES["log_usage_event"], new_callable=AsyncMock),
            patch(_PATCHES["get_settings"]) as m_settings,
            patch(_PROMPT_ENGINE_PATCHES["resolve_assets"], new_callable=AsyncMock),
            patch(_PROMPT_ENGINE_PATCHES["generate_plan"], new_callable=AsyncMock, side_effect=RuntimeError("No API key")),
            patch("pipeline.long_video.orchestrator.shutil.rmtree"),
            patch("pipeline.long_video.orchestrator.shutil.copy2"),
            patch("pipeline.long_video.orchestrator.os.makedirs"),
            patch("pipeline.long_video.orchestrator.os.path.exists", return_value=True),
        ):
            m_load_brand.return_value = _make_profile()
            m_examples.return_value = []
            m_script.side_effect = RuntimeError("Claude API failed")
            m_settings.return_value = mock_settings

            with pytest.raises(RuntimeError, match="Claude API failed"):
                await run_pipeline(
                    tenant_id="test-tenant",
                    project_id="test-project",
                    intent="Make a cool video",
                )


class TestBrandProfileNotFound:
    """Test that pipeline uses default profile when brand profile not found."""

    async def test_uses_default_profile(self, mock_settings):
        from pipeline.long_video.orchestrator import run_pipeline

        script = _make_script(4)

        with (
            patch(_PATCHES["load_brand_profile"], new_callable=AsyncMock) as m_load_brand,
            patch(_PATCHES["load_few_shot_examples"], new_callable=AsyncMock) as m_examples,
            patch(_PATCHES["generate_script"], new_callable=AsyncMock) as m_script,
            patch(_PATCHES["get_voice_from_pool_or_create"], new_callable=AsyncMock) as m_voice,
            patch(_PATCHES["generate_voiceover"], new_callable=AsyncMock) as m_tts,
            patch(_PATCHES["generate_all_frames"], new_callable=AsyncMock) as m_frames,
            patch(_PATCHES["generate_all_clips"], new_callable=AsyncMock) as m_clips,
            patch(_PATCHES["generate_sfx_batch"], new_callable=AsyncMock) as m_sfx,
            patch(_PATCHES["stitch"], new_callable=AsyncMock) as m_stitch,
            patch(_PATCHES["log_usage_event"], new_callable=AsyncMock),
            patch(_PATCHES["get_settings"]) as m_settings,
            patch(_PROMPT_ENGINE_PATCHES["resolve_assets"], new_callable=AsyncMock),
            patch(_PROMPT_ENGINE_PATCHES["generate_plan"], new_callable=AsyncMock, side_effect=RuntimeError("No API key")),
            patch("pipeline.long_video.orchestrator.shutil.rmtree"),
            patch("pipeline.long_video.orchestrator.shutil.copy2"),
            patch("pipeline.long_video.orchestrator.os.makedirs"),
            patch("pipeline.long_video.orchestrator.os.path.exists", return_value=True),
        ):
            m_load_brand.return_value = None  # Brand not found
            m_examples.return_value = []
            m_script.return_value = script
            m_voice.return_value = VoiceInfo(
                voice_id="voice-123", name="Brand Voice", is_new=False
            )
            m_tts.side_effect = [_make_tts_result(i) for i in range(4)]
            m_frames.return_value = [_make_scene_assets_with_frames(i) for i in range(4)]
            m_clips.return_value = [_make_scene_assets_with_clip(i) for i in range(4)]
            m_sfx.return_value = [_make_sfx_result(i) for i in range(4)]
            m_stitch.return_value = _make_stitch_result()
            m_settings.return_value = mock_settings

            result = await run_pipeline(
                tenant_id="test-tenant",
                project_id="test-project",
                intent="Make a cool video",
            )

            # Should still succeed with a default profile
            assert result is not None
            assert result.video_path == "/tmp/scribario-output/test-project.mp4"

            # generate_script should have been called with a BrandProfile
            call_args = m_script.call_args
            profile_arg = call_args[0][1]
            assert isinstance(profile_arg, BrandProfile)
