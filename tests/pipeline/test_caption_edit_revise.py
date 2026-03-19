"""Unit tests for revise_caption() — AI-assisted caption revision."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.brand_voice import BrandProfile, FewShotExample
from pipeline.caption_gen import RevisionResult


class TestReviseCaption:
    """revise_caption() calls Claude and returns the revised text."""

    def _make_profile(self) -> BrandProfile:
        return BrandProfile(
            tenant_id="tenant-123",
            name="Mondo Shrimp",
            tone_words=["bold", "playful"],
            audience_description="Hot sauce lovers",
            do_list=["Use humor", "Include CTA"],
            dont_list=["No generic content"],
        )

    def _make_examples(self) -> list[FewShotExample]:
        return [
            FewShotExample(
                platform="instagram",
                content_type="product",
                caption="This sauce is no joke. 🔥 #MondoShrimp",
            )
        ]

    @pytest.mark.asyncio
    async def test_revise_caption_returns_string(self):
        """revise_caption() returns a plain string (no JSON)."""
        from pipeline.caption_gen import revise_caption

        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Short and punchy! 🔥 #MondoShrimp")]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("pipeline.caption_gen.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await revise_caption(
                current_caption="Long winded caption that goes on and on. #MondoShrimp",
                instruction="make it shorter",
                profile=self._make_profile(),
                examples=self._make_examples(),
            )

        assert isinstance(result, RevisionResult)
        assert result.text == "Short and punchy! 🔥 #MondoShrimp"
        assert result.input_tokens is not None
        assert result.output_tokens is not None

    @pytest.mark.asyncio
    async def test_revise_caption_uses_haiku_model(self):
        """revise_caption() uses claude-haiku for cost efficiency."""
        from pipeline.caption_gen import revise_caption

        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Revised caption")]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("pipeline.caption_gen.anthropic.AsyncAnthropic", return_value=mock_client):
            await revise_caption(
                current_caption="Original caption",
                instruction="add emojis",
                profile=self._make_profile(),
                examples=self._make_examples(),
            )

        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-haiku-4-5-20251001"

    @pytest.mark.asyncio
    async def test_revise_caption_includes_instruction_in_user_message(self):
        """The instruction appears in the user message sent to Claude."""
        from pipeline.caption_gen import revise_caption

        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Punchy with emojis! 🔥")]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("pipeline.caption_gen.anthropic.AsyncAnthropic", return_value=mock_client):
            await revise_caption(
                current_caption="Original caption text",
                instruction="add 2 emojis",
                profile=self._make_profile(),
                examples=self._make_examples(),
            )

        call_kwargs = mock_client.messages.create.call_args[1]
        messages = call_kwargs["messages"]
        user_content = messages[0]["content"]
        assert "add 2 emojis" in user_content
        assert "Original caption text" in user_content

    @pytest.mark.asyncio
    async def test_revise_caption_strips_whitespace(self):
        """Leading/trailing whitespace is stripped from the result."""
        from pipeline.caption_gen import revise_caption

        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="  Trimmed result \n")]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("pipeline.caption_gen.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await revise_caption(
                current_caption="Some caption",
                instruction="fix it",
                profile=self._make_profile(),
                examples=[],
            )

        assert result.text == "Trimmed result"

    @pytest.mark.asyncio
    async def test_revise_caption_propagates_api_error(self):
        """API errors are not swallowed — they propagate to caller."""
        import anthropic as anthropic_lib

        from pipeline.caption_gen import revise_caption

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            side_effect=anthropic_lib.APIError(
                message="Rate limit", request=MagicMock(), body=None
            )
        )

        with patch("pipeline.caption_gen.anthropic.AsyncAnthropic", return_value=mock_client):
            with pytest.raises(anthropic_lib.APIError):
                await revise_caption(
                    current_caption="Caption",
                    instruction="shorten it",
                    profile=self._make_profile(),
                    examples=[],
                )
