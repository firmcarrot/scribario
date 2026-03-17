"""Tests for content_library DB functions."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for content_library operations."""
    with patch("bot.db.get_supabase_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestSaveToContentLibrary:
    """Tests for save_to_content_library."""

    @pytest.mark.asyncio
    async def test_inserts_image_item(self, mock_supabase):
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{
                "id": "lib-1",
                "tenant_id": "t-1",
                "source_draft_id": "d-1",
                "caption": "Great sauce!",
                "image_url": "https://img.com/1.jpg",
                "video_url": None,
                "media_type": "image",
                "status": "saved",
            }]
        )

        from bot.db import save_to_content_library

        result = await save_to_content_library(
            tenant_id="t-1",
            source_draft_id="d-1",
            caption="Great sauce!",
            media_type="image",
            image_url="https://img.com/1.jpg",
        )

        assert result["id"] == "lib-1"
        assert result["status"] == "saved"
        mock_supabase.table.assert_called_with("content_library")
        insert_data = mock_supabase.table.return_value.insert.call_args[0][0]
        assert insert_data["tenant_id"] == "t-1"
        assert insert_data["caption"] == "Great sauce!"
        assert insert_data["media_type"] == "image"
        assert insert_data["image_url"] == "https://img.com/1.jpg"
        assert insert_data.get("video_url") is None

    @pytest.mark.asyncio
    async def test_inserts_video_item(self, mock_supabase):
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{
                "id": "lib-2",
                "tenant_id": "t-1",
                "media_type": "video",
                "video_url": "https://cdn.kie.ai/v.mp4",
                "status": "saved",
            }]
        )

        from bot.db import save_to_content_library

        result = await save_to_content_library(
            tenant_id="t-1",
            source_draft_id="d-1",
            caption="Shrimp video caption",
            media_type="video",
            video_url="https://cdn.kie.ai/v.mp4",
        )

        assert result["media_type"] == "video"
        insert_data = mock_supabase.table.return_value.insert.call_args[0][0]
        assert insert_data["video_url"] == "https://cdn.kie.ai/v.mp4"

    @pytest.mark.asyncio
    async def test_includes_platform_targets(self, mock_supabase):
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": "lib-3", "platform_targets": ["facebook", "instagram"]}]
        )

        from bot.db import save_to_content_library

        await save_to_content_library(
            tenant_id="t-1",
            source_draft_id="d-1",
            caption="cap",
            media_type="image",
            platform_targets=["facebook", "instagram"],
        )

        insert_data = mock_supabase.table.return_value.insert.call_args[0][0]
        assert insert_data["platform_targets"] == ["facebook", "instagram"]


class TestGetLibraryItems:
    """Tests for get_library_items."""

    @pytest.mark.asyncio
    async def test_returns_saved_items_for_tenant(self, mock_supabase):
        chain = mock_supabase.table.return_value
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.order.return_value = chain
        chain.limit.return_value = chain
        chain.offset.return_value = chain
        chain.execute.return_value = MagicMock(
            data=[{"id": "lib-1", "caption": "Saved caption"}]
        )

        from bot.db import get_library_items

        result = await get_library_items(tenant_id="t-1", offset=0, limit=1)

        assert len(result) == 1
        assert result[0]["caption"] == "Saved caption"
        # Verify tenant_id filter applied (called twice: for tenant_id and status)
        eq_calls = chain.eq.call_args_list
        assert any(c[0] == ("tenant_id", "t-1") for c in eq_calls)
        assert any(c[0] == ("status", "saved") for c in eq_calls)

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_none(self, mock_supabase):
        chain = mock_supabase.table.return_value
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.order.return_value = chain
        chain.limit.return_value = chain
        chain.offset.return_value = chain
        chain.execute.return_value = MagicMock(data=[])

        from bot.db import get_library_items

        result = await get_library_items(tenant_id="t-1")
        assert result == []


class TestCountLibraryItems:
    """Tests for count_library_items."""

    @pytest.mark.asyncio
    async def test_returns_count(self, mock_supabase):
        chain = mock_supabase.table.return_value
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.execute.return_value = MagicMock(count=5)

        from bot.db import count_library_items

        result = await count_library_items(tenant_id="t-1")
        assert result == 5

    @pytest.mark.asyncio
    async def test_returns_zero_when_empty(self, mock_supabase):
        chain = mock_supabase.table.return_value
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.execute.return_value = MagicMock(count=0)

        from bot.db import count_library_items

        result = await count_library_items(tenant_id="t-1")
        assert result == 0


class TestUpdateLibraryItemStatus:
    """Tests for update_library_item_status."""

    @pytest.mark.asyncio
    async def test_updates_status_with_tenant_scope(self, mock_supabase):
        chain = mock_supabase.table.return_value
        chain.update.return_value = chain
        chain.eq.return_value = chain
        chain.execute.return_value = MagicMock()

        from bot.db import update_library_item_status

        await update_library_item_status("lib-1", tenant_id="t-1", status="posted")

        chain.update.assert_called_once()
        update_data = chain.update.call_args[0][0]
        assert update_data["status"] == "posted"
        # Must scope to tenant_id
        eq_calls = chain.eq.call_args_list
        assert any(c[0] == ("tenant_id", "t-1") for c in eq_calls)
        assert any(c[0] == ("id", "lib-1") for c in eq_calls)

    @pytest.mark.asyncio
    async def test_sets_posted_at_when_posting(self, mock_supabase):
        chain = mock_supabase.table.return_value
        chain.update.return_value = chain
        chain.eq.return_value = chain
        chain.execute.return_value = MagicMock()

        from bot.db import update_library_item_status

        await update_library_item_status("lib-1", tenant_id="t-1", status="posted")

        update_data = chain.update.call_args[0][0]
        assert "posted_at" in update_data


class TestGetLibraryItem:
    """Tests for get_library_item."""

    @pytest.mark.asyncio
    async def test_returns_item_scoped_to_tenant(self, mock_supabase):
        chain = mock_supabase.table.return_value
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.limit.return_value = chain
        chain.execute.return_value = MagicMock(
            data=[{"id": "lib-1", "tenant_id": "t-1", "caption": "Test"}]
        )

        from bot.db import get_library_item

        result = await get_library_item("lib-1", tenant_id="t-1")

        assert result is not None
        assert result["id"] == "lib-1"
        eq_calls = chain.eq.call_args_list
        assert any(c[0] == ("tenant_id", "t-1") for c in eq_calls)
        assert any(c[0] == ("id", "lib-1") for c in eq_calls)

    @pytest.mark.asyncio
    async def test_returns_none_for_wrong_tenant(self, mock_supabase):
        chain = mock_supabase.table.return_value
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.limit.return_value = chain
        chain.execute.return_value = MagicMock(data=[])

        from bot.db import get_library_item

        result = await get_library_item("lib-1", tenant_id="wrong-tenant")
        assert result is None
