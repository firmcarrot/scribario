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
        """handle_help should answer with a two-part HTML message."""
        message = AsyncMock()
        message.from_user = MagicMock(id=123)

        await handle_help(message)

        assert message.answer.call_count == 2, "Help is split into two messages"
        text = message.answer.call_args_list[0][0][0]
        assert len(text) > 200, "Help text should be substantial"

    @pytest.mark.asyncio
    async def test_help_mentions_key_features(self):
        """Help text should mention all major features across both parts."""
        message = AsyncMock()
        message.from_user = MagicMock(id=123)

        await handle_help(message)

        # Combine both message parts for feature checks
        all_text = " ".join(
            call[0][0] for call in message.answer.call_args_list
        )
        # Key features that users need to know about
        assert "schedule" in all_text.lower() or "friday" in all_text.lower()
        assert "style" in all_text.lower() or "cinematic" in all_text.lower()
        assert "video" in all_text.lower() or "reel" in all_text.lower()
        assert "autopilot" in all_text.lower()
        assert "/history" in all_text
        assert "/timezone" in all_text
        assert "/autopilot" in all_text
        assert "/help" in all_text or "help" in all_text.lower()
        # Billing features (new)
        assert "/subscribe" in all_text
        assert "/billing" in all_text
        assert "/topoff" in all_text
        assert "/usage" in all_text


class TestOnboardingTour:
    """Onboarding should include a quick tour before the complete screen."""

    def test_onboarding_has_tour_state(self):
        from bot.dialogs.states import OnboardingSG

        assert hasattr(OnboardingSG, "tour"), (
            "OnboardingSG must have a 'tour' state for the feature tour"
        )
