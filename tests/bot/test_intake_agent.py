"""Tests for intake agent integration in the bot intake handler."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.prompt_engine.intake import IntakeAction, IntakeResult


class TestIntakeAgentIntegration:
    """Test that handle_content_request calls check_intake before enqueueing."""

    def _make_message(self, text: str = "hero shot of our sauce") -> MagicMock:
        msg = MagicMock()
        msg.text = text
        msg.from_user = MagicMock()
        msg.from_user.id = 12345
        msg.chat = MagicMock()
        msg.chat.id = 99
        msg.answer = AsyncMock()
        return msg

    @pytest.mark.asyncio
    async def test_proceeds_when_intake_says_proceed(self) -> None:
        from bot.handlers.intake import handle_content_request

        msg = self._make_message()

        with (
            patch("bot.handlers.intake.get_tenant_by_telegram_user",
                  new_callable=AsyncMock,
                  return_value={"tenant_id": "t1", "onboarding_status": "complete"}),
            patch("bot.handlers.intake.check_intake",
                  new_callable=AsyncMock,
                  return_value=IntakeResult(action=IntakeAction.PROCEED)),
            patch("bot.handlers.intake.create_content_request",
                  new_callable=AsyncMock,
                  return_value={"id": "req-1"}),
            patch("bot.handlers.intake.enqueue_job",
                  new_callable=AsyncMock) as mock_enqueue,
            patch("bot.handlers.intake._pending_post_photos", {}),
        ):
            await handle_content_request(msg)

        # Should have enqueued a generation job
        mock_enqueue.assert_called_once()

    @pytest.mark.asyncio
    async def test_asks_for_asset_and_does_not_enqueue(self) -> None:
        from bot.handlers.intake import handle_content_request

        msg = self._make_message("put my widget on the moon")

        with (
            patch("bot.handlers.intake.get_tenant_by_telegram_user",
                  new_callable=AsyncMock,
                  return_value={"tenant_id": "t1", "onboarding_status": "complete"}),
            patch("bot.handlers.intake.check_intake",
                  new_callable=AsyncMock,
                  return_value=IntakeResult(
                      action=IntakeAction.ASK_FOR_ASSET,
                      message="Can you send me a photo of your widget?",
                  )),
            patch("bot.handlers.intake.create_content_request",
                  new_callable=AsyncMock) as mock_create,
            patch("bot.handlers.intake.enqueue_job",
                  new_callable=AsyncMock) as mock_enqueue,
            patch("bot.handlers.intake._pending_post_photos", {}),
        ):
            await handle_content_request(msg)

        # Should NOT have created a request or enqueued
        mock_create.assert_not_called()
        mock_enqueue.assert_not_called()

        # Should have sent the clarifying message
        msg.answer.assert_called()
        answer_text = msg.answer.call_args[0][0]
        assert "photo" in answer_text.lower() or "widget" in answer_text.lower()

    @pytest.mark.asyncio
    async def test_asks_for_clarity_and_does_not_enqueue(self) -> None:
        from bot.handlers.intake import handle_content_request

        msg = self._make_message("make something")

        with (
            patch("bot.handlers.intake.get_tenant_by_telegram_user",
                  new_callable=AsyncMock,
                  return_value={"tenant_id": "t1", "onboarding_status": "complete"}),
            patch("bot.handlers.intake.check_intake",
                  new_callable=AsyncMock,
                  return_value=IntakeResult(
                      action=IntakeAction.ASK_FOR_CLARITY,
                      message="What's this for? A product, event, or something else?",
                  )),
            patch("bot.handlers.intake.create_content_request",
                  new_callable=AsyncMock) as mock_create,
            patch("bot.handlers.intake.enqueue_job",
                  new_callable=AsyncMock) as mock_enqueue,
            patch("bot.handlers.intake._pending_post_photos", {}),
        ):
            await handle_content_request(msg)

        mock_create.assert_not_called()
        mock_enqueue.assert_not_called()
        msg.answer.assert_called()
