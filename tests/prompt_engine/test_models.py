"""Tests for prompt engine data models."""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from pipeline.prompt_engine.models import (
    AnimationPrompt,
    CompositeInstruction,
    ContentFormat,
    FramePrompt,
    GenerationPlan,
    RefImageAssignment,
    RefSlotType,
    ScenePlan,
    VeoMode,
)


class TestEnums:
    def test_content_format_values(self) -> None:
        assert ContentFormat.IMAGE_POST == "image_post"
        assert ContentFormat.SHORT_VIDEO == "short_video"
        assert ContentFormat.LONG_VIDEO == "long_video"

    def test_content_format_no_carousel(self) -> None:
        """CAROUSEL was removed per DA review (YAGNI)."""
        assert not hasattr(ContentFormat, "CAROUSEL")

    def test_veo_mode_values(self) -> None:
        assert VeoMode.TEXT_2_VIDEO == "TEXT_2_VIDEO"
        assert VeoMode.FIRST_AND_LAST_FRAMES == "FIRST_AND_LAST_FRAMES_2_VIDEO"
        assert VeoMode.REFERENCE_2_VIDEO == "REFERENCE_2_VIDEO"

    def test_ref_slot_type_values(self) -> None:
        assert RefSlotType.OBJECT_FIDELITY == "object_fidelity"
        assert RefSlotType.CHARACTER_CONSISTENCY == "character_consistency"


class TestRefImageAssignment:
    def test_instantiation(self) -> None:
        ref = RefImageAssignment(
            asset_url="https://example.com/product.jpg",
            slot_type=RefSlotType.OBJECT_FIDELITY,
        )
        assert ref.asset_url == "https://example.com/product.jpg"
        assert ref.slot_type == RefSlotType.OBJECT_FIDELITY

    def test_flat_urls(self) -> None:
        refs = [
            RefImageAssignment("https://a.com/1.jpg", RefSlotType.OBJECT_FIDELITY),
            RefImageAssignment("https://a.com/2.jpg", RefSlotType.CHARACTER_CONSISTENCY),
            RefImageAssignment("https://a.com/3.jpg", RefSlotType.OBJECT_FIDELITY),
        ]
        urls = RefImageAssignment.flat_urls(refs)
        assert urls == ["https://a.com/1.jpg", "https://a.com/2.jpg", "https://a.com/3.jpg"]

    def test_flat_urls_empty(self) -> None:
        assert RefImageAssignment.flat_urls([]) == []


class TestFramePrompt:
    def test_instantiation(self) -> None:
        fp = FramePrompt(
            prompt="A bottle of hot sauce on a marble counter",
            aspect_ratio="16:9",
            reference_images=[
                RefImageAssignment("https://a.com/sauce.jpg", RefSlotType.OBJECT_FIDELITY),
            ],
        )
        assert fp.prompt == "A bottle of hot sauce on a marble counter"
        assert len(fp.reference_images) == 1

    def test_no_references(self) -> None:
        fp = FramePrompt(prompt="Abstract background", aspect_ratio="1:1", reference_images=[])
        assert fp.reference_images == []


class TestAnimationPrompt:
    def test_defaults(self) -> None:
        ap = AnimationPrompt(prompt="Camera slowly zooms in", veo_mode=VeoMode.TEXT_2_VIDEO)
        assert ap.aspect_ratio == "16:9"

    def test_custom_aspect(self) -> None:
        ap = AnimationPrompt(
            prompt="test", veo_mode=VeoMode.FIRST_AND_LAST_FRAMES, aspect_ratio="9:16"
        )
        assert ap.aspect_ratio == "9:16"


class TestCompositeInstruction:
    def test_defaults(self) -> None:
        ci = CompositeInstruction()
        assert ci.logo_overlay is False
        assert ci.logo_position == "bottom_right"
        assert ci.logo_opacity == 0.7
        assert ci.text_overlay is None
        assert ci.text_position == "bottom_center"


class TestScenePlan:
    def test_image_post_scene(self) -> None:
        """IMAGE_POST scenes should only need start_frame."""
        scene = ScenePlan(
            index=0,
            scene_type="product_hero",
            duration_seconds=0,
            start_frame=FramePrompt("product shot", "1:1", []),
        )
        assert scene.end_frame is None
        assert scene.animation is None
        assert scene.voiceover_text is None
        assert scene.sfx_description is None
        assert scene.camera_direction is None
        assert scene.character_seed_scene is False

    def test_video_scene(self) -> None:
        scene = ScenePlan(
            index=0,
            scene_type="a_roll",
            duration_seconds=5.0,
            start_frame=FramePrompt("start", "16:9", []),
            end_frame=FramePrompt("end", "16:9", []),
            animation=AnimationPrompt("zoom in", VeoMode.FIRST_AND_LAST_FRAMES),
            voiceover_text="Welcome to Mondo Shrimp",
            sfx_description="Sizzling sound",
            camera_direction="slow push in",
        )
        assert scene.duration_seconds == 5.0
        assert scene.voiceover_text == "Welcome to Mondo Shrimp"

    def test_character_seed_scene(self) -> None:
        scene = ScenePlan(
            index=0,
            scene_type="ugc_person",
            duration_seconds=5.0,
            start_frame=FramePrompt("person holding product", "16:9", []),
            character_seed_scene=True,
        )
        assert scene.character_seed_scene is True


