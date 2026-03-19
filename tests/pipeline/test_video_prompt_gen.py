"""Tests for pipeline.video_prompt_gen module."""

from __future__ import annotations

import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.brand_voice import BrandProfile
from pipeline.video_prompt_gen import VideoPromptResult


def _make_profile(**overrides) -> BrandProfile:
    """Create a test brand profile with sensible defaults."""
    defaults = {
        "tenant_id": "tenant-123",
        "name": "Mondo Shrimp",
        "tone_words": ["bold", "playful", "irreverent"],
        "audience_description": "Foodies and hot sauce enthusiasts",
        "do_list": ["Reference signature sauce", "Use humor"],
        "dont_list": ["Never mention competitors"],
    }
    defaults.update(overrides)
    return BrandProfile(**defaults)


def _mock_claude_response(text: str) -> MagicMock:
    """Build a mock Anthropic response with a single text block."""
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


# Forbidden terms that trigger gibberish text-in-video
FORBIDDEN_TERMS = [
    "text", "words", "writing", "sign", "letter",
    "subtitle", "caption", "title card", "logo text",
]


class TestGenerateVideoPrompt:
    """Core video prompt generation tests."""

    @pytest.mark.asyncio
    async def test_returns_non_empty_string(self):
        """generate_video_prompt returns a non-empty string."""
        prompt_text = (
            "Cinematic close-up of golden shrimp sizzling in a cast iron skillet. "
            "Slow dolly-in reveals steam rising through warm amber light. "
            "Shallow depth of field, 35mm film grain. "
            "Audio: sizzling oil, gentle kitchen ambiance."
        )
        mock_response = _mock_claude_response(prompt_text)

        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import generate_video_prompt

            result = await generate_video_prompt(
                intent="post about our weekend shrimp special",
                brand_profile=_make_profile(),
            )

        assert isinstance(result, VideoPromptResult)
        assert len(result.text) > 0

    @pytest.mark.asyncio
    async def test_prompt_includes_camera_terms(self):
        """Generated prompt should contain cinematographic direction."""
        prompt_text = (
            "Wide establishing shot of a seafood kitchen at golden hour. "
            "Slow dolly-in to an extreme close-up of shrimp in a sizzling skillet. "
            "Shallow depth of field, warm golden light, 35mm film texture. "
            "Audio: sizzling oil, gentle kitchen ambiance, soft upbeat music."
        )
        mock_response = _mock_claude_response(prompt_text)

        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import generate_video_prompt

            result = await generate_video_prompt(
                intent="shrimp cooking video",
                brand_profile=_make_profile(),
            )

        # Should contain at least one camera/cinematographic term
        camera_terms = [
            "close-up", "dolly", "pan", "tracking", "crane",
            "establishing", "push-in", "pull-back", "orbit", "reveal",
            "wide", "medium shot", "low angle", "high angle",
        ]
        found = any(term in result.text.lower() for term in camera_terms)
        assert found, f"No camera terms found in: {result.text}"

    @pytest.mark.asyncio
    async def test_brand_name_incorporated(self):
        """Brand name should appear in the system or user prompt sent to Claude."""
        prompt_text = (
            "Cinematic close-up of Mondo Shrimp signature sauce being drizzled. "
            "Slow dolly forward, warm golden lighting. "
            "Audio: sizzling, ambient kitchen sounds."
        )
        mock_response = _mock_claude_response(prompt_text)

        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import generate_video_prompt

            await generate_video_prompt(
                intent="showcase our sauce",
                brand_profile=_make_profile(),
            )

        # Verify the brand name was included in the user message
        call_kwargs = mock_client.messages.create.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        user_content = messages[0]["content"]
        assert "Mondo Shrimp" in user_content

    @pytest.mark.asyncio
    async def test_visual_prompt_passed_to_claude(self):
        """When visual_prompt is provided, it should be included in the user message."""
        prompt_text = (
            "Slow push-in on golden fried shrimp platter. "
            "Warm lighting, shallow depth of field. "
            "Audio: gentle sizzle, ambient restaurant."
        )
        mock_response = _mock_claude_response(prompt_text)

        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import generate_video_prompt

            await generate_video_prompt(
                intent="shrimp platter video",
                brand_profile=_make_profile(),
                visual_prompt="Golden fried shrimp on a white plate with garnish",
            )

        call_kwargs = mock_client.messages.create.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        user_content = messages[0]["content"]
        assert "Golden fried shrimp on a white plate with garnish" in user_content

    @pytest.mark.asyncio
    async def test_without_visual_prompt(self):
        """Should work fine without a visual_prompt."""
        prompt_text = (
            "Tracking shot of a lively outdoor seafood market. "
            "Cinematic color grading, natural light. "
            "Audio: crowd chatter, sizzling grills."
        )
        mock_response = _mock_claude_response(prompt_text)

        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import generate_video_prompt

            result = await generate_video_prompt(
                intent="show our food truck vibe",
                brand_profile=_make_profile(),
                visual_prompt=None,
            )

        assert len(result.text) > 0

    @pytest.mark.asyncio
    async def test_aspect_ratio_passed_to_claude(self):
        """Aspect ratio should be included in the user message for composition guidance."""
        prompt_text = (
            "Vertical close-up of sauce being poured. "
            "Low angle, dramatic lighting. "
            "Audio: thick pour, sizzle."
        )
        mock_response = _mock_claude_response(prompt_text)

        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import generate_video_prompt

            await generate_video_prompt(
                intent="sauce pour video",
                brand_profile=_make_profile(),
                aspect_ratio="9:16",
            )

        call_kwargs = mock_client.messages.create.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        user_content = messages[0]["content"]
        assert "9:16" in user_content

    @pytest.mark.asyncio
    async def test_reference_image_flag_in_message(self):
        """reference_has_image flag should affect the user message."""
        prompt_text = (
            "Slow orbit around a product on a clean surface. "
            "Soft lighting, professional cinematography. "
            "Audio: minimal ambient hum."
        )
        mock_response = _mock_claude_response(prompt_text)

        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import generate_video_prompt

            await generate_video_prompt(
                intent="product showcase",
                brand_profile=_make_profile(),
                reference_has_image=True,
            )

        call_kwargs = mock_client.messages.create.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        user_content = messages[0]["content"]
        assert "reference image" in user_content.lower()

    @pytest.mark.asyncio
    async def test_claude_api_failure_fallback(self):
        """On Claude API failure, falls back to raw visual_prompt or intent."""
        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(
                side_effect=Exception("API rate limited")
            )
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import generate_video_prompt

            result = await generate_video_prompt(
                intent="shrimp special",
                brand_profile=_make_profile(),
                visual_prompt="golden shrimp on a plate",
            )

        # Should fall back to visual_prompt
        assert isinstance(result, VideoPromptResult)
        assert result.text == "golden shrimp on a plate"
        assert result.input_tokens is None

    @pytest.mark.asyncio
    async def test_claude_api_failure_fallback_to_intent(self):
        """On failure with no visual_prompt, falls back to intent."""
        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(
                side_effect=Exception("API down")
            )
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import generate_video_prompt

            result = await generate_video_prompt(
                intent="shrimp special",
                brand_profile=_make_profile(),
                visual_prompt=None,
            )

        assert isinstance(result, VideoPromptResult)
        assert result.text == "shrimp special"


