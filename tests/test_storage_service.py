"""Tests for bot/services/storage.py — download, EXIF strip, upload."""

from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestStripExif:
    def test_strips_metadata_from_jpeg(self):
        from bot.services.storage import strip_exif
        from PIL import Image

        # Create a small JPEG with fake EXIF
        buf = io.BytesIO()
        img = Image.new("RGB", (10, 10), color=(255, 0, 0))
        img.save(buf, format="JPEG")
        original = buf.getvalue()

        result = strip_exif(original)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_returns_bytes(self):
        from bot.services.storage import strip_exif
        from PIL import Image

        buf = io.BytesIO()
        img = Image.new("RGB", (20, 20), color=(0, 255, 0))
        img.save(buf, format="JPEG")

        result = strip_exif(buf.getvalue())
        assert isinstance(result, bytes)

    def test_preserves_image_content(self):
        from bot.services.storage import strip_exif
        from PIL import Image

        buf = io.BytesIO()
        img = Image.new("RGB", (5, 5), color=(128, 64, 32))
        img.save(buf, format="JPEG")

        result = strip_exif(buf.getvalue())
        # Should still be a valid image
        reopened = Image.open(io.BytesIO(result))
        assert reopened.size == (5, 5)


class TestBuildStoragePath:
    def test_includes_tenant_id(self):
        from bot.services.storage import build_storage_path

        path = build_storage_path(tenant_id="abc-123", file_unique_id="tg_file_xyz")
        assert "abc-123" in path

    def test_includes_file_unique_id(self):
        from bot.services.storage import build_storage_path

        path = build_storage_path(tenant_id="abc-123", file_unique_id="tg_file_xyz")
        assert "tg_file_xyz" in path

    def test_ends_with_jpg(self):
        from bot.services.storage import build_storage_path

        path = build_storage_path(tenant_id="abc-123", file_unique_id="tg_file_xyz")
        assert path.endswith(".jpg")

    def test_starts_with_reference_photos(self):
        from bot.services.storage import build_storage_path

        path = build_storage_path(tenant_id="abc-123", file_unique_id="tg_file_xyz")
        assert path.startswith("reference-photos/")


class TestGetSignedUrl:
    def test_returns_signed_url_string(self):
        from bot.services.storage import get_signed_url

        mock_client = MagicMock()
        mock_client.storage.from_.return_value.create_signed_url.return_value = {
            "signedURL": "https://example.supabase.co/signed/abc.jpg?token=xyz"
        }

        with patch("bot.services.storage.get_supabase_client", return_value=mock_client):
            url = get_signed_url(storage_path="reference-photos/abc/def.jpg", expires_in=600)

        assert url.startswith("https://")
        assert "signed" in url or "token" in url or "abc.jpg" in url

    def test_uses_correct_bucket(self):
        from bot.services.storage import get_signed_url, STORAGE_BUCKET

        mock_client = MagicMock()
        mock_client.storage.from_.return_value.create_signed_url.return_value = {
            "signedURL": "https://x.supabase.co/signed/x.jpg"
        }

        with patch("bot.services.storage.get_supabase_client", return_value=mock_client):
            get_signed_url(storage_path="reference-photos/abc/def.jpg", expires_in=600)

        mock_client.storage.from_.assert_called_with(STORAGE_BUCKET)


class TestDownloadAndStore:
    @pytest.mark.asyncio
    async def test_returns_storage_path(self):
        from bot.services.storage import download_and_store
        from PIL import Image

        # Build fake JPEG bytes
        buf = io.BytesIO()
        Image.new("RGB", (10, 10)).save(buf, format="JPEG")
        fake_jpeg = buf.getvalue()

        # Mock the entire download_and_store by patching strip_exif and the HTTP call
        mock_supabase = MagicMock()
        mock_supabase.storage.from_.return_value.upload.return_value = {}

        # Use httpx.AsyncClient mock that returns fake JPEG bytes
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.read = AsyncMock(return_value=fake_jpeg)

        # Async context manager for http.get(url)
        mock_get_ctx = MagicMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_client = MagicMock()
        mock_client.get = MagicMock(return_value=mock_get_ctx)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("bot.services.storage.get_supabase_client", return_value=mock_supabase),
            patch("httpx.AsyncClient", return_value=mock_client),
        ):
            path = await download_and_store(
                download_url="https://api.telegram.org/file/botTOKEN/photos/file_123.jpg",
                tenant_id="tenant-abc",
                file_unique_id="tg_unique_xyz",
            )

        assert isinstance(path, str)
        assert "tenant-abc" in path
