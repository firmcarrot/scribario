"""Asset resolver — loads and categorizes tenant reference photos for the Prompt Engine."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bot.db import get_reference_photos
from bot.services.storage import get_signed_urls_for_generation

logger = logging.getLogger(__name__)

MAX_PRODUCT_PHOTOS = 10
MAX_PEOPLE_PHOTOS = 4

# Labels that map to people_photos
_PEOPLE_LABELS = {"owner", "partner", "person", "team"}
# Labels that map to product_photos
_PRODUCT_LABELS = {"product"}


@dataclass
class AssetManifest:
    product_photos: list[str]
    people_photos: list[str]
    other_photos: list[str]
    logo_url: str | None = None

    @property
    def all_urls(self) -> list[str]:
        return self.product_photos + self.people_photos + self.other_photos

    @property
    def total_count(self) -> int:
        return len(self.product_photos) + len(self.people_photos) + len(self.other_photos)


async def _load_logo_url(tenant_id: str) -> str | None:
    """Load logo signed URL from brand_profiles.logo_storage_path."""
    from bot.db import get_supabase_client

    try:
        client = get_supabase_client()
        result = (
            client.table("brand_profiles")
            .select("logo_storage_path")
            .eq("tenant_id", tenant_id)
            .limit(1)
            .execute()
        )
        if result.data and result.data[0].get("logo_storage_path"):
            path = result.data[0]["logo_storage_path"]
            urls = get_signed_urls_for_generation([path])
            return urls[0] if urls else None
    except Exception:
        logger.exception("Failed to load logo URL", extra={"tenant_id": tenant_id})
    return None


async def resolve_assets(
    tenant_id: str,
    new_photo_paths: list[str] | None = None,
) -> AssetManifest:
    """Load and categorize all reference assets for a tenant.

    Args:
        tenant_id: Tenant to load assets for.
        new_photo_paths: Storage paths from the current message (treated as product photos).

    Returns:
        AssetManifest with categorized signed URLs, capped at API limits.
    """
    photos = await get_reference_photos(tenant_id)

    # Group by label
    product_paths: list[str] = []
    people_paths: list[str] = []
    other_paths: list[str] = []

    for photo in photos:
        label = (photo.get("label") or "other").lower()
        path = photo["storage_path"]
        if label in _PRODUCT_LABELS:
            product_paths.append(path)
        elif label in _PEOPLE_LABELS:
            people_paths.append(path)
        else:
            other_paths.append(path)

    # Add new photos (treat as product)
    if new_photo_paths:
        product_paths = list(new_photo_paths) + product_paths

    # Cap at limits (newest/new first since lists are ordered that way)
    product_paths = product_paths[:MAX_PRODUCT_PHOTOS]
    people_paths = people_paths[:MAX_PEOPLE_PHOTOS]

    # Generate signed URLs for all paths
    all_paths = product_paths + people_paths + other_paths
    if all_paths:
        all_signed = get_signed_urls_for_generation(all_paths)
        # Split back into categories
        p_end = len(product_paths)
        pp_end = p_end + len(people_paths)
        product_urls = all_signed[:p_end]
        people_urls = all_signed[p_end:pp_end]
        other_urls = all_signed[pp_end:]
    else:
        product_urls = []
        people_urls = []
        other_urls = []

    # Load logo
    logo_url = await _load_logo_url(tenant_id)

    return AssetManifest(
        product_photos=product_urls,
        people_photos=people_urls,
        other_photos=other_urls,
        logo_url=logo_url,
    )
