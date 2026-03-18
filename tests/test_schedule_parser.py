"""Tests for pipeline.schedule_parser — natural language → validated cron."""

from __future__ import annotations

import pytest

from pipeline.schedule_parser import parse_schedule


class TestParseSchedule:
    """Test schedule parsing from natural language to cron expressions."""

    def test_daily_at_time(self):
        cron, desc, err = parse_schedule("daily at 10am")
        assert err is None
        assert cron == "0 10 * * *"
        assert "daily" in desc.lower()

    def test_daily_at_time_pm(self):
        cron, desc, err = parse_schedule("daily at 3pm")
        assert err is None
        assert cron == "0 15 * * *"

    def test_daily_at_24h(self):
        cron, desc, err = parse_schedule("daily at 14:00")
        assert err is None
        assert cron == "0 14 * * *"

    def test_weekdays_at_time(self):
        cron, desc, err = parse_schedule("weekdays at 9am")
        assert err is None
        assert cron == "0 9 * * 1-5"
        assert "weekday" in desc.lower()

    def test_mon_wed_fri(self):
        cron, desc, err = parse_schedule("Mon/Wed/Fri at 10am")
        assert err is None
        assert cron == "0 10 * * 1,3,5"

    def test_mon_wed_fri_spaces(self):
        cron, desc, err = parse_schedule("Mon Wed Fri at 10am")
        assert err is None
        assert cron == "0 10 * * 1,3,5"

    def test_tue_thu(self):
        cron, desc, err = parse_schedule("Tue/Thu at 2pm")
        assert err is None
        assert cron == "0 14 * * 2,4"

    def test_3x_week(self):
        cron, desc, err = parse_schedule("3x/week at 10am")
        assert err is None
        assert cron == "0 10 * * 1,3,5"

    def test_every_other_day(self):
        cron, desc, err = parse_schedule("every other day at 8am")
        assert err is None
        assert cron == "0 8 */2 * *"

    def test_invalid_pattern_returns_error(self):
        cron, desc, err = parse_schedule("every full moon at midnight")
        assert err is not None
        assert cron is None

    def test_case_insensitive(self):
        cron, desc, err = parse_schedule("DAILY AT 10AM")
        assert err is None
        assert cron == "0 10 * * *"

    def test_timezone_conversion(self):
        """UTC conversion: 10am Eastern = 14:00 or 15:00 UTC depending on DST."""
        cron, desc, err = parse_schedule(
            "daily at 10am", timezone="America/New_York"
        )
        assert err is None
        # Should convert to UTC hour
        assert cron is not None
        parts = cron.split()
        utc_hour = int(parts[1])
        assert utc_hour in (14, 15)  # EDT=14, EST=15

    def test_empty_string_returns_error(self):
        cron, desc, err = parse_schedule("")
        assert err is not None
        assert cron is None

    def test_midnight(self):
        cron, desc, err = parse_schedule("daily at 12am")
        assert err is None
        assert cron == "0 0 * * *"

    def test_noon(self):
        cron, desc, err = parse_schedule("daily at 12pm")
        assert err is None
        assert cron == "0 12 * * *"
