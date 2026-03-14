"""Data models for the Prompt Engine — GenerationPlan and supporting types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

MAX_REF_IMAGES_PER_SCENE = 14


class ContentFormat(StrEnum):
    IMAGE_POST = "image_post"
    SHORT_VIDEO = "short_video"
    LONG_VIDEO = "long_video"


class VeoMode(StrEnum):
    TEXT_2_VIDEO = "TEXT_2_VIDEO"
    FIRST_AND_LAST_FRAMES = "FIRST_AND_LAST_FRAMES_2_VIDEO"
    REFERENCE_2_VIDEO = "REFERENCE_2_VIDEO"


class RefSlotType(StrEnum):
    OBJECT_FIDELITY = "object_fidelity"
    CHARACTER_CONSISTENCY = "character_consistency"


@dataclass
class RefImageAssignment:
    asset_url: str
    slot_type: RefSlotType

    @staticmethod
    def flat_urls(refs: list[RefImageAssignment]) -> list[str]:
        """Collapse to flat URL list for Kie.ai image_input param."""
        return [r.asset_url for r in refs]


@dataclass
class FramePrompt:
    prompt: str
    aspect_ratio: str
    reference_images: list[RefImageAssignment]


@dataclass
class AnimationPrompt:
    prompt: str
    veo_mode: VeoMode
    aspect_ratio: str = "16:9"


@dataclass
class CompositeInstruction:
    logo_overlay: bool = False
    logo_position: str = "bottom_right"
    logo_opacity: float = 0.7
    text_overlay: str | None = None
    text_position: str = "bottom_center"


@dataclass
class ScenePlan:
    index: int
    scene_type: str
    duration_seconds: float
    start_frame: FramePrompt
    end_frame: FramePrompt | None = None
    animation: AnimationPrompt | None = None
    voiceover_text: str | None = None
    sfx_description: str | None = None
    camera_direction: str | None = None
    composite: CompositeInstruction = field(default_factory=CompositeInstruction)
    character_seed_scene: bool = False


# Scene count limits per content format.
_SCENE_LIMITS: dict[ContentFormat, tuple[int, int]] = {
    ContentFormat.IMAGE_POST: (1, 3),
    ContentFormat.SHORT_VIDEO: (1, 1),
    ContentFormat.LONG_VIDEO: (2, 6),
}


@dataclass
class GenerationPlan:
    content_format: ContentFormat
    title: str
    concept_summary: str
    scenes: list[ScenePlan]
    captions: list[dict]
    voice_style: str | None = None
    aspect_ratio: str = "16:9"
    transition_style: str = "fade"

    def validate(self) -> list[str]:
        """Return a list of validation errors (empty = valid)."""
        errors: list[str] = []

        # Captions check
        if not self.captions:
            errors.append("At least one caption is required")

        # Caption formula diversity check — each caption should use a different formula
        if len(self.captions) >= 3:
            formulas = {c.get("formula") for c in self.captions if isinstance(c, dict)}
            formulas.discard(None)
            if len(formulas) < 3:
                errors.append("Caption formulas must be diverse — each of the 3 captions must use a different formula")

        # Scene count check
        lo, hi = _SCENE_LIMITS.get(self.content_format, (1, 6))
        if not (lo <= len(self.scenes) <= hi):
            errors.append(
                f"Scene count {len(self.scenes)} out of range [{lo}, {hi}] "
                f"for {self.content_format}"
            )

        is_video = self.content_format in (ContentFormat.SHORT_VIDEO, ContentFormat.LONG_VIDEO)

        for scene in self.scenes:
            # Video scenes require voiceover + animation
            if is_video:
                if not scene.voiceover_text:
                    errors.append(f"Scene {scene.index}: voiceover_text required for video")
                if not scene.animation:
                    errors.append(f"Scene {scene.index}: animation required for video")

            # Reference image cap per scene (across start + end frames)
            total_refs = len(scene.start_frame.reference_images)
            if scene.end_frame:
                total_refs += len(scene.end_frame.reference_images)
            if total_refs > MAX_REF_IMAGES_PER_SCENE:
                errors.append(
                    f"Scene {scene.index}: {total_refs} reference images exceeds "
                    f"max {MAX_REF_IMAGES_PER_SCENE}"
                )

        return errors
