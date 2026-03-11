"""Tests for bot.services.postiz_oauth — Postiz OAuth platform connection service."""

from __future__ import annotations

import asyncio

from bot.services.postiz_oauth import (
    PostizOAuthService,
    disconnect_platform,
    get_connect_url,
    get_connected_platforms,
)


class TestPostizOAuthService:
    """Verify PostizOAuthService class structure."""

    def test_instantiation(self):
        service = PostizOAuthService(base_url="http://localhost:5000", api_key="test-key")
        assert service.base_url == "http://localhost:5000"

    def test_default_base_url(self):
        service = PostizOAuthService(api_key="test-key")
        assert "localhost" in service.base_url or "postiz" in service.base_url


class TestGetConnectUrl:
    def test_is_async(self):
        assert asyncio.iscoroutinefunction(get_connect_url)

    def test_accepts_platform_and_tenant(self):
        import inspect
        sig = inspect.signature(get_connect_url)
        params = list(sig.parameters.keys())
        assert "platform" in params
        assert "tenant_id" in params


class TestGetConnectedPlatforms:
    def test_is_async(self):
        assert asyncio.iscoroutinefunction(get_connected_platforms)

    def test_accepts_tenant_id(self):
        import inspect
        sig = inspect.signature(get_connected_platforms)
        params = list(sig.parameters.keys())
        assert "tenant_id" in params


class TestDisconnectPlatform:
    def test_is_async(self):
        assert asyncio.iscoroutinefunction(disconnect_platform)

    def test_accepts_platform_and_tenant(self):
        import inspect
        sig = inspect.signature(disconnect_platform)
        params = list(sig.parameters.keys())
        assert "platform" in params
        assert "tenant_id" in params
