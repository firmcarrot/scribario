"""Data models for the long-form video generation pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class SceneType(StrEnum):
    A_ROLL = "a_roll"
    B_ROLL = "b_roll"
    TRANSITION = "transition"


class VideoProjectStatus(StrEnum):
    SCRIPTING = "scripting"
    TTS = "tts"
    GENERATING_FRAMES = "generating_frames"
    GENERATING_CLIPS = "generating_clips"
    STITCHING = "stitching"
    PREVIEW_READY = "preview_ready"
    APPROVED = "approved"
    FAILED = "failed"


@dataclass
class Scene:
    """A single scene in a multi-scene video script."""

    index: int
    scene_type: SceneType
    voiceover_text: str
    visual_description: str
    start_frame_prompt: str
    end_frame_prompt: str
    camera_direction: str
    sfx_description: str


@dataclass
class LongVideoScript:
    """Claude-generated multi-scene video script."""

    title: str
    voice_style: str
    scenes: list[Scene]

    @property
    def total_scenes(self) -> int:
        return len(self.scenes)


@dataclass
class SceneAssets:
    """Generated assets for a single scene."""

    scene_index: int
    voiceover_url: str | None = None
    voiceover_duration_seconds: float | None = None
    start_frame_url: str | None = None
    end_frame_url: str | None = None
    video_clip_url: str | None = None
    sfx_url: str | None = None
    cost_usd: float = 0.0


@dataclass
class StitchSpec:
    """Specification for FFmpeg stitching."""

    project_id: str
    scene_clips: list[str]
    scene_voiceovers: list[str] = field(default_factory=list)
    aspect_ratio: str = "16:9"
    transition_duration: float = 0.5
    sfx_volume: float = 0.3
    scene_sfx: list[str] = field(default_factory=list)


@dataclass
class StitchResult:
    """Result from FFmpeg stitching."""

    output_path: str
    duration_seconds: float
    file_size_bytes: int
