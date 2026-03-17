"""Tests for FFmpeg stitcher — normalize, transitions, audio mix, orchestration."""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from pipeline.long_video.models import StitchResult, StitchSpec
from pipeline.long_video.stitcher import (
    _resolution,
    _run_ffmpeg,
    build_audio_mix_command,
    build_normalize_command,
    build_xfade_command,
    stitch,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_spec(**overrides) -> StitchSpec:
    defaults = dict(
        project_id="test-proj-001",
        scene_clips=["/tmp/clip0.mp4", "/tmp/clip1.mp4", "/tmp/clip2.mp4"],
        scene_voiceovers=["/tmp/vo0.mp3", "/tmp/vo1.mp3", "/tmp/vo2.mp3"],
        aspect_ratio="16:9",
        transition_duration=0.5,
        sfx_volume=0.3,
        scene_sfx=["/tmp/sfx0.mp3", "/tmp/sfx1.mp3"],
    )
    defaults.update(overrides)
    return StitchSpec(**defaults)


# ---------------------------------------------------------------------------
# Resolution helper
# ---------------------------------------------------------------------------

class TestResolution:
    def test_landscape_16_9(self) -> None:
        assert _resolution("16:9") == (1920, 1080)

    def test_portrait_9_16(self) -> None:
        assert _resolution("9:16") == (1080, 1920)

    def test_default_is_landscape(self) -> None:
        assert _resolution("4:3") == (1920, 1080)


# ---------------------------------------------------------------------------
# build_normalize_command
# ---------------------------------------------------------------------------

class TestBuildNormalizeCommand:
    def test_16_9_resolution_and_fps(self) -> None:
        args = build_normalize_command("/tmp/clip.mp4", "/tmp/norm.mp4", "16:9")
        assert "-i" in args
        assert "/tmp/clip.mp4" in args
        assert "/tmp/norm.mp4" in args
        # Check scale filter targets 1920x1080
        vf_idx = args.index("-vf")
        vf_filter = args[vf_idx + 1]
        assert "1920" in vf_filter
        assert "1080" in vf_filter
        assert "fps=30" in vf_filter
        assert "force_original_aspect_ratio=decrease" in vf_filter
        assert "pad=" in vf_filter

    def test_9_16_resolution(self) -> None:
        args = build_normalize_command("/tmp/clip.mp4", "/tmp/norm.mp4", "9:16")
        vf_idx = args.index("-vf")
        vf_filter = args[vf_idx + 1]
        assert "1080" in vf_filter
        assert "1920" in vf_filter

    def test_overwrite_flag(self) -> None:
        args = build_normalize_command("/tmp/clip.mp4", "/tmp/norm.mp4", "16:9")
        assert "-y" in args

    def test_no_audio_in_normalize(self) -> None:
        args = build_normalize_command("/tmp/clip.mp4", "/tmp/norm.mp4", "16:9")
        assert "-an" in args


# ---------------------------------------------------------------------------
# build_xfade_command
# ---------------------------------------------------------------------------

class TestBuildXfadeCommand:
    def test_two_clips_single_xfade(self) -> None:
        clips = ["/tmp/n0.mp4", "/tmp/n1.mp4"]
        durations = [5.0, 4.0]
        args = build_xfade_command(clips, durations, "/tmp/xfade.mp4", 0.5)
        assert "-filter_complex" in args
        fc_idx = args.index("-filter_complex")
        fc = args[fc_idx + 1]
        assert "xfade" in fc
        assert "fade" in fc
        assert "duration=0.5" in fc
        # offset = first clip duration - transition_duration
        assert "offset=4.5" in fc

    def test_three_clips_chained_xfade(self) -> None:
        clips = ["/tmp/n0.mp4", "/tmp/n1.mp4", "/tmp/n2.mp4"]
        durations = [5.0, 4.0, 3.0]
        args = build_xfade_command(clips, durations, "/tmp/xfade.mp4", 0.5)
        fc_idx = args.index("-filter_complex")
        fc = args[fc_idx + 1]
        # Should have two xfade filters chained
        assert fc.count("xfade") == 2

    def test_all_inputs_listed(self) -> None:
        clips = ["/tmp/n0.mp4", "/tmp/n1.mp4", "/tmp/n2.mp4"]
        durations = [5.0, 4.0, 3.0]
        args = build_xfade_command(clips, durations, "/tmp/xfade.mp4", 0.5)
        for clip in clips:
            assert clip in args

    def test_single_clip_no_xfade(self) -> None:
        clips = ["/tmp/n0.mp4"]
        durations = [5.0]
        args = build_xfade_command(clips, durations, "/tmp/xfade.mp4", 0.5)
        # Single clip: no filter_complex needed, just copy
        assert "-filter_complex" not in args


# ---------------------------------------------------------------------------
# build_audio_mix_command
# ---------------------------------------------------------------------------

class TestBuildAudioMixCommand:
    def test_voiceover_only(self) -> None:
        args = build_audio_mix_command(
            voiceovers=["/tmp/vo0.mp3", "/tmp/vo1.mp3"],
            sfx=[],
            output_path="/tmp/audio.mp3",
            sfx_volume=0.3,
        )
        for vo in ["/tmp/vo0.mp3", "/tmp/vo1.mp3"]:
            assert vo in args
        assert "/tmp/audio.mp3" in args

    def test_voiceover_plus_sfx(self) -> None:
        args = build_audio_mix_command(
            voiceovers=["/tmp/vo0.mp3"],
            sfx=["/tmp/sfx0.mp3"],
            output_path="/tmp/audio.mp3",
            sfx_volume=0.3,
        )
        assert "/tmp/sfx0.mp3" in args
        fc_idx = args.index("-filter_complex")
        fc = args[fc_idx + 1]
        # SFX should have volume=0.3 applied
        assert "volume=0.3" in fc
        assert "amix" in fc

    def test_sfx_volume_customizable(self) -> None:
        args = build_audio_mix_command(
            voiceovers=["/tmp/vo0.mp3"],
            sfx=["/tmp/sfx0.mp3"],
            output_path="/tmp/audio.mp3",
            sfx_volume=0.5,
        )
        fc_idx = args.index("-filter_complex")
        fc = args[fc_idx + 1]
        assert "volume=0.5" in fc

    def test_sfx_only_no_voiceovers_single_sfx(self) -> None:
        """SFX-only mode: no voiceovers, single SFX → volume-adjusted copy."""
        args = build_audio_mix_command(
            voiceovers=[],
            sfx=["/tmp/sfx0.mp3"],
            output_path="/tmp/audio.mp3",
            sfx_volume=0.8,
        )
        assert "/tmp/sfx0.mp3" in args
        assert "/tmp/audio.mp3" in args
        fc_idx = args.index("-filter_complex")
        fc = args[fc_idx + 1]
        assert "volume=0.8" in fc
        # Should NOT have amix (no voiceover to mix with)
        assert "amix" not in fc
        # Should NOT have concat=n=0
        assert "concat=n=0" not in fc

    def test_sfx_only_no_voiceovers_multiple_sfx(self) -> None:
        """SFX-only mode: no voiceovers, multiple SFX → concat at volume."""
        args = build_audio_mix_command(
            voiceovers=[],
            sfx=["/tmp/sfx0.mp3", "/tmp/sfx1.mp3", "/tmp/sfx2.mp3"],
            output_path="/tmp/audio.mp3",
            sfx_volume=0.8,
        )
        for sfx in ["/tmp/sfx0.mp3", "/tmp/sfx1.mp3", "/tmp/sfx2.mp3"]:
            assert sfx in args
        fc_idx = args.index("-filter_complex")
        fc = args[fc_idx + 1]
        # Each SFX should be volume-adjusted
        assert fc.count("volume=0.8") == 3
        # Should concat all SFX
        assert "concat=n=3" in fc
        # Should NOT have amix
        assert "amix" not in fc

    def test_no_voiceovers_no_sfx_raises(self) -> None:
        """No audio at all should raise ValueError."""
        with pytest.raises(ValueError, match="No audio"):
            build_audio_mix_command(
                voiceovers=[],
                sfx=[],
                output_path="/tmp/audio.mp3",
            )


# ---------------------------------------------------------------------------
# _run_ffmpeg
# ---------------------------------------------------------------------------

class TestRunFFmpeg:
    async def test_success(self) -> None:
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))
        mock_proc.returncode = 0

        with patch("pipeline.long_video.stitcher.asyncio.create_subprocess_exec",
                    return_value=mock_proc) as mock_exec:
            await _run_ffmpeg(["-i", "test.mp4", "out.mp4"])
            mock_exec.assert_called_once()

    async def test_failure_raises_runtime_error(self) -> None:
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b"error details"))
        mock_proc.returncode = 1

        with patch("pipeline.long_video.stitcher.asyncio.create_subprocess_exec",
                    return_value=mock_proc):
            with pytest.raises(RuntimeError, match="FFmpeg failed"):
                await _run_ffmpeg(["-i", "bad.mp4"])