class TestPostProcessing:
    """Tests for forbidden-term stripping in post-processing."""

    @pytest.mark.asyncio
    async def test_strips_text_in_scene_instructions(self):
        """Post-processing should strip forbidden text-in-scene terms."""
        # Claude might hallucinate "with text overlay saying..." despite instructions
        prompt_with_text = (
            "Close-up of shrimp sizzling with text overlay saying 'Hot Deal'. "
            "Warm lighting, cinematic. Audio: sizzle, music."
        )
        mock_response = _mock_claude_response(prompt_with_text)

        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import sanitize_video_prompt

            result = sanitize_video_prompt(prompt_with_text)

        # Should have stripped the text overlay clause
        assert "text overlay" not in result.lower()

    def test_sanitize_removes_forbidden_phrases(self):
        """sanitize_video_prompt strips sentences with forbidden terms."""
        from pipeline.video_prompt_gen import sanitize_video_prompt

        dirty = (
            "Close-up of shrimp. "
            "A sign reads 'Weekend Special'. "
            "Warm golden lighting."
        )
        result = sanitize_video_prompt(dirty)
        assert "sign reads" not in result.lower()
        assert "close-up" in result.lower()
        assert "warm golden" in result.lower()

    def test_sanitize_preserves_clean_prompt(self):
        """Clean prompts pass through unchanged."""
        from pipeline.video_prompt_gen import sanitize_video_prompt

        clean = (
            "Slow dolly-in on sizzling shrimp in a cast iron skillet. "
            "Warm amber light, shallow depth of field. "
            "Audio: sizzling oil, soft music."
        )
        result = sanitize_video_prompt(clean)
        assert result == clean

    def test_sanitize_handles_empty_string(self):
        from pipeline.video_prompt_gen import sanitize_video_prompt

        assert sanitize_video_prompt("") == ""

    def test_sanitize_all_sentences_stripped_returns_empty(self):
        """If every sentence has forbidden terms, sanitizer returns empty."""
        from pipeline.video_prompt_gen import sanitize_video_prompt

        all_forbidden = (
            "A sign reads 'Weekend Special'. "
            "Text overlay showing the price. "
            "Subtitle announcing the deal."
        )
        result = sanitize_video_prompt(all_forbidden)
        assert result == ""

    @pytest.mark.asyncio
    async def test_all_sentences_stripped_falls_back_to_raw(self):
        """When sanitizer strips everything, generate_video_prompt returns raw Claude output."""
        all_forbidden = (
            "A sign reads 'Weekend Special'. "
            "Text overlay showing the price."
        )
        mock_response = _mock_claude_response(all_forbidden)

        with patch("pipeline.video_prompt_gen.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic.AsyncAnthropic.return_value = mock_client

            from pipeline.video_prompt_gen import generate_video_prompt

            result = await generate_video_prompt(
                intent="weekend special",
                brand_profile=_make_profile(),
            )

        # Should fall back to raw (unsanitized) Claude output
        assert result.text == all_forbidden.strip()


class TestSystemPrompt:
    """Verify the system prompt encodes critical Veo 3.1 knowledge."""

    def test_system_prompt_has_camera_vocabulary(self):
        from pipeline.video_prompt_gen import VIDEO_PROMPT_SYSTEM

        prompt = VIDEO_PROMPT_SYSTEM.lower()
        assert "dolly" in prompt or "tracking" in prompt
        assert "close-up" in prompt or "closeup" in prompt

    def test_system_prompt_has_audio_guidance(self):
        from pipeline.video_prompt_gen import VIDEO_PROMPT_SYSTEM

        assert "audio" in VIDEO_PROMPT_SYSTEM.lower()

    def test_system_prompt_has_anti_patterns(self):
        from pipeline.video_prompt_gen import VIDEO_PROMPT_SYSTEM

        prompt = VIDEO_PROMPT_SYSTEM.lower()
        # Must warn against text/signs in scene
        assert "text" in prompt
        assert "sign" in prompt or "gibberish" in prompt

    def test_system_prompt_has_word_count_guidance(self):
        from pipeline.video_prompt_gen import VIDEO_PROMPT_SYSTEM

        prompt = VIDEO_PROMPT_SYSTEM.lower()
        assert "100" in prompt or "150" in prompt or "word" in prompt
