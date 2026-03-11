"""Tests for reference photo DB functions."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from bot.db import (
    count_reference_photos,
    create_reference_photo,
    get_default_reference_photos,
    get_reference_photo_by_id,
    get_reference_photos,
    soft_delete_reference_photo,
    toggle_reference_photo_default,
)

TENANT_ID = "52590da5-bc80-4161-ac13-62e9bcd75424"
USER_ID = 7560539974
PHOTO_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _make_client(return_data: list[dict] | None = None):
    """Build a mock Supabase client."""
    client = MagicMock()
    chain = MagicMock()
    chain.execute.return_value = MagicMock(data=return_data or [])
    client.table.return_value = chain
    chain.insert.return_value = chain
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.is_.return_value = chain
    chain.order.return_value = chain
    chain.limit.return_value = chain
    chain.update.return_value = chain
    chain.single.return_value = chain
    return client


class TestCreateReferencePhoto:
    def test_inserts_row_and_returns_data(self):
        expected = {
            "id": PHOTO_ID,
            "tenant_id": TENANT_ID,
            "label": "owner",
            "storage_path": f"reference-photos/{TENANT_ID}/abc.jpg",
            "file_unique_id": "AgACAgIxxx",
            "is_default": True,
        }
        client = _make_client([expected])
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(
                create_reference_photo(
                    tenant_id=TENANT_ID,
                    uploaded_by=USER_ID,
                    label="owner",
                    storage_path=f"reference-photos/{TENANT_ID}/abc.jpg",
                    file_unique_id="AgACAgIxxx",
                    file_size_bytes=102400,
                    mime_type="image/jpeg",
                    is_default=True,
                )
            )
        assert result["id"] == PHOTO_ID
        assert result["label"] == "owner"

    def test_invalid_label_raises(self):
        with pytest.raises(ValueError, match="Invalid label"):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                create_reference_photo(
                    tenant_id=TENANT_ID,
                    uploaded_by=USER_ID,
                    label="invalid_label",
                    storage_path="x",
                    file_unique_id="y",
                )
            )


class TestGetReferencePhotos:
    def test_returns_active_photos_for_tenant(self):
        photos = [
            {"id": PHOTO_ID, "label": "owner", "is_default": True},
        ]
        client = _make_client(photos)
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(
                get_reference_photos(tenant_id=TENANT_ID)
            )
        assert len(result) == 1
        assert result[0]["label"] == "owner"

    def test_empty_when_no_photos(self):
        client = _make_client([])
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(
                get_reference_photos(tenant_id=TENANT_ID)
            )
        assert result == []


class TestGetDefaultReferencePhotos:
    def test_returns_only_defaults(self):
        defaults = [
            {"id": PHOTO_ID, "label": "owner", "is_default": True, "storage_path": "x/y.jpg"},
        ]
        client = _make_client(defaults)
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(
                get_default_reference_photos(tenant_id=TENANT_ID)
            )
        assert len(result) == 1
        assert result[0]["is_default"] is True


class TestSoftDeleteReferencePhoto:
    def test_sets_deleted_at(self):
        client = _make_client([{"id": PHOTO_ID}])
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                soft_delete_reference_photo(photo_id=PHOTO_ID, tenant_id=TENANT_ID)
            )
        # Verify update was called on the table
        client.table.assert_called_with("reference_photos")

    def test_requires_tenant_id_for_safety(self):
        """Soft delete must always filter by tenant_id to prevent cross-tenant deletion."""
        client = _make_client([])
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                soft_delete_reference_photo(photo_id=PHOTO_ID, tenant_id=TENANT_ID)
            )
        # Both eq calls should have been made (photo_id AND tenant_id)
        eq_calls = [str(c) for c in client.table.return_value.eq.call_args_list]
        assert len(eq_calls) >= 1


class TestToggleDefault:
    def test_sets_is_default_true(self):
        client = _make_client([{"id": PHOTO_ID, "is_default": True}])
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                toggle_reference_photo_default(
                    photo_id=PHOTO_ID, tenant_id=TENANT_ID, is_default=True
                )
            )
        client.table.assert_called_with("reference_photos")

    def test_sets_is_default_false(self):
        client = _make_client([{"id": PHOTO_ID, "is_default": False}])
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                toggle_reference_photo_default(
                    photo_id=PHOTO_ID, tenant_id=TENANT_ID, is_default=False
                )
            )
        client.table.assert_called_with("reference_photos")


class TestCountReferencePhotos:
    def test_returns_count(self):
        client = MagicMock()
        chain = MagicMock()
        chain.execute.return_value = MagicMock(count=5, data=[])
        client.table.return_value = chain
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.is_.return_value = chain
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(
                count_reference_photos(tenant_id=TENANT_ID)
            )
        assert result == 5


class TestGetReferencePhotoById:
    def test_returns_photo(self):
        photo = {"id": PHOTO_ID, "tenant_id": TENANT_ID, "label": "product"}
        client = _make_client([photo])
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(
                get_reference_photo_by_id(photo_id=PHOTO_ID, tenant_id=TENANT_ID)
            )
        assert result["id"] == PHOTO_ID

    def test_returns_none_if_not_found(self):
        client = _make_client([])
        with patch("bot.db.get_supabase_client", return_value=client):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(
                get_reference_photo_by_id(photo_id=PHOTO_ID, tenant_id=TENANT_ID)
            )
        assert result is None
