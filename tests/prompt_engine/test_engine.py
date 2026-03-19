"""Tests for the prompt engine core."""

from __future__ import annotations

import json
from dataclasses import asdict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.brand_voice import BrandProfile, FewShotExample
from pipeline.prompt_engine.asset_resolver import AssetManifest
from pipeline.prompt_engine.models import (
    ContentFormat,
    GenerationPlan,
    VeoMode,
)
from pipeline.prompt_engine.engine import (
    ENGINE_COST_USD,
    PlanResult,
    generate_plan,
    _parse_tool_response,
)


def _profile() -> BrandProfile:
    return BrandProfile(
        tenant_id="t1",
        name="Mondo Shrimp",
        tone_words=["bold", "playful"],
        audience_description="Foodies",
        do_list=["Use humor"],
        dont_list=["No cliches"],
    )


def _examples() -> list[FewShotExample]:
    return [
        FewShotExample(platform="instagram", content_type="product", caption="Stay Hungry"),
    ]


def _manifest() -> AssetManifest:
    return AssetManifest(
        product_photos=["https://a.com/sauce.jpg"],
        people_photos=[],
        other_photos=[],
    )


# A valid tool_use response payload that Claude would return.
_VALID_PLAN_DICT = {
    "content_format": "image_post",
    "title": "Mondo Monday",
    "concept_summary": "Hero shot of signature sauce",
    "scenes": [
        {
            "index": 0,
            "scene_type": "product_hero",
            "duration_seconds": 0,
            "start_frame": {
                "prompt": "A bottle of hot sauce on marble, golden hour light",
                "aspect_ratio": "1:1",
                "reference_images": [
                    {"asset_url": "https://a.com/sauce.jpg", "slot_type": "object_fidelity"},
                ],
            },
            "end_frame": None,
            "animation": None,
            "voiceover_text": None,
            "sfx_description": None,
            "camera_direction": None,
            "composite": {
                "logo_overlay": False,
                "logo_position": "bottom_right",
                "logo_opacity": 0.7,
                "text_overlay": None,
                "text_position": "bottom_center",
            },
            "character_seed_scene": False,
        },
    ],
    "captions": [
        {"text": "Stay Hungry, My Friends. #MondoShrimp", "platform_variant": "instagram", "formula": "hook_story_offer"},
        {"text": "The sauce speaks for itself. #MondoMonday", "platform_variant": "facebook", "formula": "punchy_one_liner"},
        {"text": "Heat seekers only. #MondoShrimp", "platform_variant": "instagram", "formula": "problem_agitate_solution"},
    ],
    "voice_style": None,
    "aspect_ratio": "16:9",
    "transition_style": "fade",
}

_VALID_VIDEO_PLAN_DICT = {
    "content_format": "long_video",
    "title": "Sauce Ad",
    "concept_summary": "30-second sauce commercial",
    "scenes": [
        {
            "index": i,
            "scene_type": "a_roll" if i % 2 == 0 else "b_roll",
            "duration_seconds": 7.5,
            "start_frame": {
                "prompt": f"Scene {i} start",
                "aspect_ratio": "16:9",
                "reference_images": [],
            },
            "end_frame": {
                "prompt": f"Scene {i} end",
                "aspect_ratio": "16:9",
                "reference_images": [],
            },
            "animation": {
                "prompt": f"Scene {i} animation",
                "veo_mode": "FIRST_AND_LAST_FRAMES_2_VIDEO",
                "aspect_ratio": "16:9",
            },
            "voiceover_text": f"Narration for scene {i}",
            "sfx_description": f"SFX for scene {i}",
            "camera_direction": "slow push in",
            "composite": {
                "logo_overlay": False,
                "logo_position": "bottom_right",
                "logo_opacity": 0.7,
                "text_overlay": None,
                "text_position": "bottom_center",
            },
            "character_seed_scene": False,
        }
        for i in range(4)
    ],
    "captions": [{"text": "Watch this", "platform_variant": "facebook"}],
    "voice_style": "warm_narrator",
    "aspect_ratio": "16:9",
    "transition_style": "dissolve",
}


def _mock_tool_response(plan_dict: dict) -> MagicMock:
    """Create a mock Anthropic response with tool_use block."""
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "create_generation_plan"
    tool_block.input = plan_dict

    response = MagicMock()
    response.content = [tool_block]
    response.stop_reason = "tool_use"
    return response


class TestParseToolResponse:
    def test_parses_image_plan(self) -> None:
        response = _mock_tool_response(_VALID_PLAN_DICT)
        plan = _parse_tool_response(response)
        assert isinstance(plan, GenerationPlan)
        assert plan.content_format == ContentFormat.IMAGE_POST
        assert plan.title == "Mondo Monday"
        assert len(plan.scenes) == 1
        assert len(plan.captions) == 3

    def test_parses_video_plan(self) -> None:
        response = _mock_tool_response(_VALID_VIDEO_PLAN_DICT)
        plan = _parse_tool_response(response)
        assert plan.content_format == ContentFormat.LONG_VIDEO
        assert len(plan.scenes) == 4
        assert plan.voice_style == "warm_narrator"
        assert plan.scenes[0].animation is not None
        assert plan.scenes[0].animation.veo_mode == VeoMode.FIRST_AND_LAST_FRAMES

    def test_parses_reference_images(self) -> None:
        response = _mock_tool_response(_VALID_PLAN_DICT)
        plan = _parse_tool_response(response)
        refs = plan.scenes[0].start_frame.reference_images
        assert len(refs) == 1
        assert refs[0].asset_url == "https://a.com/sauce.jpg"

    def test_raises_on_no_tool_use(self) -> None:
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Sorry, I can't do that."
        response = MagicMock()
        response.content = [text_block]
        response.stop_reason = "end_turn"
        with pytest.raises(ValueError, match="tool_use"):
            _parse_tool_response(response)

    def test_raises_on_validation_failure(self) -> None:
        bad_plan = dict(_VALID_VIDEO_PLAN_DICT)
        # Remove voiceover from a video scene — validation should fail
        bad_scenes = []
        for s in bad_plan["scenes"]:
            s_copy = dict(s)
            s_copy["voiceover_text"] = None
            bad_scenes.append(s_copy)
        bad_plan["scenes"] = bad_scenes

        response = _mock_tool_response(bad_plan)
        with pytest.raises(ValueError, match="voiceover"):
            _parse_tool_response(response)


class TestGeneratePlan:
    @pytest.mark.asyncio
    async def test_calls_claude_and_returns_plan(self) -> None:
        mock_response = _mock_tool_response(_VALID_PLAN_DICT)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("pipeline.prompt_engine.engine.anthropic.AsyncAnthropic",
                  return_value=mock_client),
            patch("pipeline.prompt_engine.engine.get_settings") as mock_settings,
        ):
            mock_settings.return_value.anthropic_api_key = "test-key"
            plan = await generate_plan(
                intent="hero shot of our sauce",
                profile=_profile(),
                examples=_examples(),
                assets=_manifest(),
                platform_targets=["instagram"],
            )

        assert isinstance(plan, PlanResult)
        assert isinstance(plan.plan, GenerationPlan)
        assert plan.plan.title == "Mondo Monday"
        assert plan.input_tokens is not None
        assert plan.output_tokens is not None

        # Verify tool_use was passed in the API call
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert "tools" in call_kwargs
        assert call_kwargs["tools"][0]["name"] == "create_generation_plan"

    @pytest.mark.asyncio
    async def test_cost_constant(self) -> None:
        assert ENGINE_COST_USD == 0.04
