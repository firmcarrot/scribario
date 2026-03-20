"""Engagement data fetcher — polls Postiz analytics API for post metrics.

Uses: GET /api/analytics/post/{postizId}?date=30
Returns: AnalyticsData[] with labels "Impressions", "Reactions", "Clicks", etc.
Auth: Session cookie (same as posting).

Facebook is confirmed working. Other providers may return [] if they don't
implement postAnalytics (provider-specific). Returns None in that case.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from bot.config import get_settings

logger = logging.getLogger(__name__)

# Number of days to look back for analytics
ANALYTICS_LOOKBACK_DAYS = 30


@dataclass
class PostEngagement:
    """Engagement metrics for a single post."""

    likes: int  # Reactions from Postiz
    comments: int
    shares: int
    views: int  # Impressions from Postiz
    clicks: int = 0


async def fetch_post_engagement(
    postiz_id: str,
    base_url: str | None = None,
) -> PostEngagement | None:
    """Fetch engagement metrics for a post from Postiz analytics API.

    Uses GET /api/analytics/post/{postizId}?date=30 which returns
    AnalyticsData[] with labels like "Impressions", "Reactions", "Clicks".

    Args:
        postiz_id: The Postiz internal post ID (the 'i' field from post response).
        base_url: Override Postiz base URL (for testing).

    Returns:
        PostEngagement with metrics, or None if no data available.
    """
    settings = get_settings()
    url = (base_url or settings.postiz_url).rstrip("/")
    session_token = settings.postiz_session_token

    headers = {
        "Cookie": f"auth={session_token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{url}/api/analytics/post/{postiz_id}",
                params={"date": str(ANALYTICS_LOOKBACK_DAYS)},
                headers=headers,
            )
            if response.status_code in (404, 204):
                return None
            response.raise_for_status()

            text = response.text.strip()
            if not text:
                return None

            data = response.json()
    except httpx.HTTPStatusError:
        logger.warning(
            "Postiz analytics API error",
            extra={"postiz_id": postiz_id},
        )
        return None
    except httpx.RequestError:
        logger.warning(
            "Postiz connection error fetching analytics",
            extra={"postiz_id": postiz_id},
        )
        return None

    if not isinstance(data, list):
        # Postiz returns {"missing": true} if releaseId is missing
        if isinstance(data, dict) and data.get("missing"):
            return None
        return None

    if not data:
        # Empty array — provider doesn't implement postAnalytics
        return None

    # Parse AnalyticsData[] response
    # Each item: {"label": "Impressions", "data": [{"total": "342", "date": "..."}], ...}
    metrics = _parse_analytics_data(data)

    impressions = metrics.get("impressions", 0)
    reactions = metrics.get("reactions", 0)
    clicks = metrics.get("clicks", 0)

    # If everything is zero, no meaningful data yet
    if impressions == 0 and reactions == 0 and clicks == 0:
        return None

    return PostEngagement(
        likes=reactions,
        comments=0,  # Postiz doesn't break out comments vs reactions
        shares=0,    # Not available from Postiz analytics
        views=impressions,
        clicks=clicks,
    )


def _parse_analytics_data(data: list[dict]) -> dict[str, int]:
    """Parse Postiz AnalyticsData[] into a flat metrics dict.

    Each item has: {"label": "...", "data": [{"total": "N", "date": "..."}], ...}
    We sum all daily totals per label.
    """
    metrics: dict[str, int] = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        label = (item.get("label") or "").lower().strip()
        if not label:
            continue

        daily_data = item.get("data", [])
        if not isinstance(daily_data, list):
            continue

        total = 0
        for day in daily_data:
            if isinstance(day, dict):
                total += _int(day.get("total"))

        # Normalize label names
        if "impression" in label:
            metrics["impressions"] = metrics.get("impressions", 0) + total
        elif "reaction" in label:
            metrics["reactions"] = metrics.get("reactions", 0) + total
        elif label == "clicks":
            metrics["clicks"] = metrics.get("clicks", 0) + total
        # "Clicks by Type" is a sub-breakdown — skip to avoid double-counting

    return metrics


def _int(val: object) -> int:
    """Safe int conversion, default 0."""
    if val is None:
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0
