"""Tests for long video pipeline data models."""

from __future__ import annotations

from pipeline.long_video.models import (
    LongVideoScript,
    Scene,
    SceneAssets,
    SceneType,
    StitchResult,
    StitchSpec,
    VideoProjectStatus,
)


class TestScene:
    def test_scene_has_required_fields(self) -> None:
        scene = Scene(
            index=0,
            scene_type=SceneType.A_ROLL,
            voiceover_text="In a world of bland condiments...",
            visual_description="Dark kitchen counter, sauce bottle",
            start_frame_prompt="Dark kitchen, bottle, spotlight",
            end_frame_prompt="Close-up bottle label, warm light",
            camera_direction="slow dolly push-in",
            sfx_description="dramatic whoosh",
        )
        assert scene.index == 0
        assert scene.scene_type == SceneType.A_ROLL
        assert scene.voiceover_text == "In a world of bland condiments..."

    def test_scene_type_enum_values(self) -> None:
        assert SceneType.A_ROLL == "a_roll"
        assert SceneType.B_ROLL == "b_roll"
        assert SceneType.TRANSITION == "transition"


class TestLongVideoScript:
    def test_script_has_scenes(self) -> None:
        scene = Scene(
            index=0,
            scene_type=SceneType.A_ROLL,
            voiceover_text="Test voiceover",
            visual_description="Test visual",
            start_frame_prompt="Start frame",
            end_frame_prompt="End frame",
            camera_direction="push-in",
            sfx_description="whoosh",
        )
        script = LongVideoScript(
            title="Test Video",
            voice_style="confident male narrator",
            scenes=[scene],
        )
        assert script.title == "Test Video"
        assert len(script.scenes) == 1
        assert script.scenes[0].index == 0

    def test_script_total_scenes(self) -> None:
        scenes = [
            Scene(
                index=i,
                scene_type=SceneType.A_ROLL,
                voiceover_text=f"Scene {i}",
                visual_description=f"Visual {i}",
                start_frame_prompt=f"Start {i}",
                end_frame_prompt=f"End {i}",
                camera_direction="push-in",
                sfx_description="whoosh",
            )
            for i in range(4)
        ]
        script = LongVideoScript(
            title="4 Scene Video",
            voice_style="narrator",
            scenes=scenes,
        )
        assert script.total_scenes == 4


class TestSceneAssets:
    def test_scene_assets_defaults_to_none(self) -> None:
        assets = SceneAssets(scene_index=0)
        assert assets.voiceover_url is None
        assert assets.voiceover_duration_seconds is None
        assert assets.start_frame_url is None
        assert assets.end_frame_url is None
        assert assets.video_clip_url is None
        assert assets.sfx_url is None
        assert assets.cost_usd == 0.0

    def test_scene_assets_with_values(self) -> None:
        assets = SceneAssets(
            scene_index=0,
            voiceover_url="https://example.com/vo.mp3",
            voiceover_duration_seconds=7.5,
            start_frame_url="https://example.com/start.jpg",
            end_frame_url="https://example.com/end.jpg",
            video_clip_url="https://example.com/clip.mp4",
            sfx_url="https://example.com/sfx.mp3",
            cost_usd=0.86,
        )
        assert assets.voiceover_duration_seconds == 7.5
        assert assets.cost_usd == 0.86


class TestStitchSpec:
    def test_stitch_spec_defaults(self) -> None:
        spec = StitchSpec(
            project_id="test-id",
            scene_clips=["clip1.mp4", "clip2.mp4"],
            scene_voiceovers=["vo1.mp3", "vo2.mp3"],
        )
        assert spec.aspect_ratio == "16:9"
        assert spec.transition_duration == 0.5
        assert spec.sfx_volume == 0.3
        assert spec.scene_sfx == []

    def test_stitch_spec_custom_values(self) -> None:
        spec = StitchSpec(
            project_id="test-id",
            scene_clips=["clip1.mp4"],
            scene_voiceovers=["vo1.mp3"],
            aspect_ratio="9:16",
            transition_duration=1.0,
            sfx_volume=0.5,
            scene_sfx=["sfx1.mp3"],
        )
        assert spec.aspect_ratio == "9:16"
        assert spec.transition_duration == 1.0


class TestStitchResult:
    def test_stitch_result(self) -> None:
        result = StitchResult(
            output_path="/tmp/scribario/test/final.mp4",
            duration_seconds=30.5,
            file_size_bytes=15_000_000,
        )
        assert result.output_path == "/tmp/scribario/test/final.mp4"
        assert result.duration_seconds == 30.5
        assert result.file_size_bytes == 15_000_000


class TestVideoProjectStatus:
    def test_status_values(self) -> None:
        assert VideoProjectStatus.SCRIPTING == "scripting"
        assert VideoProjectStatus.TTS == "tts"
        assert VideoProjectStatus.GENERATING_FRAMES == "generating_frames"
        assert VideoProjectStatus.GENERATING_CLIPS == "generating_clips"
        assert VideoProjectStatus.STITCHING == "stitching"
        assert VideoProjectStatus.PREVIEW_READY == "preview_ready"
        assert VideoProjectStatus.APPROVED == "approved"
        assert VideoProjectStatus.FAILED == "failed"
