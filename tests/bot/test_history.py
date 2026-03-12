"""Tests for /history command — Feature 6."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestGetRecentPosts:
    """get_recent_posts returns correct structure from two-query join."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_posted_jobs(self):
        posting_jobs_mock = MagicMock()
        posting_jobs_mock.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[]
        )

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = posting_jobs_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import get_recent_posts

            result = await get_recent_posts("tenant-abc", limit=10)

        assert result == []

    @pytest.mark.asyncio
    async def test_returns_correct_structure_for_two_posts(self):
        """Two posted jobs (different drafts) → two dicts with expected keys."""
        posted_jobs = [
            {"draft_id": "draft-1", "platform": "facebook", "updated_at": "2026-03-10T12:00:00Z"},
            {"draft_id": "draft-2", "platform": "instagram", "updated_at": "2026-03-09T10:00:00Z"},
        ]
        draft_data = [
            {"id": "draft-1", "caption_variants": [{"text": "Post about sauce" * 10}], "created_at": "2026-03-10T11:00:00Z"},
            {"id": "draft-2", "caption_variants": [{"text": "Stay hungry, my friends"}], "created_at": "2026-03-09T09:00:00Z"},
        ]

        # We need to mock table() calls that go through different chains
        posting_jobs_table = MagicMock()
        posting_jobs_table.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=posted_jobs
        )

        drafts_table = MagicMock()
        drafts_table.select.return_value.in_.return_value.eq.return_value.execute.return_value = MagicMock(
            data=draft_data
        )

        def table_side_effect(name: str) -> MagicMock:
            if name == "posting_jobs":
                return posting_jobs_table
            if name == "content_drafts":
                return drafts_table
            return MagicMock()

        supabase_mock = MagicMock()
        supabase_mock.table.side_effect = table_side_effect

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import get_recent_posts

            result = await get_recent_posts("tenant-abc", limit=10)

        assert len(result) == 2
        assert result[0]["draft_id"] == "draft-1"
        assert result[0]["platforms"] == ["facebook"]
        assert "caption_preview" in result[0]
        assert "posted_at" in result[0]
        assert result[1]["draft_id"] == "draft-2"
        assert result[1]["platforms"] == ["instagram"]

    @pytest.mark.asyncio
    async def test_caption_preview_truncated_to_80_chars(self):
        long_caption = "A" * 200
        posted_jobs = [
            {"draft_id": "draft-1", "platform": "facebook", "updated_at": "2026-03-10T12:00:00Z"},
        ]
        draft_data = [
            {"id": "draft-1", "caption_variants": [{"text": long_caption}], "created_at": "2026-03-10T11:00:00Z"},
        ]

        posting_jobs_table = MagicMock()
        posting_jobs_table.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=posted_jobs
        )

        drafts_table = MagicMock()
        drafts_table.select.return_value.in_.return_value.eq.return_value.execute.return_value = MagicMock(
            data=draft_data
        )

        def table_side_effect(name: str) -> MagicMock:
            if name == "posting_jobs":
                return posting_jobs_table
            if name == "content_drafts":
                return drafts_table
            return MagicMock()

        supabase_mock = MagicMock()
        supabase_mock.table.side_effect = table_side_effect

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import get_recent_posts

            result = await get_recent_posts("tenant-abc")

        preview = result[0]["caption_preview"]
        assert len(preview) <= 83  # 80 chars + "..."
        assert preview.endswith("...")


class TestHistoryCommand:
    """handle_history command behavior."""

    @pytest.mark.asyncio
    async def test_no_posts_returns_no_posts_message(self):
        message_mock = AsyncMock()
        message_mock.from_user = MagicMock(id=12345)

        membership = {"tenant_id": "tenant-abc"}

        with (
            patch("bot.handlers.commands.get_tenant_by_telegram_user", new_callable=AsyncMock, return_value=membership),
            patch("bot.handlers.commands.get_recent_posts", new_callable=AsyncMock, return_value=[]),
        ):
            from bot.handlers.commands import handle_history

            await handle_history(message_mock)

        message_mock.answer.assert_called_once()
        call_text = message_mock.answer.call_args[0][0]
        assert "No posts yet" in call_text

    @pytest.mark.asyncio
    async def test_with_posts_returns_formatted_list(self):
        message_mock = AsyncMock()
        message_mock.from_user = MagicMock(id=12345)

        membership = {"tenant_id": "tenant-abc"}
        posts = [
            {
                "draft_id": "d1",
                "caption_preview": "The sauce that started it all... #MondoShrimp",
                "posted_at": "2026-03-10T12:00:00Z",
                "platforms": ["facebook", "instagram"],
            },
            {
                "draft_id": "d2",
                "caption_preview": "Stay Hungry, My Friends.",
                "posted_at": "2026-03-09T10:00:00Z",
                "platforms": ["facebook"],
            },
        ]

        with (
            patch("bot.handlers.commands.get_tenant_by_telegram_user", new_callable=AsyncMock, return_value=membership),
            patch("bot.handlers.commands.get_recent_posts", new_callable=AsyncMock, return_value=posts),
        ):
            from bot.handlers.commands import handle_history

            await handle_history(message_mock)

        message_mock.answer.assert_called_once()
        call_text = message_mock.answer.call_args[0][0]
        assert "Recent Posts" in call_text
        assert "Facebook" in call_text
        assert "Instagram" in call_text
        assert "The sauce that started it all" in call_text

    @pytest.mark.asyncio
    async def test_no_membership_returns_setup_message(self):
        message_mock = AsyncMock()
        message_mock.from_user = MagicMock(id=99999)

        with patch(
            "bot.handlers.commands.get_tenant_by_telegram_user",
            new_callable=AsyncMock,
            return_value=None,
        ):
            from bot.handlers.commands import handle_history

            await handle_history(message_mock)

        message_mock.answer.assert_called_once()
        call_text = message_mock.answer.call_args[0][0]
        assert "not set up" in call_text.lower() or "get started" in call_text.lower()
