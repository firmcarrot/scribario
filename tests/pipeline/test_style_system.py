"""Tests for the style system (Feature 4)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.intake import parse_style_override
from pipeline.brand_voice import BrandProfile
from pipeline.caption_gen import CaptionResult, generate_captions


class TestParseStyleOverride:
    def test_cinematic_detected(self):
        assert parse_style_override("make it cinematic") == "cinematic"

    def test_dramatic_maps_to_cinematic(self):
        assert parse_style_override("I want a dramatic feel") == "cinematic"

    def test_cartoon_detected(self):
        assert parse_style_override("make it cartoon style") == "cartoon"

    def test_illustrated_maps_to_cartoon(self):
        assert parse_style_override("illustrated version please") == "cartoon"

    def test_animated_maps_to_cartoon(self):
        assert parse_style_override("make it animated") == "cartoon"

    def test_watercolor_detected(self):
        assert parse_style_override("watercolor look") == "watercolor"

    def test_painted_maps_to_watercolor(self):
        assert parse_style_override("painted style") == "watercolor"

    def test_photorealistic_detected(self):
        assert parse_style_override("photorealistic please") == "photorealistic"

    def test_realistic_maps_to_photorealistic(self):
        assert parse_style_override("make it realistic") == "photorealistic"

    def test_no_style_returns_none(self):
        assert parse_style_override("write about our hot sauce") is None

    def test_case_insensitive(self):
        assert parse_style_override("CINEMATIC style") == "cinematic"
        assert parse_style_override("Cartoon please") == "cartoon"


class TestStyleInjectionInVisualPrompt:
    """Test that style prefix is injected into visual prompts in generate_captions."""

    def _mock_claude_response(self):
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                type="text",
                text='{"captions": [{"text": "Hot sauce caption", "visual_prompt": "beautiful food"}]}',
            )
        ]
        mock_response.usage = MagicMock(input_tokens=100, output_tokens=50)
        return mock_response

    @pytest.mark.asyncio
    async def test_style_injected_into_visual_prompt(self):
        """When style='cinematic', visual prompts should start with [STYLE: cinematic]."""
        profile = BrandProfile(
            tenant_id="t1",
            name="Mondo Shrimp",
            tone_words=["bold"],
            audience_description="Hot sauce fans",
            do_list=[],
            dont_list=[],
        )

        with patch("pipeline.caption_gen.anthropic.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(return_value=self._mock_claude_response())

            response = await generate_captions(
                intent="our new sauce",
                profile=profile,
                examples=[],
                platform_targets=["instagram"],
                num_options=1,
                style="cinematic",
            )

        assert len(response.results) == 1
        assert response.results[0].visual_prompt == "[STYLE: cinematic] beautiful food"

    @pytest.mark.asyncio
    async def test_no_style_leaves_visual_prompt_unchanged(self):
        """When style=None, visual prompts should not be modified."""
        profile = BrandProfile(
            tenant_id="t1",
            name="Mondo Shrimp",
            tone_words=["bold"],
            audience_description="Hot sauce fans",
            do_list=[],
            dont_list=[],
        )

        with patch("pipeline.caption_gen.anthropic.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(return_value=self._mock_claude_response())

            response = await generate_captions(
                intent="our new sauce",
                profile=profile,
                examples=[],
                platform_targets=["instagram"],
                num_options=1,
                style=None,
            )

        assert len(response.results) == 1
        assert response.results[0].visual_prompt == "beautiful food"


class TestStyleFallbackToBrandDefault:
    """Test that brand default_image_style is used when no style_override on the job."""

    def test_brand_profile_has_default_image_style(self):
        profile = BrandProfile(
            tenant_id="t1",
            name="Test Brand",
            tone_words=[],
            audience_description="",
            do_list=[],
            dont_list=[],
        )
        assert profile.default_image_style == "photorealistic"

    def test_brand_profile_custom_default_style(self):
        profile = BrandProfile(
            tenant_id="t1",
            name="Test Brand",
            tone_words=[],
            audience_description="",
            do_list=[],
            dont_list=[],
            default_image_style="cinematic",
        )
        assert profile.default_image_style == "cinematic"

    def test_style_override_takes_priority_over_brand_default(self):
        """style_override from job should win over brand's default_image_style."""
        profile = BrandProfile(
            tenant_id="t1",
            name="Test Brand",
            tone_words=[],
            audience_description="",
            do_list=[],
            dont_list=[],
            default_image_style="photorealistic",
        )
        # Simulate the worker logic: style_override OR brand default
        style_override = "cinematic"
        effective_style = style_override or profile.default_image_style
        assert effective_style == "cinematic"

    def test_falls_back_to_brand_default_when_no_override(self):
        profile = BrandProfile(
            tenant_id="t1",
            name="Test Brand",
            tone_words=[],
            audience_description="",
            do_list=[],
            dont_list=[],
            default_image_style="watercolor",
        )
        style_override = None
        effective_style = style_override or profile.default_image_style
        assert effective_style == "watercolor"
