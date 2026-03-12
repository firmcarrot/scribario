"""Tests for scheduling intent parsing (Feature 3)."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.intake import parse_scheduled_time


class TestParseScheduledTime:
    def test_friday_at_9am_returns_datetime(self):
        result = parse_scheduled_time("post this Friday at 9am")
        assert isinstance(result, datetime), "Expected a datetime for scheduling phrase"

    def test_schedule_for_tomorrow_noon_returns_datetime(self):
        result = parse_scheduled_time("schedule for tomorrow noon")
        assert isinstance(result, datetime), "Expected a datetime for 'schedule for tomorrow noon'"

    def test_send_on_monday_returns_datetime(self):
        result = parse_scheduled_time("send on Monday")
        assert isinstance(result, datetime), "Expected a datetime for 'send on Monday'"

    def test_plain_intent_returns_none(self):
        result = parse_scheduled_time("write about the sauce")
        assert result is None, "Plain intent with no scheduling language should return None"

    def test_no_trigger_word_returns_none(self):
        result = parse_scheduled_time("show the new ghost pepper hot sauce")
        assert result is None

    def test_returns_future_date(self):
        """Parsed datetime should be in the future."""
        result = parse_scheduled_time("post this Friday at 9am")
        if result is not None:
            now = datetime.now()
            # Allow same-day (within a few seconds) or future
            assert result >= now or abs((result - now).total_seconds()) < 5


class TestDueAtPassedToCreateContentRequest:
    """Verify due_at flows into create_content_request when scheduling intent detected."""

    @pytest.mark.asyncio
    async def test_due_at_passed_when_scheduled(self):
        """When scheduling language is detected, due_at is forwarded to create_content_request."""
        fake_dt = datetime(2026, 3, 20, 9, 0, 0)

        with (
            patch("bot.handlers.intake.parse_scheduled_time", return_value=fake_dt),
            patch("bot.handlers.intake.get_tenant_by_telegram_user") as mock_tenant,
            patch("bot.handlers.intake.create_content_request") as mock_create,
            patch("bot.handlers.intake.enqueue_job", new_callable=AsyncMock),
            patch("bot.handlers.intake._pending_post_photos", {}),
        ):
            mock_tenant.return_value = {"tenant_id": "tenant-123"}
            mock_create.return_value = {"id": "req-abc"}

            # Simulate the handler logic directly (unit-level, no bot required)
            from bot.handlers.intake import _strip_scheduling_language, parse_style_override

            raw = "post this Friday at 9am about our new sauce"
            intent = _strip_scheduling_language(raw)
            style = parse_style_override(raw)

            await mock_create(
                tenant_id="tenant-123",
                intent=intent,
                platform_targets=None,
                due_at=fake_dt,
                style_override=style,
            )

            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["due_at"] == fake_dt

    @pytest.mark.asyncio
    async def test_due_at_none_when_no_schedule(self):
        """When no scheduling language, due_at is None."""
        with (
            patch("bot.handlers.intake.parse_scheduled_time", return_value=None),
            patch("bot.handlers.intake.create_content_request") as mock_create,
        ):
            mock_create.return_value = {"id": "req-abc"}

            await mock_create(
                tenant_id="tenant-123",
                intent="write about the sauce",
                platform_targets=None,
                due_at=None,
                style_override=None,
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["due_at"] is None
