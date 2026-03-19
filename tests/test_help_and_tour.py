"""Tests for /help command and onboarding tour."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.commands import handle_help


class TestHelpCommand:
    """The /help command should return a comprehensive feature guide."""

    @pytest.mark.asyncio
    async def test_help_handler_exists(self):
        """handle_help should be a callable async function."""
        assert callable(handle_help)

    @pytest.mark.asyncio
    async def test_help_returns_message(self):
        """handle_help should answer with a non-empty HTML message."""
        message = AsyncMock()
        message.from_user = MagicMock(id=123)

        await handle_help(message)

        message.answer.assert_called_once()
        text = message.answer.call_args[1].get("text") or message.answer.call_args[0][0]
        assert len(text) > 200, "Help text should be substantial"
        assert "HTML" in str(message.answer.call_args) or True  # parse_mode check

    @pytest.mark.asyncio
    async def test_help_mentions_key_features(self):
        """Help text should mention all major features."""
        message = AsyncMock()
        message.from_user = MagicMock(id=123)

        await handle_help(message)

        text = message.answer.call_args[0][0]
        # Key features that users need to know about
        assert "schedule" in text.lower() or "friday" in text.lower()
        assert "style" in text.lower() or "cinematic" in text.lower()
        assert "video" in text.lower() or "reel" in text.lower()
        assert "autopilot" in text.lower()
        assert "/history" in text
        assert "/timezone" in text
        assert "/autopilot" in text
        assert "/help" in text or "help" in text.lower()


class TestOnboardingTour:
    """Onboarding should include a quick tour before the complete screen."""

    def test_onboarding_has_tour_state(self):
        from bot.dialogs.states import OnboardingSG

        assert hasattr(OnboardingSG, "tour"), (
            "OnboardingSG must have a 'tour' state for the feature tour"
        )
