"""Supabase Storage service — download from Telegram, strip EXIF, store privately.

Flow per photo:
  1. Download bytes from Telegram (60-min URL)
  2. Strip EXIF metadata (privacy — removes GPS, device info)
  3. Upload to private Supabase Storage bucket under tenant-scoped path
  4. Return storage_path (permanent, used to generate signed URLs at generation time)

Signed URLs (600s TTL) are generated fresh per generation request and passed to Kie.ai.
Never store raw public URLs — always store the path and sign on demand.
"""

from __future__ import annotations

import io
import logging

import httpx
from PIL import Image

from bot.db import get_supabase_client

logger = logging.getLogger(__name__)

STORAGE_BUCKET = "reference-photos"
SIGNED_URL_TTL = 600  # 10 minutes — plenty for Kie.ai to fetch


def strip_exif(image_bytes: bytes, preserve_alpha: bool = False) -> tuple[bytes, str]:
    """Remove EXIF metadata from image bytes.

    Strips GPS coordinates, device model, timestamps, and other metadata
    that could compromise user privacy.

    Args:
        image_bytes: Raw image bytes.
        preserve_alpha: If True, keep PNG format for images with transparency
            (important for logos). If False, always convert to JPEG.

    Returns:
        (clean_bytes, content_type) tuple. content_type is "image/png" or "image/jpeg".
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Determine output format: preserve PNG if alpha channel exists and requested
    has_alpha = img.mode in ("RGBA", "LA", "PA") or (
        img.mode == "P" and "transparency" in img.info
    )
    use_png = preserve_alpha and has_alpha

    if use_png:
        # Keep RGBA for transparency
        if img.mode != "RGBA":
            img = img.convert("RGBA")
    else:
        # Convert to RGB for JPEG
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

    # Create new image with same pixel data but no metadata
    clean = Image.new(img.mode, img.size)
    clean.putdata(list(img.getdata()))
    buf = io.BytesIO()
    if use_png:
        clean.save(buf, format="PNG", optimize=True)
        return buf.getvalue(), "image/png"
    else:
        clean.save(buf, format="JPEG", quality=92)
        return buf.getvalue(), "image/jpeg"


def build_storage_path(tenant_id: str, file_unique_id: str) -> str:
    """Build a tenant-scoped storage path for a reference photo.

    Format: reference-photos/{tenant_id}/{file_unique_id}.jpg
    Tenant scoping enables bucket policy enforcement and easy bulk deletion.
    """
    return f"reference-photos/{tenant_id}/{file_unique_id}.jpg"


def get_signed_url(storage_path: str, expires_in: int = SIGNED_URL_TTL) -> str:
    """Generate a short-lived signed URL for a private storage file.

    The signed URL is public HTTPS (required by Kie.ai image_input) but expires
    after `expires_in` seconds. Default 600s is sufficient for Kie.ai to fetch.
    """
    client = get_supabase_client()
    response = client.storage.from_(STORAGE_BUCKET).create_signed_url(
        storage_path, expires_in
    )
    # Supabase returns {"signedURL": "https://..."} or {"error": "..."}
    signed_url = response.get("signedURL") or response.get("signedUrl")
    if not signed_url:
        raise RuntimeError(
            f"Failed to create signed URL for {storage_path}: {response}"
        )
    return signed_url


MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB — reject oversized uploads


async def download_and_store(
    download_url: str,
    tenant_id: str,
    file_unique_id: str,
    preserve_alpha: bool = False,
) -> str:
    """Download photo from Telegram, strip EXIF, upload to Supabase Storage.

    Args:
        download_url: Temporary Telegram file download URL (60-min TTL).
        tenant_id: Tenant UUID for scoped storage path.
        file_unique_id: Telegram's stable file_unique_id for deduplication.
        preserve_alpha: If True, keep PNG format for images with transparency (logos).

    Returns:
        storage_path: Permanent path in Supabase Storage (use get_signed_url to access).

    Raises:
        ValueError: If the downloaded file exceeds MAX_UPLOAD_SIZE or is not a valid image.
    """
    # Download from Telegram
    async with httpx.AsyncClient(timeout=60.0) as http:
        response = await http.get(download_url)
        response.raise_for_status()
        image_bytes = response.content

    if len(image_bytes) > MAX_UPLOAD_SIZE:
        raise ValueError(
            f"File too large ({len(image_bytes)} bytes, max {MAX_UPLOAD_SIZE})"
        )

    # Validate it's actually an image
    try:
        with Image.open(io.BytesIO(image_bytes)) as test_img:
            test_img.verify()
    except Exception as e:
        raise ValueError(f"File is not a valid image: {e}") from e

    logger.info(
        "Downloaded photo from Telegram",
        extra={"file_unique_id": file_unique_id, "size_bytes": len(image_bytes)},
    )

    # Strip EXIF for privacy
    clean_bytes, content_type = strip_exif(image_bytes, preserve_alpha=preserve_alpha)

    # Determine file extension from content type
    ext = "png" if content_type == "image/png" else "jpg"

    logger.info(
        "EXIF stripped",
        extra={
            "file_unique_id": file_unique_id,
            "original_size": len(image_bytes),
            "clean_size": len(clean_bytes),
            "content_type": content_type,
        },
    )

    # Upload to private Supabase Storage bucket
    storage_path = f"reference-photos/{tenant_id}/{file_unique_id}.{ext}"
    client = get_supabase_client()
    client.storage.from_(STORAGE_BUCKET).upload(
        storage_path,
        clean_bytes,
        file_options={"content-type": content_type, "upsert": "true"},
    )

    logger.info(
        "Photo uploaded to Supabase Storage",
        extra={"storage_path": storage_path, "tenant_id": tenant_id},
    )

    return storage_path


def get_signed_urls_for_generation(storage_paths: list[str]) -> list[str]:
    """Generate fresh signed URLs for a batch of storage paths.

    Called right before submitting to Kie.ai so URLs are always fresh.
    TTL is 600s — well within Kie.ai's fetch window.
    """
    return [get_signed_url(path) for path in storage_paths]
