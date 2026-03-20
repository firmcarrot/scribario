"""Tests for pipeline.engagement module — Postiz analytics engagement fetcher."""

from __future__ import annotations

import pytest

from pipeline.engagement import fetch_post_engagement, PostEngagement, _parse_analytics_data


class TestFetchPostEngagement:
    @pytest.mark.asyncio
    async def test_returns_engagement_from_analytics_endpoint(self, httpx_mock):
        """Confirmed Postiz analytics response shape from live data."""
        httpx_mock.add_response(
            url="http://test-postiz:5000/api/analytics/post/abc123",
            json=[
                {
                    "label": "Impressions",
                    "percentageChange": 0,
                    "data": [{"total": "342", "date": "2026-03-19"}],
                },
                {
                    "label": "Reactions",
                    "percentageChange": 0,
                    "data": [{"total": "7", "date": "2026-03-19"}],
                },
                {
                    "label": "Clicks",
                    "percentageChange": 0,
                    "data": [{"total": "18", "date": "2026-03-19"}],
                },
                {
                    "label": "Clicks by Type",
                    "percentageChange": 0,
                    "data": [{"total": "18", "date": "2026-03-19"}],
                },
            ],
        )

        result = await fetch_post_engagement(
            postiz_id="abc123",
            base_url="http://test-postiz:5000",
        )

        assert result is not None
        assert result.views == 342  # Impressions
        assert result.likes == 7  # Reactions
        assert result.clicks == 18
        assert result.comments == 0  # Not available from Postiz
        assert result.shares == 0  # Not available from Postiz

    @pytest.mark.asyncio
    async def test_sums_multi_day_totals(self, httpx_mock):
        """Analytics may return multiple days of data — sum them."""
        httpx_mock.add_response(
            url="http://test-postiz:5000/api/analytics/post/abc123",
            json=[
                {
                    "label": "Impressions",
                    "percentageChange": 0,
                    "data": [
                        {"total": "100", "date": "2026-03-18"},
                        {"total": "200", "date": "2026-03-19"},
                    ],
                },
                {
                    "label": "Reactions",
                    "percentageChange": 0,
                    "data": [
                        {"total": "3", "date": "2026-03-18"},
                        {"total": "5", "date": "2026-03-19"},
                    ],
                },
            ],
        )

        result = await fetch_post_engagement(
            postiz_id="abc123",
            base_url="http://test-postiz:5000",
        )

        assert result is not None
        assert result.views == 300  # 100 + 200
        assert result.likes == 8  # 3 + 5

    @pytest.mark.asyncio
    async def test_returns_none_on_empty_array(self, httpx_mock):
        """Provider doesn't implement postAnalytics → empty array."""
        httpx_mock.add_response(
            url="http://test-postiz:5000/api/analytics/post/abc123",
            json=[],
        )

        result = await fetch_post_engagement(
            postiz_id="abc123",
            base_url="http://test-postiz:5000",
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_missing_response(self, httpx_mock):
        """Postiz returns {"missing": true} when releaseId is gone."""
        httpx_mock.add_response(
            url="http://test-postiz:5000/api/analytics/post/abc123",
            json={"missing": True},
        )

        result = await fetch_post_engagement(
            postiz_id="abc123",
            base_url="http://test-postiz:5000",
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_404(self, httpx_mock):
        httpx_mock.add_response(
            url="http://test-postiz:5000/api/analytics/post/missing",
            status_code=404,
            json={"error": "Not found"},
        )

        result = await fetch_post_engagement(
            postiz_id="missing",
            base_url="http://test-postiz:5000",
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_server_error(self, httpx_mock):
        httpx_mock.add_response(
            url="http://test-postiz:5000/api/analytics/post/abc123",
            status_code=500,
            json={"error": "Internal error"},
        )

        result = await fetch_post_engagement(
            postiz_id="abc123",
            base_url="http://test-postiz:5000",
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_all_zeros(self, httpx_mock):
        """All-zero metrics means no real data yet."""
        httpx_mock.add_response(
            url="http://test-postiz:5000/api/analytics/post/abc123",
            json=[
                {
                    "label": "Impressions",
                    "percentageChange": 0,
                    "data": [{"total": "0", "date": "2026-03-19"}],
                },
                {
                    "label": "Reactions",
                    "percentageChange": 0,
                    "data": [{"total": "0", "date": "2026-03-19"}],
                },
                {
                    "label": "Clicks",
                    "percentageChange": 0,
                    "data": [{"total": "0", "date": "2026-03-19"}],
                },
            ],
        )

        result = await fetch_post_engagement(
            postiz_id="abc123",
            base_url="http://test-postiz:5000",
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_empty_body(self, httpx_mock):
        httpx_mock.add_response(
            url="http://test-postiz:5000/api/analytics/post/abc123",
            json=None,
            status_code=200,
        )

        result = await fetch_post_engagement(
            postiz_id="abc123",
            base_url="http://test-postiz:5000",
        )
        assert result is None


class TestParseAnalyticsData:
    def test_parses_standard_response(self):
        data = [
            {"label": "Impressions", "data": [{"total": "100", "date": "2026-03-19"}]},
            {"label": "Reactions", "data": [{"total": "5", "date": "2026-03-19"}]},
            {"label": "Clicks", "data": [{"total": "10", "date": "2026-03-19"}]},
        ]
        metrics = _parse_analytics_data(data)
        assert metrics["impressions"] == 100
        assert metrics["reactions"] == 5
        assert metrics["clicks"] == 10

    def test_skips_clicks_by_type(self):
        """'Clicks by Type' should not double-count with 'Clicks'."""
        data = [
            {"label": "Clicks", "data": [{"total": "10", "date": "2026-03-19"}]},
            {"label": "Clicks by Type", "data": [{"total": "10", "date": "2026-03-19"}]},
        ]
        metrics = _parse_analytics_data(data)
        assert metrics["clicks"] == 10  # Not 20

    def test_handles_empty_data_array(self):
        data = [
            {"label": "Impressions", "data": []},
        ]
        metrics = _parse_analytics_data(data)
        assert metrics.get("impressions", 0) == 0

    def test_handles_non_numeric_totals(self):
        data = [
            {"label": "Impressions", "data": [{"total": "not-a-number", "date": "2026-03-19"}]},
        ]
        metrics = _parse_analytics_data(data)
        assert metrics.get("impressions", 0) == 0

    def test_handles_missing_label(self):
        data = [{"data": [{"total": "100"}]}]
        metrics = _parse_analytics_data(data)
        assert metrics == {}


class TestPostEngagement:
    def test_dataclass_fields(self):
        e = PostEngagement(likes=10, comments=5, shares=2, views=1000, clicks=50)
        assert e.likes == 10
        assert e.comments == 5
        assert e.shares == 2
        assert e.views == 1000
        assert e.clicks == 50

    def test_clicks_default_zero(self):
        e = PostEngagement(likes=0, comments=0, shares=0, views=0)
        assert e.clicks == 0


@pytest.fixture
def httpx_mock(monkeypatch):
    """Simple httpx mock."""
    import httpx

    responses: list[dict] = []

    class MockTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request):
            for resp_config in responses:
                if resp_config["url"] in str(request.url):
                    return httpx.Response(
                        status_code=resp_config.get("status_code", 200),
                        json=resp_config.get("json"),
                        request=request,
                    )
            return httpx.Response(status_code=404, request=request)

    class MockHelper:
        def add_response(self, url: str, json: dict | list | None = None, status_code: int = 200):
            responses.append({"url": url, "json": json, "status_code": status_code})

    mock = MockHelper()
    original_init = httpx.AsyncClient.__init__

    def patched_init(self, *args, **kwargs):
        kwargs["transport"] = MockTransport()
        kwargs.pop("timeout", None)
        original_init(self, *args, timeout=60.0, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)
    return mock
