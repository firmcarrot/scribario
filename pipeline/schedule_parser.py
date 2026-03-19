"""Schedule parser — natural language schedule text → validated cron expression.

Uses preset-based validation only (DA CRIT-1 fix): rejects anything that
doesn't match a known safe pattern. No arbitrary cron injection possible.
"""

from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

# Day name → cron day-of-week number
_DAY_MAP: dict[str, int] = {
    "mon": 1, "monday": 1,
    "tue": 2, "tuesday": 2,
    "wed": 3, "wednesday": 3,
    "thu": 4, "thursday": 4,
    "fri": 5, "friday": 5,
    "sat": 6, "saturday": 6,
    "sun": 0, "sunday": 0,
}


def _parse_time(time_str: str) -> int | None:
    """Parse a time string like '10am', '3pm', '14:00', '12am' into hour (0-23)."""
    time_str = time_str.strip().lower()

    # 12-hour format: "10am", "3pm", "12am", "12pm"
    m = re.match(r"^(\d{1,2})\s*(am|pm)$", time_str)
    if m:
        hour = int(m.group(1))
        period = m.group(2)
        if hour < 1 or hour > 12:
            return None
        if period == "am":
            return 0 if hour == 12 else hour
        else:
            return 12 if hour == 12 else hour + 12

    # 24-hour format: "14:00", "9:00"
    m = re.match(r"^(\d{1,2}):(\d{2})$", time_str)
    if m:
        hour = int(m.group(1))
        if 0 <= hour <= 23:
            return hour
        return None

    # Plain number
    m = re.match(r"^(\d{1,2})$", time_str)
    if m:
        hour = int(m.group(1))
        if 0 <= hour <= 23:
            return hour
        return None

    return None


def _convert_hour_to_utc(hour: int, timezone: str) -> int:
    """Convert a local hour to UTC hour for today's date."""
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    local_dt = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
    return utc_dt.hour


def _extract_time(text: str) -> tuple[str, int | None]:
    """Extract time from the end of a schedule string. Returns (remaining_text, hour)."""
    # Try "at <time>" pattern
    m = re.search(r"\bat\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*$", text, re.IGNORECASE)
    if m:
        hour = _parse_time(m.group(1))
        remaining = text[: m.start()].strip()
        return remaining, hour
    return text, None


def parse_schedule(
    text: str,
    timezone: str | None = None,
) -> tuple[str | None, str, str | None]:
    """Parse natural language schedule into a validated cron expression.

    Args:
        text: Natural language like "daily at 10am", "Mon/Wed/Fri at 10am"
        timezone: Optional IANA timezone to convert to UTC. If None, hour is used as-is.

    Returns:
        (cron_expr, description, error) — on success error is None,
        on failure cron_expr is None and error explains why.
    """
    if not text or not text.strip():
        return None, "", "Please provide a schedule like 'daily at 10am' or 'Mon/Wed/Fri at 10am'."

    text = text.strip()
    schedule_part, hour = _extract_time(text)
    schedule_lower = schedule_part.lower().strip()

    if hour is None:
        return None, "", "Could not parse the time. Use formats like '10am', '3pm', or '14:00'."

    # Convert to UTC if timezone provided
    display_hour = hour
    if timezone:
        hour = _convert_hour_to_utc(hour, timezone)

    # Match against known patterns
    cron: str | None = None
    desc: str = ""

    # "daily"
    if schedule_lower in ("daily", "every day", "everyday"):
        cron = f"0 {hour} * * *"
        desc = f"Daily at {_format_hour(display_hour)}"

    # "weekdays"
    elif schedule_lower in ("weekdays", "weekday", "every weekday"):
        cron = f"0 {hour} * * 1-5"
        desc = f"Weekdays at {_format_hour(display_hour)}"

    # Specific days: "Mon/Wed/Fri", "Mon Wed Fri", "Tue/Thu"
    elif _is_day_list(schedule_lower):
        days = _parse_day_list(schedule_lower)
        if days:
            day_str = ",".join(str(d) for d in sorted(days))
            day_names = _format_day_names(sorted(days))
            cron = f"0 {hour} * * {day_str}"
            desc = f"{day_names} at {_format_hour(display_hour)}"

    # "3x/week", "3x per week", "three times a week"
    elif re.match(r"^3x[/ ]*(per\s+)?week$", schedule_lower):
        cron = f"0 {hour} * * 1,3,5"
        desc = f"Mon/Wed/Fri at {_format_hour(display_hour)}"

    # "every other day"
    elif schedule_lower in ("every other day",):
        cron = f"0 {hour} */2 * *"
        desc = f"Every other day at {_format_hour(display_hour)}"

    if cron is None:
        return (
            None,
            "",
            f"Unrecognized schedule: '{text}'. Try: 'daily at 10am', "
            "'weekdays at 9am', 'Mon/Wed/Fri at 10am', or '3x/week at 10am'.",
        )

    return cron, desc, None


def _is_day_list(text: str) -> bool:
    """Check if text looks like a list of day names."""
    parts = re.split(r"[/,\s]+", text)
    return all(p.lower() in _DAY_MAP for p in parts if p)


def _parse_day_list(text: str) -> list[int]:
    """Parse a list of day names into cron day numbers."""
    parts = re.split(r"[/,\s]+", text)
    days = []
    for p in parts:
        p = p.lower().strip()
        if p in _DAY_MAP:
            days.append(_DAY_MAP[p])
    return days


def _format_hour(hour: int) -> str:
    """Format an hour as a human-readable time string."""
    if hour == 0:
        return "12:00 AM"
    elif hour < 12:
        return f"{hour}:00 AM"
    elif hour == 12:
        return "12:00 PM"
    else:
        return f"{hour - 12}:00 PM"


_DAY_NAMES = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}


def _format_day_names(days: list[int]) -> str:
    """Format day numbers as human-readable names."""
    return "/".join(_DAY_NAMES[d] for d in days)
