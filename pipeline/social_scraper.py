"""Social media scraper — extract recent posts for few-shot examples.

Scrapes public social media profiles to gather example posts that can be
used as few-shot examples for caption generation. Uses web scraping
(no unofficial APIs that risk bans).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 15

# Platform URL patterns for handle extraction
_HANDLE_PATTERNS: dict[str, re.Pattern] = {
    "instagram": re.compile(r"instagram\.com/([^/?#]+)"),
    "facebook": re.compile(r"facebook\.com/([^/?#]+)"),
    "tiktok": re.compile(r"tiktok\.com/@([^/?#]+)"),
    "x": re.compile(r"(?:twitter|x)\.com/([^/?#]+)"),
    "youtube": re.compile(r"youtube\.com/(?:@|c/|channel/)([^/?#]+)"),
    "linkedin": re.compile(r"linkedin\.com/(?:company|in)/([^/?#]+)"),
}


@dataclass
class FewShotCandidate:
    """A social media post that could become a few-shot example."""

    platform: str
    content_type: str
    caption: str
    image_url: str | None = None
    engagement_score: float | None = None


def _extract_handle_from_url(platform: str, url: str) -> str | None:
    """Extract the social media handle/username from a profile URL."""
    pattern = _HANDLE_PATTERNS.get(platform)
    if not pattern:
        return None

    match = pattern.search(url)
    if not match:
        return None

    handle = match.group(1).rstrip("/")
    return handle if handle else None


async def scrape_social_profile(
    platform: str,
    handle: str,
) -> list[FewShotCandidate]:
    """Scrape a social media profile for recent posts.

    NOTE: Most social platforms block direct scraping of post content.
    This function attempts a best-effort scrape of publicly visible data.
    For Instagram and TikTok, it falls back to metadata-only extraction.

    Args:
        platform: The social platform (instagram, facebook, x, etc.)
        handle: The username/handle on that platform.

    Returns:
        List of FewShotCandidate objects (may be empty if scraping blocked).
    """
    candidates: list[FewShotCandidate] = []

    # Platform-specific scraping strategies
    if platform == "facebook":
        candidates = await _scrape_facebook(handle)
    elif platform == "x":
        candidates = await _scrape_x(handle)
    else:
        # Instagram, TikTok, etc. — mostly blocked without login
        logger.info(
            "Direct scraping not supported for %s, skipping",
            platform,
            extra={"handle": handle},
        )

    return candidates


async def _scrape_facebook(handle: str) -> list[FewShotCandidate]:
    """Attempt to scrape public Facebook page posts."""
    url = f"https://www.facebook.com/{handle}"
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=_REQUEST_TIMEOUT,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            },
        ) as client:
            response = await client.get(url)
            if response.status_code != 200:
                logger.warning("Facebook scrape returned %d", response.status_code)
                return []

        # Facebook heavily uses JavaScript rendering — we can only get meta
        soup = BeautifulSoup(response.text, "lxml")
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            return [
                FewShotCandidate(
                    platform="facebook",
                    content_type="page_description",
                    caption=str(desc["content"]),
                )
            ]
    except Exception:
        logger.exception("Facebook scrape failed for %s", handle)

    return []


async def _scrape_x(handle: str) -> list[FewShotCandidate]:
    """Attempt to scrape public X/Twitter profile."""
    # X requires authentication for most content now
    logger.info("X/Twitter requires login, skipping direct scrape for %s", handle)
    return []


async def build_few_shot_from_social(
    social_links: dict[str, str],
) -> list[FewShotCandidate]:
    """Scrape all social profiles and build few-shot candidates.

    Args:
        social_links: Dict mapping platform name to profile URL
                     (as extracted by the website scraper).

    Returns:
        Combined list of FewShotCandidate objects from all platforms.
    """
    all_candidates: list[FewShotCandidate] = []

    for platform, url in social_links.items():
        handle = _extract_handle_from_url(platform, url)
        if not handle:
            logger.warning("Could not extract handle from %s URL: %s", platform, url)
            continue

        candidates = await scrape_social_profile(platform, handle)
        all_candidates.extend(candidates)

    return all_candidates
