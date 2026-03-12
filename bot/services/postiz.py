"""Postiz API client — org management, channel invites, and posting."""

from __future__ import annotations

import logging

import httpx

from bot.config import get_settings

logger = logging.getLogger(__name__)


def _headers() -> dict[str, str]:
    settings = get_settings()
    return {
        "Authorization": f"Bearer {settings.postiz_api_key}",
        "Content-Type": "application/json",
    }


def _admin_headers() -> dict[str, str]:
    """Headers using session cookie for admin-only endpoints."""
    settings = get_settings()
    return {
        "Cookie": f"auth={settings.postiz_session_token}",
        "Content-Type": "application/json",
    }


async def create_org_invite(email: str, role: str = "USER") -> str:
    """Create a Postiz org invite link for a new client.

    Returns the join URL to send to the client.
    """
    settings = get_settings()
    url = f"{settings.postiz_url}/api/settings/team"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=_admin_headers(),
            json={"email": email, "role": role, "sendEmail": False},
        )
        response.raise_for_status()
        data = response.json()
        return data["url"]


async def get_oauth_url(platform: str) -> str:
    """Get the OAuth authorization URL for a social platform.

    Args:
        platform: Platform name e.g. 'facebook', 'instagram', 'linkedin'

    Returns:
        The OAuth URL to redirect the user to.
    """
    settings = get_settings()
    url = f"{settings.postiz_url}/api/integrations/social/{platform}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=_admin_headers())
        response.raise_for_status()
        data = response.json()
        return data["url"]


async def get_connected_channels(org_id: str | None = None) -> list[dict]:
    """Get all connected social channels for an org."""
    settings = get_settings()
    url = f"{settings.postiz_url}/api/integrations"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=_headers())
        response.raise_for_status()
        return response.json()


async def post_content(
    integration_ids: list[str],
    content: str,
    image_url: str | None = None,
    publish_now: bool = True,
) -> dict:
    """Post content to one or more social channels via Postiz.

    Args:
        integration_ids: Postiz channel integration IDs to post to.
        content: The caption/text to post.
        image_url: Optional image URL to include.
        publish_now: If True, publish immediately. If False, save as draft.

    Returns:
        Postiz API response.
    """
    settings = get_settings()
    url = f"{settings.postiz_url}/api/posts"

    posts = []
    for integration_id in integration_ids:
        post: dict = {
            "integration": {"id": integration_id},
            "value": [{"content": content}],
            "publishDate": None,
            "settings": {},
        }
        if image_url:
            post["value"][0]["image"] = [{"url": image_url}]
        posts.append(post)

    payload = {
        "type": "now" if publish_now else "draft",
        "posts": posts,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=_headers(), json=payload)
        response.raise_for_status()
        return response.json()