# ---------------------------------------------------------------------------
# stitch() orchestration
# ---------------------------------------------------------------------------

class TestStitch:
    async def test_returns_stitch_result(self) -> None:
        spec = _make_spec()

        with (
            patch("pipeline.long_video.stitcher._run_ffmpeg", new_callable=AsyncMock) as mock_ff,
            patch("pipeline.long_video.stitcher._probe_duration", return_value=12.5),
            patch("pipeline.long_video.stitcher.os.path.getsize", return_value=5_000_000),
            patch("pipeline.long_video.stitcher.tempfile.mkdtemp", return_value="/tmp/scribario-test"),
            patch("pipeline.long_video.stitcher.shutil.rmtree") as mock_rmtree,
        ):
            result = await stitch(spec)

        assert isinstance(result, StitchResult)
        assert result.output_path.endswith(".mp4")
        assert result.duration_seconds == 12.5
        assert result.file_size_bytes == 5_000_000

    async def test_calls_normalize_for_each_clip(self) -> None:
        spec = _make_spec()

        with (
            patch("pipeline.long_video.stitcher._run_ffmpeg", new_callable=AsyncMock) as mock_ff,
            patch("pipeline.long_video.stitcher._probe_duration", return_value=5.0),
            patch("pipeline.long_video.stitcher.os.path.getsize", return_value=1_000),
            patch("pipeline.long_video.stitcher.tempfile.mkdtemp", return_value="/tmp/scribario-test"),
            patch("pipeline.long_video.stitcher.shutil.rmtree"),
        ):
            await stitch(spec)

        # At least 3 normalize calls (one per clip)
        assert mock_ff.await_count >= 3

    async def test_temp_dir_cleaned_on_success(self) -> None:
        spec = _make_spec()

        with (
            patch("pipeline.long_video.stitcher._run_ffmpeg", new_callable=AsyncMock),
            patch("pipeline.long_video.stitcher._probe_duration", return_value=5.0),
            patch("pipeline.long_video.stitcher.os.path.getsize", return_value=1_000),
            patch("pipeline.long_video.stitcher.tempfile.mkdtemp", return_value="/tmp/scribario-test"),
            patch("pipeline.long_video.stitcher.shutil.rmtree") as mock_rmtree,
        ):
            await stitch(spec)

        mock_rmtree.assert_called_once_with("/tmp/scribario-test")

    async def test_temp_dir_cleaned_on_failure(self) -> None:
        spec = _make_spec()

        with (
            patch("pipeline.long_video.stitcher._run_ffmpeg", new_callable=AsyncMock,
                  side_effect=RuntimeError("FFmpeg failed")),
            patch("pipeline.long_video.stitcher.tempfile.mkdtemp", return_value="/tmp/scribario-test"),
            patch("pipeline.long_video.stitcher.shutil.rmtree") as mock_rmtree,
        ):
            with pytest.raises(RuntimeError):
                await stitch(spec)

        mock_rmtree.assert_called_once_with("/tmp/scribario-test")

    async def test_sfx_only_skips_audio_mix_uses_sfx_directly(self) -> None:
        """When voiceovers=[], stitch should build SFX-only audio (no crash)."""
        spec = _make_spec(scene_voiceovers=[], scene_sfx=["/tmp/sfx0.mp3", "/tmp/sfx1.mp3"])

        with (
            patch("pipeline.long_video.stitcher._run_ffmpeg", new_callable=AsyncMock) as mock_ff,
            patch("pipeline.long_video.stitcher._probe_duration", return_value=5.0),
            patch("pipeline.long_video.stitcher.os.path.getsize", return_value=1_000),
            patch("pipeline.long_video.stitcher.tempfile.mkdtemp", return_value="/tmp/scribario-test"),
            patch("pipeline.long_video.stitcher.shutil.rmtree"),
        ):
            result = await stitch(spec)

        assert isinstance(result, StitchResult)
        assert result.output_path.endswith(".mp4")

    async def test_output_dir_created(self) -> None:
        spec = _make_spec()

        with (
            patch("pipeline.long_video.stitcher._run_ffmpeg", new_callable=AsyncMock),
            patch("pipeline.long_video.stitcher._probe_duration", return_value=5.0),
            patch("pipeline.long_video.stitcher.os.path.getsize", return_value=1_000),
            patch("pipeline.long_video.stitcher.tempfile.mkdtemp", return_value="/tmp/scribario-test"),
            patch("pipeline.long_video.stitcher.shutil.rmtree"),
            patch("pipeline.long_video.stitcher.os.makedirs") as mock_makedirs,
        ):
            result = await stitch(spec)

        # Should create output directory
        mock_makedirs.assert_called()
