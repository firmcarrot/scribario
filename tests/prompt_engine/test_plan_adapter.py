"""Tests for the GenerationPlan → LongVideoScript adapter."""

from __future__ import annotations

import pytest

from pipeline.long_video.models import LongVideoScript, SceneType
from pipeline.prompt_engine.models import (
    AnimationPrompt,
    ContentFormat,
    FramePrompt,
    GenerationPlan,
    ScenePlan,
    VeoMode,
)
from pipeline.prompt_engine.plan_adapter import plan_to_script


def _make_video_plan(num_scenes: int = 4) -> GenerationPlan:
    return GenerationPlan(
        content_format=ContentFormat.LONG_VIDEO,
        title="Sauce Ad",
        concept_summary="30-second sauce commercial",
        scenes=[
            ScenePlan(
                index=i,
                scene_type="a_roll" if i % 2 == 0 else "b_roll",
                duration_seconds=7.5,
                start_frame=FramePrompt(f"Scene {i} start frame cinematic", "16:9", []),
                end_frame=FramePrompt(f"Scene {i} end frame cinematic", "16:9", []),
                animation=AnimationPrompt(f"Scene {i} camera movement", VeoMode.FIRST_AND_LAST_FRAMES),
                voiceover_text=f"Narration for scene {i}",
                sfx_description=f"SFX for scene {i}",
                camera_direction="slow push in",
            )
            for i in range(num_scenes)
        ],
        captions=[{"text": "Watch this"}],
        voice_style="warm_narrator",
    )


class TestPlanToScript:
    def test_converts_to_long_video_script(self) -> None:
        plan = _make_video_plan()
        script = plan_to_script(plan)

        assert isinstance(script, LongVideoScript)
        assert script.title == "Sauce Ad"
        assert script.voice_style == "warm_narrator"
        assert script.total_scenes == 4

    def test_scene_fields_mapped(self) -> None:
        plan = _make_video_plan()
        script = plan_to_script(plan)

        scene = script.scenes[0]
        assert scene.index == 0
        assert scene.scene_type == SceneType.A_ROLL
        assert scene.voiceover_text == "Narration for scene 0"
        assert scene.start_frame_prompt == "Scene 0 start frame cinematic"
        assert scene.end_frame_prompt == "Scene 0 end frame cinematic"
        assert scene.camera_direction == "slow push in"
        assert scene.sfx_description == "SFX for scene 0"

    def test_visual_description_from_animation(self) -> None:
        plan = _make_video_plan()
        script = plan_to_script(plan)

        scene = script.scenes[0]
        assert scene.visual_description == "Scene 0 camera movement"

    def test_scene_type_mapping(self) -> None:
        plan = _make_video_plan()
        script = plan_to_script(plan)

        assert script.scenes[0].scene_type == SceneType.A_ROLL
        assert script.scenes[1].scene_type == SceneType.B_ROLL

    def test_unknown_scene_type_defaults_to_b_roll(self) -> None:
        plan = _make_video_plan(num_scenes=1)
        plan.scenes[0].scene_type = "product_hero"
        script = plan_to_script(plan)

        assert script.scenes[0].scene_type == SceneType.B_ROLL

    def test_default_voice_style(self) -> None:
        plan = _make_video_plan()
        plan.voice_style = None
        script = plan_to_script(plan)

        assert script.voice_style == "professional narrator"
