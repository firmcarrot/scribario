"""Postiz OAuth service — manage platform connections via Postiz API.

Postiz handles OAuth flows for social media platforms (Instagram, Facebook,
TikTok, X, LinkedIn, YouTube, etc.). This module wraps the Postiz API to:
- Generate OAuth connect URLs for users
- Check which platforms a tenant has connected
- Disconnect platforms

Postiz is self-hosted via Docker on the same VPS as the worker.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from bot.config import get_settings

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 15


@dataclass
class PostizOAuthService:
    """Client for the Postiz OAuth/posting API."""

    base_url: str = ""
    api_key: str = ""

    def __post_init__(self):
        if not self.base_url:
            self.base_url = get_settings().postiz_url
        if not self.api_key:
            self.api_key = get_settings().postiz_api_key

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def get_connect_url(self, platform: str, tenant_id: str) -> str:
        """Get the OAuth authorization URL for connecting a platform.

        Args:
            platform: Social platform name (instagram, facebook, tiktok, etc.)
            tenant_id: The tenant ID to associate this connection with.

        Returns:
            The OAuth URL the user should visit to authorize.
        """
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/integrations/connect",
                headers=self._headers(),
                json={"platform": platform, "metadata": {"tenant_id": tenant_id}},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("url", "")

    async def get_connected_platforms(self, tenant_id: str) -> list[dict]:
        """Get all connected platforms for a tenant.

        Returns:
            List of dicts with platform info: {platform, username, connected_at}
        """
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/integrations",
                headers=self._headers(),
                params={"tenant_id": tenant_id},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("integrations", [])

    async def disconnect_platform(self, platform: str, tenant_id: str) -> bool:
        """Disconnect a platform for a tenant.

        Returns:
            True if successfully disconnected.
        """
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
            response = await client.delete(
                f"{self.base_url}/api/v1/integrations/{platform}",
                headers=self._headers(),
                params={"tenant_id": tenant_id},
            )
            response.raise_for_status()
            return True


# --- Module-level convenience functions ---

_service: PostizOAuthService | None = None


def _get_service() -> PostizOAuthService:
    global _service
    if _service is None:
        _service = PostizOAuthService()
    return _service


async def get_connect_url(platform: str, tenant_id: str) -> str:
    """Get OAuth URL for connecting a platform. See PostizOAuthService."""
    return await _get_service().get_connect_url(platform, tenant_id)


async def get_connected_platforms(tenant_id: str) -> list[dict]:
    """Get connected platforms for a tenant. See PostizOAuthService."""
    return await _get_service().get_connected_platforms(tenant_id)


async def disconnect_platform(platform: str, tenant_id: str) -> bool:
    """Disconnect a platform. See PostizOAuthService."""
    return await _get_service().disconnect_platform(platform, tenant_id)
