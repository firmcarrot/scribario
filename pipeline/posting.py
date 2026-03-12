"""Posting module — Postiz API client for multi-platform posting."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from bot.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class PostingResult:
    """Result from posting to a platform."""

    platform: str
    platform_post_id: str | None
    platform_url: str | None
    success: bool
    error_message: str | None = None


class PostizClient:
    """Client for Postiz self-hosted posting API."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        settings = get_settings()
        self._base_url = (base_url or settings.postiz_url).rstrip("/")
        self._api_key = api_key or settings.postiz_api_key
        self._session_token = settings.postiz_session_token

    def _headers(self) -> dict[str, str]:
        return {
            "Cookie": f"auth={self._session_token}",
            "Content-Type": "application/json",
        }

    async def get_integrations(self) -> list[dict]:
        """Get all connected social channel integrations."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self._base_url}/api/integrations/list",
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()
            return data.get("integrations", [])

    async def post(
        self,
        caption: str,
        image_urls: list[str],
        platforms: list[str] | None = None,
        scheduled_for: str | None = None,
    ) -> list[PostingResult]:
        """Submit a post to Postiz for publishing.

        Args:
            caption: Post text/caption.
            image_urls: List of image URLs to attach.
            platforms: Target platform identifiers. If None or empty, posts to all connected.
            scheduled_for: ISO timestamp for scheduled posting, or None for immediate.

        Returns:
            List of PostingResult per platform.
        """
        # Get connected integrations
        try:
            integrations = await self.get_integrations()
        except Exception as e:
            logger.error("Failed to fetch Postiz integrations", extra={"error": str(e)})
            return [
                PostingResult(
                    platform=p,
                    platform_post_id=None,
                    platform_url=None,
                    success=False,
                    error_message=f"Could not fetch integrations: {e}",
                )
                for p in (platforms or ["unknown"])
            ]

        # Map platform name → integration ID, filtered by requested platforms (or all)
        platform_to_integration: dict[str, str] = {}
        for integration in integrations:
            identifier = integration.get("identifier", "")
            int_id = integration.get("id", "")
            if not platforms or identifier in platforms:
                platform_to_integration[identifier] = int_id

        if not platform_to_integration:
            logger.warning(
                "No matching integrations found for platforms",
                extra={"platforms": platforms, "available": [i.get("identifier") for i in integrations]},
            )
            return [
                PostingResult(
                    platform=p,
                    platform_post_id=None,
                    platform_url=None,
                    success=False,
                    error_message="No connected account found for this platform. Use /connect to add one.",
                )
                for p in (platforms or ["unknown"])
            ]

        # Build Postiz posts payload — one post per integration
        # image field must always be an array; path key required (not url)
        posts = []
        for platform, integration_id in platform_to_integration.items():
            images = [{"id": str(i), "path": url} for i, url in enumerate(image_urls)]
            post: dict = {
                "integration": {"id": integration_id},
                "value": [{"content": caption, "image": images}],
            }
            posts.append((platform, post))

        results: list[PostingResult] = []

        payload = {
            "type": "now",
            "shortLink": False,
            "date": datetime.now(UTC).isoformat(),
            "tags": [],
            "posts": [p for _, p in posts],
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self._base_url}/api/posts",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            logger.info("Postiz post submitted", extra={"platforms": list(platform_to_integration.keys()), "response": str(data)[:200]})

            # Mark all as successful
            for platform, _ in posts:
                results.append(
                    PostingResult(
                        platform=platform,
                        platform_post_id=None,
                        platform_url=None,
                        success=True,
                    )
                )

        except httpx.HTTPStatusError as e:
            logger.error(
                "Postiz API error",
                extra={"status": e.response.status_code, "body": e.response.text[:500]},
            )
            for platform, _ in posts:
                results.append(
                    PostingResult(
                        platform=platform,
                        platform_post_id=None,
                        platform_url=None,
                        success=False,
                        error_message=f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                    )
                )
        except httpx.RequestError as e:
            logger.error("Postiz connection error", extra={"error": str(e)})
            for platform, _ in posts:
                results.append(
                    PostingResult(
                        platform=platform,
                        platform_post_id=None,
                        platform_url=None,
                        success=False,
                        error_message=str(e),
                    )
                )

        # Add failures for platforms with no connected integration (only when specific platforms were requested)
        for platform in (platforms or []):
            if platform not in platform_to_integration:
                results.append(
                    PostingResult(
                        platform=platform,
                        platform_post_id=None,
                        platform_url=None,
                        success=False,
                        error_message="No connected account for this platform.",
                    )
                )

        return results
