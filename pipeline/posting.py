"""Posting module — Postiz Agent CLI wrapper for multi-platform posting."""

from __future__ import annotations

import logging
from dataclasses import dataclass

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
        self._base_url = (base_url or get_settings().postiz_url).rstrip("/")
        self._api_key = api_key or get_settings().postiz_api_key
        self._client = httpx.AsyncClient(timeout=60.0)

    async def post(
        self,
        caption: str,
        image_urls: list[str],
        platforms: list[str],
        scheduled_for: str | None = None,
    ) -> list[PostingResult]:
        """Submit a post to Postiz for publishing.

        Args:
            caption: Post text/caption.
            image_urls: List of image URLs to attach.
            platforms: Target platforms (e.g., ['instagram', 'facebook']).
            scheduled_for: ISO timestamp for scheduled posting, or None for immediate.

        Returns:
            List of PostingResult per platform.
        """
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload: dict = {
            "content": caption,
            "media": [{"url": url, "type": "image"} for url in image_urls],
            "platforms": platforms,
        }
        if scheduled_for:
            payload["scheduled_for"] = scheduled_for

        results: list[PostingResult] = []
        try:
            response = await self._client.post(
                f"{self._base_url}/api/posts",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            # Postiz returns per-platform results
            for platform_result in data.get("results", []):
                results.append(
                    PostingResult(
                        platform=platform_result.get("platform", "unknown"),
                        platform_post_id=platform_result.get("id"),
                        platform_url=platform_result.get("url"),
                        success=platform_result.get("success", False),
                        error_message=platform_result.get("error"),
                    )
                )

            logger.info(
                "Postiz submission complete",
                extra={
                    "platforms": platforms,
                    "success_count": sum(1 for r in results if r.success),
                },
            )
        except httpx.HTTPStatusError as e:
            logger.error("Postiz API error", extra={"status": e.response.status_code})
            for platform in platforms:
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
            for platform in platforms:
                results.append(
                    PostingResult(
                        platform=platform,
                        platform_post_id=None,
                        platform_url=None,
                        success=False,
                        error_message=str(e),
                    )
                )

        return results
