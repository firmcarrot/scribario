"""FFmpeg stitcher — normalize, transition, audio mix, output."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path

from pipeline.long_video.models import StitchResult, StitchSpec

logger = logging.getLogger(__name__)


def _resolution(aspect_ratio: str) -> tuple[int, int]:
    """Get target resolution for aspect ratio."""
    if aspect_ratio == "9:16":
        return 1080, 1920
    return 1920, 1080


def build_normalize_command(
    input_path: str,
    output_path: str,
    aspect_ratio: str,
) -> list[str]:
    """Build ffmpeg args to normalize a clip to target resolution + 30fps.

    Strips audio (-an) since audio is handled separately.
    """
    w, h = _resolution(aspect_ratio)
    vf = (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
        f"fps=30"
    )
    return ["-y", "-i", input_path, "-vf", vf, "-an", output_path]


def build_xfade_command(
    clips: list[str],
    durations: list[float],
    output_path: str,
    transition_duration: float = 0.5,
) -> list[str]:
    """Build ffmpeg args to concatenate clips with xfade transitions.

    For a single clip, just copies the input. For N clips, chains N-1
    xfade filters with cumulative offsets.
    """
    if len(clips) == 1:
        return ["-y", "-i", clips[0], "-c", "copy", output_path]

    # Build inputs
    args: list[str] = ["-y"]
    for clip in clips:
        args.extend(["-i", clip])

    # Build filter_complex with chained xfade
    filters: list[str] = []
    # Track cumulative offset: each transition eats `transition_duration` from total
    offset = round(durations[0] - transition_duration, 3)

    # First xfade: [0:v][1:v]
    filters.append(
        f"[0:v][1:v]xfade=transition=fade:duration={transition_duration}:offset={offset}[v01]"
    )

    for i in range(2, len(clips)):
        if i == 2:
            prev = "v01"
        else:
            prev = f"xf{i - 1}"
        out_label = f"xf{i}" if i < len(clips) - 1 else "vout"
        offset = round(offset + durations[i - 1] - transition_duration, 3)
        filters.append(
            f"[{prev}][{i}:v]xfade=transition=fade"
            f":duration={transition_duration}:offset={offset}[{out_label}]"
        )

    fc = ";".join(filters)

    # Fix: for 2 clips, output label is v01; for 3+, last label
    if len(clips) == 2:
        out_label = "v01"
    else:
        out_label = "vout"

    args.extend(["-filter_complex", fc, "-map", f"[{out_label}]", output_path])
    return args


def build_audio_mix_command(
    voiceovers: list[str],
    sfx: list[str],
    output_path: str,
    sfx_volume: float = 0.3,
) -> list[str]:
    """Build ffmpeg args to mix voiceover + sfx audio tracks.

    Supports three modes:
    1. Voiceovers only (no SFX) — concat voiceovers
    2. SFX only (no voiceovers) — volume-adjust and concat SFX
    3. Both — concat voiceovers as base, mix with volume-adjusted SFX via amix
    """
    if not voiceovers and not sfx:
        raise ValueError("No audio inputs: both voiceovers and sfx are empty")

    args: list[str] = ["-y"]

    # SFX-only mode: no voiceovers
    if not voiceovers:
        for inp in sfx:
            args.extend(["-i", inp])

        if len(sfx) == 1:
            # Single SFX: just volume-adjust
            fc = f"[0:a]volume={sfx_volume}[aout]"
            args.extend(["-filter_complex", fc, "-map", "[aout]", output_path])
        else:
            # Multiple SFX: volume-adjust each, then concat
            fc_parts: list[str] = []
            sfx_vol_labels = []
            for i in range(len(sfx)):
                label = f"sfx{i}"
                fc_parts.append(f"[{i}:a]volume={sfx_volume}[{label}]")
                sfx_vol_labels.append(f"[{label}]")
            sfx_concat = "".join(sfx_vol_labels)
            fc_parts.append(f"{sfx_concat}concat=n={len(sfx)}:v=0:a=1[aout]")
            fc = ";".join(fc_parts)
            args.extend(["-filter_complex", fc, "-map", "[aout]", output_path])
        return args

    # Add all inputs (voiceovers first, then SFX)
    all_inputs = voiceovers + sfx
    for inp in all_inputs:
        args.extend(["-i", inp])

    if not sfx:
        # Voiceovers only
        if len(voiceovers) == 1:
            args.extend(["-c", "copy", output_path])
        else:
            fc_parts = []
            for i in range(len(voiceovers)):
                fc_parts.append(f"[{i}:a]")
            fc = "".join(fc_parts) + f"concat=n={len(voiceovers)}:v=0:a=1[aout]"
            args.extend(["-filter_complex", fc, "-map", "[aout]", output_path])
    else:
        # Both voiceovers and SFX
        fc_parts: list[str] = []
        vo_count = len(voiceovers)
        sfx_count = len(sfx)

        # Concat voiceovers into one stream
        vo_labels = "".join(f"[{i}:a]" for i in range(vo_count))
        fc_parts.append(f"{vo_labels}concat=n={vo_count}:v=0:a=1[vo]")

        # Volume-adjust each SFX and concat them
        sfx_vol_labels = []
        for i, _ in enumerate(sfx):
            idx = vo_count + i
            label = f"sfx{i}"
            fc_parts.append(f"[{idx}:a]volume={sfx_volume}[{label}]")
            sfx_vol_labels.append(f"[{label}]")

        if sfx_count > 1:
            sfx_concat = "".join(sfx_vol_labels)
            fc_parts.append(f"{sfx_concat}concat=n={sfx_count}:v=0:a=1[sfxall]")
            sfx_final = "[sfxall]"
        else:
            sfx_final = sfx_vol_labels[0]

        # Mix voiceover + sfx
        fc_parts.append(f"[vo]{sfx_final}amix=inputs=2:duration=longest[aout]")

        fc = ";".join(fc_parts)
        args.extend(["-filter_complex", fc, "-map", "[aout]", output_path])

    return args


async def _run_ffmpeg(args: list[str]) -> None:
    """Run an ffmpeg command. Raises RuntimeError on failure."""
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed (rc={proc.returncode}): {stderr.decode()[-500:]}")


async def _probe_duration(path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    proc = await asyncio.create_subprocess_exec(
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {stderr.decode()[-500:]}")
    info = json.loads(stdout.decode())
    return float(info["format"]["duration"])


async def stitch(spec: StitchSpec) -> StitchResult:
    """Stitch scene clips with transitions and audio into final video.

    Steps:
    1. Normalize each clip to target resolution + 30fps
    2. Concatenate with xfade transitions
    3. Mix voiceover + SFX audio
    4. Mux video + audio into final MP4

    Output: /tmp/scribario/{project_id}/final.mp4
    """
    tmp_dir = tempfile.mkdtemp(prefix="scribario-stitch-")
    try:
        # 1. Normalize clips
        norm_clips: list[str] = []
        norm_durations: list[float] = []
        for i, clip in enumerate(spec.scene_clips):
            norm_path = os.path.join(tmp_dir, f"norm_{i}.mp4")
            cmd = build_normalize_command(clip, norm_path, spec.aspect_ratio)
            await _run_ffmpeg(cmd)
            norm_clips.append(norm_path)
            # Probe duration of normalized clip
            dur = await _probe_duration(norm_path)
            norm_durations.append(dur)

        # 2. xfade transitions
        xfade_path = os.path.join(tmp_dir, "xfade.mp4")
        xfade_cmd = build_xfade_command(
            norm_clips, norm_durations, xfade_path, spec.transition_duration,
        )
        await _run_ffmpeg(xfade_cmd)

        # 3. Audio mix (skip if no audio inputs at all)
        has_audio = bool(spec.scene_voiceovers or spec.scene_sfx)
        audio_path = os.path.join(tmp_dir, "audio.mp3")
        if has_audio:
            audio_cmd = build_audio_mix_command(
                spec.scene_voiceovers, spec.scene_sfx, audio_path, spec.sfx_volume,
            )
            await _run_ffmpeg(audio_cmd)

        # 4. Mux video + audio → final MP4
        output_dir = os.path.join("/tmp", "scribario", spec.project_id)
        os.makedirs(output_dir, exist_ok=True)
        final_path = os.path.join(output_dir, "final.mp4")

        if has_audio:
            mux_cmd = [
                "-y",
                "-i", xfade_path,
                "-i", audio_path,
                "-c:v", "libx264", "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-profile:v", "high",
                "-c:a", "aac", "-b:a", "128k",
                "-shortest",
                "-movflags", "+faststart",
                final_path,
            ]
        else:
            mux_cmd = [
                "-y",
                "-i", xfade_path,
                "-c:v", "libx264", "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-profile:v", "high",
                "-an",
                "-movflags", "+faststart",
                final_path,
            ]
        await _run_ffmpeg(mux_cmd)

        duration = await _probe_duration(final_path)
        file_size = os.path.getsize(final_path)

        return StitchResult(
            output_path=final_path,
            duration_seconds=duration,
            file_size_bytes=file_size,
        )
    finally:
        shutil.rmtree(tmp_dir)
