"""Tests for the intake agent module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.prompt_engine.intake import (
    INTAKE_COST_USD,
    IntakeAction,
    IntakeResult,
    check_intake,
)


TENANT_ID = "test-tenant-id"


class TestIntakeResult:
    def test_proceed(self) -> None:
        r = IntakeResult(action=IntakeAction.PROCEED)
        assert r.action == IntakeAction.PROCEED
        assert r.message is None

    def test_ask_for_asset(self) -> None:
        r = IntakeResult(
            action=IntakeAction.ASK_FOR_ASSET,
            message="Can you send a photo of your widget?",
        )
        assert r.action == IntakeAction.ASK_FOR_ASSET
        assert "photo" in r.message

    def test_ask_for_clarity(self) -> None:
        r = IntakeResult(
            action=IntakeAction.ASK_FOR_CLARITY,
            message="What's this for? A product, your business, an event?",
        )
        assert r.action == IntakeAction.ASK_FOR_CLARITY


class TestCheckIntake:
    def _mock_haiku_response(self, action: str, message: str | None = None) -> MagicMock:
        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.name = "intake_decision"
        tool_block.input = {"action": action}
        if message:
            tool_block.input["message"] = message

        response = MagicMock()
        response.content = [tool_block]
        response.stop_reason = "tool_use"
        return response

    @pytest.mark.asyncio
    async def test_proceed_when_has_assets(self) -> None:
        """If tenant has photos and intent is clear, proceed."""
        mock_response = self._mock_haiku_response("proceed")
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("pipeline.prompt_engine.intake.anthropic.AsyncAnthropic",
                  return_value=mock_client),
            patch("pipeline.prompt_engine.intake.get_settings") as ms,
            patch("pipeline.prompt_engine.intake.count_reference_photos",
                  new_callable=AsyncMock, return_value=3),
        ):
            ms.return_value.anthropic_api_key = "k"
            result = await check_intake("hero shot of our sauce", TENANT_ID)

        assert result.action == IntakeAction.PROCEED

    @pytest.mark.asyncio
    async def test_ask_for_asset(self) -> None:
        """If intent references product but no photos exist, ask."""
        mock_response = self._mock_haiku_response(
            "ask_for_asset", "Can you send me a photo of your widget?"
        )
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("pipeline.prompt_engine.intake.anthropic.AsyncAnthropic",
                  return_value=mock_client),
            patch("pipeline.prompt_engine.intake.get_settings") as ms,
            patch("pipeline.prompt_engine.intake.count_reference_photos",
                  new_callable=AsyncMock, return_value=0),
        ):
            ms.return_value.anthropic_api_key = "k"
            result = await check_intake("put my widget on the moon", TENANT_ID)

        assert result.action == IntakeAction.ASK_FOR_ASSET
        assert result.message is not None

    @pytest.mark.asyncio
    async def test_ask_for_clarity(self) -> None:
        """If intent is too vague, ask for clarity."""
        mock_response = self._mock_haiku_response(
            "ask_for_clarity", "What's this for? A product, event, or something else?"
        )
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with (
            patch("pipeline.prompt_engine.intake.anthropic.AsyncAnthropic",
                  return_value=mock_client),
            patch("pipeline.prompt_engine.intake.get_settings") as ms,
            patch("pipeline.prompt_engine.intake.count_reference_photos",
                  new_callable=AsyncMock, return_value=0),
        ):
            ms.return_value.anthropic_api_key = "k"
            result = await check_intake("make something", TENANT_ID)

        assert result.action == IntakeAction.ASK_FOR_CLARITY

    @pytest.mark.asyncio
    async def test_fallback_to_proceed_on_bad_response(self) -> None:
        """If Haiku returns nonsense, default to proceed (don't block the user)."""
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "I'm not sure what to do."
        response = MagicMock()
        response.content = [text_block]
        response.stop_reason = "end_turn"

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=response)

        with (
            patch("pipeline.prompt_engine.intake.anthropic.AsyncAnthropic",
                  return_value=mock_client),
            patch("pipeline.prompt_engine.intake.get_settings") as ms,
            patch("pipeline.prompt_engine.intake.count_reference_photos",
                  new_callable=AsyncMock, return_value=2),
        ):
            ms.return_value.anthropic_api_key = "k"
            result = await check_intake("some intent", TENANT_ID)

        assert result.action == IntakeAction.PROCEED

    @pytest.mark.asyncio
    async def test_cost_constant(self) -> None:
        assert INTAKE_COST_USD == 0.001
