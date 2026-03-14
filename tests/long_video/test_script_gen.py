"""Tests for long video script generation via Claude API."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.brand_voice import BrandProfile
from pipeline.long_video.models import LongVideoScript, SceneType


def _make_profile(**overrides) -> BrandProfile:
    defaults = {
        "tenant_id": "test-tenant",
        "name": "Mondo Shrimp",
        "tone_words": ["bold", "fun", "spicy"],
        "audience_description": "Hot sauce enthusiasts aged 25-45",
        "do_list": ["Use fire emojis", "Mention heat levels"],
        "dont_list": ["Never say mild", "No health claims"],
        "product_catalog": {"sauces": ["Ghost Pepper", "Habanero"]},
        "compliance_notes": "",
    }
    defaults.update(overrides)
    return BrandProfile(**defaults)


VALID_SCRIPT_JSON = {
    "title": "The Most Interesting Sauce in the World",
    "voice_style": "confident male narrator, warm baritone, conversational",
    "scenes": [
        {
            "index": 0,
            "scene_type": "a_roll",
            "voiceover_text": "In a world of bland condiments, one sauce dares to be different.",
            "visual_description": "Dark kitchen counter, single hot sauce bottle, dramatic spotlight",
            "start_frame_prompt": "Dark kitchen counter, single hot sauce bottle, dramatic spotlight, cinematic",
            "end_frame_prompt": "Same counter, extreme close-up of sauce bottle label, warm golden light",
            "camera_direction": "slow dolly push-in",
            "sfx_description": "subtle dramatic whoosh, low bass rumble",
        },
        {
            "index": 1,
            "scene_type": "b_roll",
            "voiceover_text": "Crafted from the finest peppers, aged to perfection.",
            "visual_description": "Fresh peppers being sliced on cutting board",
            "start_frame_prompt": "Overhead shot of fresh red peppers on wooden cutting board",
            "end_frame_prompt": "Close-up of pepper slices with steam rising",
            "camera_direction": "overhead crane down",
            "sfx_description": "crisp knife chop sound",
        },
        {
            "index": 2,
            "scene_type": "a_roll",
            "voiceover_text": "One taste, and you'll never go back to ordinary.",
            "visual_description": "Person tasting sauce, eyes widening",
            "start_frame_prompt": "Medium shot of person holding sauce bottle, neutral expression",
            "end_frame_prompt": "Same person, eyes wide with delight, warm lighting",
            "camera_direction": "slow zoom in on face",
            "sfx_description": "satisfying sizzle sound",
        },
        {
            "index": 3,
            "scene_type": "b_roll",
            "voiceover_text": "Stay hungry, my friends.",
            "visual_description": "Bottle on table with brand logo",
            "start_frame_prompt": "Sauce bottle centered on dark table, soft backlight",
            "end_frame_prompt": "Same bottle with logo and tagline super, golden glow",
            "camera_direction": "slow pull back reveal",
            "sfx_description": "deep bass stinger, subtle reverb tail",
        },
    ],
}


def _mock_claude_response(content: str) -> SimpleNamespace:
    """Create a mock Claude API response."""
    block = SimpleNamespace(type="text", text=content)
    return SimpleNamespace(content=[block])


class TestGenerateScriptCallsClaude:
    """Test that generate_script calls Claude with correct system prompt."""

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_calls_claude_with_system_prompt(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import SCRIPT_SYSTEM_PROMPT, generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _mock_claude_response(
            json.dumps(VALID_SCRIPT_JSON)
        )

        await generate_script("Promo for our new sauce", _make_profile())

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["system"] == SCRIPT_SYSTEM_PROMPT
        assert call_kwargs["model"] == "claude-sonnet-4-20250514"
        assert call_kwargs["max_tokens"] == 2000

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_user_message_includes_intent_and_brand(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _mock_claude_response(
            json.dumps(VALID_SCRIPT_JSON)
        )

        profile = _make_profile(name="Mondo Shrimp")
        await generate_script("Promo for our new sauce", profile)

        call_kwargs = mock_client.messages.create.call_args.kwargs
        user_msg = call_kwargs["messages"][0]["content"]
        assert "Promo for our new sauce" in user_msg
        assert "Mondo Shrimp" in user_msg

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_system_prompt_has_key_instructions(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import SCRIPT_SYSTEM_PROMPT

        assert "4 scenes" in SCRIPT_SYSTEM_PROMPT
        assert "30-second" in SCRIPT_SYSTEM_PROMPT.lower() or "30 second" in SCRIPT_SYSTEM_PROMPT.lower()
        assert "a_roll" in SCRIPT_SYSTEM_PROMPT or "A-roll" in SCRIPT_SYSTEM_PROMPT
        assert "JSON" in SCRIPT_SYSTEM_PROMPT
        assert "camera_direction" in SCRIPT_SYSTEM_PROMPT


class TestParseScriptResponse:
    """Test JSON response parsing into LongVideoScript."""

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_parses_valid_json_into_script(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _mock_claude_response(
            json.dumps(VALID_SCRIPT_JSON)
        )

        result = await generate_script("Test intent", _make_profile())

        assert isinstance(result, LongVideoScript)
        assert result.title == "The Most Interesting Sauce in the World"
        assert result.voice_style == "confident male narrator, warm baritone, conversational"

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_parses_scenes_with_correct_types(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _mock_claude_response(
            json.dumps(VALID_SCRIPT_JSON)
        )

        result = await generate_script("Test intent", _make_profile())

        assert result.scenes[0].scene_type == SceneType.A_ROLL
        assert result.scenes[1].scene_type == SceneType.B_ROLL
        assert result.scenes[0].camera_direction == "slow dolly push-in"
        assert result.scenes[0].sfx_description == "subtle dramatic whoosh, low bass rumble"


class TestFourScenesFor30s:
    """Test script generates 4 scenes for a 30-second video."""

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_returns_4_scenes(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _mock_claude_response(
            json.dumps(VALID_SCRIPT_JSON)
        )

        result = await generate_script("Test intent", _make_profile())

        assert result.total_scenes == 4
        assert [s.index for s in result.scenes] == [0, 1, 2, 3]

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_alternates_a_roll_b_roll(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _mock_claude_response(
            json.dumps(VALID_SCRIPT_JSON)
        )

        result = await generate_script("Test intent", _make_profile())

        types = [s.scene_type for s in result.scenes]
        assert types == [SceneType.A_ROLL, SceneType.B_ROLL, SceneType.A_ROLL, SceneType.B_ROLL]


class TestJsonParsingErrors:
    """Test error handling for malformed Claude responses."""

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_malformed_json_raises(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _mock_claude_response(
            "This is not JSON at all!"
        )

        with pytest.raises(json.JSONDecodeError):
            await generate_script("Test intent", _make_profile())

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_missing_scenes_key_raises(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _mock_claude_response(
            json.dumps({"title": "Test", "voice_style": "narrator"})
        )

        with pytest.raises(KeyError):
            await generate_script("Test intent", _make_profile())

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_strips_markdown_fences(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        wrapped = f"```json\n{json.dumps(VALID_SCRIPT_JSON)}\n```"
        mock_client.messages.create.return_value = _mock_claude_response(wrapped)

        result = await generate_script("Test intent", _make_profile())

        assert isinstance(result, LongVideoScript)
        assert result.total_scenes == 4


class TestVisualPromptSuffix:
    """Test that visual prompts get 'No music, no sound effects, no dialogue.' appended."""

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_appends_no_audio_suffix_to_start_frame(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _mock_claude_response(
            json.dumps(VALID_SCRIPT_JSON)
        )

        result = await generate_script("Test intent", _make_profile())

        for scene in result.scenes:
            assert scene.start_frame_prompt.endswith(
                "No music, no sound effects, no dialogue."
            ), f"Scene {scene.index} start_frame_prompt missing suffix"

    @patch("pipeline.long_video.script_gen.anthropic")
    @patch("pipeline.long_video.script_gen.get_settings")
    async def test_appends_no_audio_suffix_to_end_frame(
        self, mock_settings: MagicMock, mock_anthropic: MagicMock
    ) -> None:
        from pipeline.long_video.script_gen import generate_script

        mock_settings.return_value.anthropic_api_key = "test-key"
        mock_client = AsyncMock()
        mock_anthropic.AsyncAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _mock_claude_response(
            json.dumps(VALID_SCRIPT_JSON)
        )

        result = await generate_script("Test intent", _make_profile())

        for scene in result.scenes:
            assert scene.end_frame_prompt.endswith(
                "No music, no sound effects, no dialogue."
            ), f"Scene {scene.index} end_frame_prompt missing suffix"


class TestCostConstant:
    """Test the cost constant is defined correctly."""

    def test_cost_constant_value(self) -> None:
        from pipeline.long_video.script_gen import SCRIPT_GEN_COST_USD

        assert SCRIPT_GEN_COST_USD == 0.03
