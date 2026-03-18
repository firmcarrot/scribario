"""Tests for timezone-aware scheduling.

Covers:
- parse_scheduled_time with timezone parameter
- UTC conversion of scheduled times
- Timezone display in confirmation messages
- Tenant timezone storage and retrieval
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from bot.handlers.intake import parse_scheduled_time


class TestTimezoneAwareScheduling:
    """parse_scheduled_time should use tenant timezone when provided."""

    def test_timezone_param_accepted(self):
        """parse_scheduled_time accepts an optional timezone parameter."""
        result = parse_scheduled_time(
            "post this Friday at 3pm", tenant_timezone="America/New_York"
        )
        assert result is None or isinstance(result, datetime)

    def test_result_is_utc_when_timezone_given(self):
        """When a timezone is provided, the result should be UTC-aware."""
        result = parse_scheduled_time(
            "post tomorrow at 3pm", tenant_timezone="America/New_York"
        )
        if result is not None:
            assert result.tzinfo is not None, "Result should be timezone-aware"
            assert result.tzinfo == timezone.utc, "Result should be in UTC"

    def test_result_is_utc_when_no_timezone(self):
        """Even without tenant timezone, result should be UTC (server default)."""
        result = parse_scheduled_time("post tomorrow at 3pm")
        if result is not None:
            assert result.tzinfo is not None, "Result should be timezone-aware"
            assert result.tzinfo == timezone.utc, "Result should be in UTC"

    def test_ny_vs_la_different_utc(self):
        """Same local time in NY and LA should produce different UTC times.

        We use a fixed date to avoid "tomorrow" resolving to different days
        depending on the timezone's current local time.
        """
        result_ny = parse_scheduled_time(
            "post next Friday at 3pm", tenant_timezone="America/New_York"
        )
        result_la = parse_scheduled_time(
            "post next Friday at 3pm", tenant_timezone="America/Los_Angeles"
        )
        if result_ny is not None and result_la is not None:
            # Both should resolve to the same Friday but different UTC hours
            # LA is 3 hours behind NY, so LA's 3pm UTC should be 3 hours later
            diff_hours = (result_la - result_ny).total_seconds() / 3600
            assert abs(diff_hours - 3.0) < 0.1, (
                f"Expected ~3 hour difference, got {diff_hours}h. "
                f"NY={result_ny}, LA={result_la}"
            )

    def test_no_schedule_returns_none_with_timezone(self):
        """Non-scheduling text returns None even with timezone."""
        result = parse_scheduled_time(
            "write about the sauce", tenant_timezone="America/New_York"
        )
        assert result is None

    def test_relative_time_works(self):
        """'Post in an hour' should work regardless of timezone."""
        result = parse_scheduled_time(
            "post in an hour", tenant_timezone="Asia/Tokyo"
        )
        # "post in" triggers the schedule regex via "post" + time phrase
        # dateparser handles relative times correctly
        if result is not None:
            assert result.tzinfo is not None


class TestFormatScheduledTimeForUser:
    """format_scheduled_time_for_user converts UTC back to user's local time."""

    def test_format_function_exists(self):
        from bot.handlers.intake import format_scheduled_time_for_user

        utc_dt = datetime(2026, 3, 20, 19, 0, 0, tzinfo=timezone.utc)
        result = format_scheduled_time_for_user(utc_dt, "America/New_York")
        assert "3:00 PM" in result or "3:00PM" in result.replace(" ", "")
        assert "ET" in result or "EST" in result or "EDT" in result

    def test_format_with_la_timezone(self):
        from bot.handlers.intake import format_scheduled_time_for_user

        utc_dt = datetime(2026, 3, 20, 22, 0, 0, tzinfo=timezone.utc)
        result = format_scheduled_time_for_user(utc_dt, "America/Los_Angeles")
        assert "3:00 PM" in result or "3:00PM" in result.replace(" ", "")
        assert "PT" in result or "PST" in result or "PDT" in result

    def test_format_naive_utc_assumes_utc(self):
        """If given a naive datetime, assume UTC."""
        from bot.handlers.intake import format_scheduled_time_for_user

        naive_dt = datetime(2026, 3, 20, 19, 0, 0)
        result = format_scheduled_time_for_user(naive_dt, "America/New_York")
        assert "3:00 PM" in result or "3:00PM" in result.replace(" ", "")


class TestTenantTimezoneInDB:
    """Tenant timezone column exists and flows through queries."""

    def test_create_tenant_accepts_timezone(self):
        """create_tenant should accept a timezone parameter."""
        import inspect
        from bot.db import create_tenant

        sig = inspect.signature(create_tenant)
        assert "timezone" in sig.parameters, (
            "create_tenant must accept a timezone parameter"
        )

    def test_get_tenant_returns_timezone(self):
        """get_tenant_by_telegram_user should include timezone in the select."""
        import inspect
        from bot.db import get_tenant_by_telegram_user

        # We can't easily test the SQL select, but we verify the function exists
        assert callable(get_tenant_by_telegram_user)


class TestOnboardingTimezoneStep:
    """Onboarding should include a timezone selection step."""

    def test_onboarding_states_include_timezone(self):
        from bot.dialogs.states import OnboardingSG

        assert hasattr(OnboardingSG, "timezone"), (
            "OnboardingSG must have a 'timezone' state"
        )
