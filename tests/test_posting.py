"""Tests for pipeline.posting module."""

from __future__ import annotations

import httpx
import pytest

from pipeline.posting import PostizClient


class TestPostizClient:
    @pytest.mark.asyncio
    async def test_successful_post(self, httpx_mock):
        """Test successful multi-platform posting."""
        httpx_mock.add_response(
            url="http://test-postiz:5000/api/posts",
            json={
                "results": [
                    {
                        "platform": "instagram",
                        "id": "ig-123",
                        "url": "https://instagram.com/p/123",
                        "success": True,
                    },
                    {
                        "platform": "facebook",
                        "id": "fb-456",
                        "url": "https://facebook.com/post/456",
                        "success": True,
                    },
                ]
            },
        )

        client = PostizClient(base_url="http://test-postiz:5000", api_key="test-key")
        results = await client.post(
            caption="Test post!",
            image_urls=["https://example.com/img.png"],
            platforms=["instagram", "facebook"],
        )

        assert len(results) == 2
        assert results[0].success is True
        assert results[0].platform == "instagram"
        assert results[1].platform == "facebook"

    @pytest.mark.asyncio
    async def test_api_error_returns_failures(self, httpx_mock):
        """Test that HTTP errors produce failure results for each platform."""
        httpx_mock.add_response(
            url="http://test-postiz:5000/api/posts",
            status_code=500,
            json={"error": "Internal server error"},
        )

        client = PostizClient(base_url="http://test-postiz:5000", api_key="test-key")
        results = await client.post(
            caption="Test",
            image_urls=[],
            platforms=["instagram", "facebook"],
        )

        assert len(results) == 2
        assert all(not r.success for r in results)
        assert all(r.error_message is not None for r in results)


@pytest.fixture
def httpx_mock(monkeypatch):
    """Simple httpx mock fixture."""
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
        def add_response(self, url: str, json: dict | None = None, status_code: int = 200):
            responses.append({"url": url, "json": json, "status_code": status_code})

    mock = MockHelper()
    # Patch httpx.AsyncClient to use our mock transport
    original_init = httpx.AsyncClient.__init__

    def patched_init(self, *args, **kwargs):
        kwargs["transport"] = MockTransport()
        kwargs.pop("timeout", None)
        original_init(self, *args, timeout=60.0, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched_init)
    return mock
