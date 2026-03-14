"""Adapter — converts GenerationPlan to LongVideoScript for the existing pipeline."""

from __future__ import annotations

from pipeline.long_video.models import LongVideoScript, Scene, SceneType
from pipeline.prompt_engine.models import GenerationPlan

# Map plan scene_type strings to LongVideoScript SceneType.
_SCENE_TYPE_MAP = {
    "a_roll": SceneType.A_ROLL,
    "b_roll": SceneType.B_ROLL,
    "transition": SceneType.TRANSITION,
}


def plan_to_script(plan: GenerationPlan) -> LongVideoScript:
    """Convert a GenerationPlan into a LongVideoScript.

    This allows the existing long-form pipeline (TTS → frames → clips → stitch)
    to consume plans from the Prompt Engine without rewriting.
    """
    scenes: list[Scene] = []
    for sp in plan.scenes:
        scene_type = _SCENE_TYPE_MAP.get(sp.scene_type, SceneType.B_ROLL)

        scenes.append(Scene(
            index=sp.index,
            scene_type=scene_type,
            voiceover_text=sp.voiceover_text or "",
            visual_description=sp.animation.prompt if sp.animation else sp.start_frame.prompt,
            start_frame_prompt=sp.start_frame.prompt,
            end_frame_prompt=sp.end_frame.prompt if sp.end_frame else sp.start_frame.prompt,
            camera_direction=sp.camera_direction or "smooth motion",
            sfx_description=sp.sfx_description or "ambient",
        ))

    return LongVideoScript(
        title=plan.title,
        voice_style=plan.voice_style or "professional narrator",
        scenes=scenes,
    )