class TestGenerationPlan:
    def _make_image_plan(self) -> GenerationPlan:
        return GenerationPlan(
            content_format=ContentFormat.IMAGE_POST,
            title="Mondo Monday",
            concept_summary="Hero shot of signature sauce",
            scenes=[
                ScenePlan(
                    index=0,
                    scene_type="product_hero",
                    duration_seconds=0,
                    start_frame=FramePrompt("sauce bottle close-up", "1:1", []),
                ),
            ],
            captions=[{"text": "Stay Hungry, My Friends", "platform_variant": "instagram"}],
        )

    def _make_video_plan(self) -> GenerationPlan:
        return GenerationPlan(
            content_format=ContentFormat.LONG_VIDEO,
            title="Sauce Ad",
            concept_summary="30-second sauce commercial",
            scenes=[
                ScenePlan(
                    index=i,
                    scene_type="a_roll" if i % 2 == 0 else "b_roll",
                    duration_seconds=5.0,
                    start_frame=FramePrompt(f"scene {i} start", "16:9", []),
                    end_frame=FramePrompt(f"scene {i} end", "16:9", []),
                    animation=AnimationPrompt(f"scene {i}", VeoMode.FIRST_AND_LAST_FRAMES),
                    voiceover_text=f"Scene {i} narration",
                    sfx_description=f"Scene {i} sfx",
                    camera_direction="slow zoom",
                )
                for i in range(4)
            ],
            captions=[{"text": "Check it out", "platform_variant": "facebook"}],
            voice_style="warm_narrator",
            transition_style="dissolve",
        )

    def test_image_plan_instantiation(self) -> None:
        plan = self._make_image_plan()
        assert plan.content_format == ContentFormat.IMAGE_POST
        assert len(plan.scenes) == 1
        assert plan.voice_style is None

    def test_video_plan_instantiation(self) -> None:
        plan = self._make_video_plan()
        assert plan.content_format == ContentFormat.LONG_VIDEO
        assert len(plan.scenes) == 4
        assert plan.voice_style == "warm_narrator"

    def test_serialization_roundtrip(self) -> None:
        """asdict should produce JSON-serializable output."""
        plan = self._make_image_plan()
        d = asdict(plan)
        serialized = json.dumps(d)
        deserialized = json.loads(serialized)
        assert deserialized["title"] == "Mondo Monday"
        assert deserialized["content_format"] == "image_post"

    def test_defaults(self) -> None:
        plan = self._make_image_plan()
        assert plan.aspect_ratio == "16:9"
        assert plan.transition_style == "fade"

    def test_validate_image_post_valid(self) -> None:
        plan = self._make_image_plan()
        errors = plan.validate()
        assert errors == []

    def test_validate_image_post_too_many_scenes(self) -> None:
        plan = self._make_image_plan()
        plan.scenes = [
            ScenePlan(i, "hero", 0, FramePrompt("x", "1:1", []))
            for i in range(5)
        ]
        errors = plan.validate()
        assert any("scene" in e.lower() for e in errors)

    def test_validate_video_missing_voiceover(self) -> None:
        plan = self._make_video_plan()
        plan.scenes[0].voiceover_text = None
        errors = plan.validate()
        assert any("voiceover" in e.lower() for e in errors)

    def test_validate_video_missing_animation(self) -> None:
        plan = self._make_video_plan()
        plan.scenes[0].animation = None
        errors = plan.validate()
        assert any("animation" in e.lower() for e in errors)

    def test_validate_short_video_scene_count(self) -> None:
        plan = GenerationPlan(
            content_format=ContentFormat.SHORT_VIDEO,
            title="Quick clip",
            concept_summary="Single scene",
            scenes=[
                ScenePlan(0, "hero", 8.0, FramePrompt("x", "16:9", []),
                          animation=AnimationPrompt("x", VeoMode.TEXT_2_VIDEO),
                          voiceover_text="vo"),
                ScenePlan(1, "hero", 8.0, FramePrompt("x", "16:9", []),
                          animation=AnimationPrompt("x", VeoMode.TEXT_2_VIDEO),
                          voiceover_text="vo"),
            ],
            captions=[{"text": "caption"}],
        )
        errors = plan.validate()
        assert any("scene" in e.lower() for e in errors)

    def test_validate_formula_diversity_requires_three(self) -> None:
        """3 captions must each use a different formula."""
        plan = self._make_image_plan()
        plan.captions = [
            {"text": "Caption one about sauce", "platform_variant": "instagram", "formula": "hook_story_offer"},
            {"text": "Caption two about sauce", "platform_variant": "instagram", "formula": "hook_story_offer"},
            {"text": "Caption three about sauce", "platform_variant": "instagram", "formula": "problem_agitate_solution"},
        ]
        errors = plan.validate()
        assert any("formula" in e.lower() for e in errors)

    def test_validate_formula_diversity_three_unique_passes(self) -> None:
        """3 captions with 3 different formulas should pass."""
        plan = self._make_image_plan()
        plan.captions = [
            {"text": "Caption one", "platform_variant": "ig", "formula": "hook_story_offer"},
            {"text": "Caption two", "platform_variant": "ig", "formula": "problem_agitate_solution"},
            {"text": "Caption three", "platform_variant": "ig", "formula": "punchy_one_liner"},
        ]
        errors = plan.validate()
        assert not any("formula" in e.lower() for e in errors)

    def test_validate_ref_image_cap(self) -> None:
        """More than 14 reference images per scene should fail validation."""
        refs = [
            RefImageAssignment(f"https://a.com/{i}.jpg", RefSlotType.OBJECT_FIDELITY)
            for i in range(15)
        ]
        plan = self._make_image_plan()
        plan.scenes[0].start_frame.reference_images = refs
        errors = plan.validate()
        assert any("14" in e or "reference" in e.lower() for e in errors)
