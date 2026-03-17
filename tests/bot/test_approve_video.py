"""Tests for approve_video caption selection in approval handler."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.approval import handle_approve_video


def _make_callback(data: str, chat_id: int = 999) -> MagicMock:
    """Create a mock CallbackQuery."""
    cb = AsyncMock()
    cb.data = data
    cb.from_user = MagicMock(id=12345)
    cb.message = MagicMock()
    cb.message.chat = MagicMock(id=chat_id)
    cb.message.edit_reply_markup = AsyncMock()
    cb.message.reply = AsyncMock()
    cb.answer = AsyncMock()
    return cb


def _make_draft(draft_id: str = "draft-1", video_url: str = "https://cdn/vid.mp4") -> dict:
    return {
        "id": draft_id,
        "tenant_id": "tenant-1",
        "request_id": "req-1",
        "status": "previewing",
        "video_url": video_url,
        "caption_variants": [
            {"text": "Caption one #hot"},
            {"text": "Caption two #spicy"},
            {"text": "Caption three #fire"},
        ],
        "image_urls": ["https://img/1.jpg"],
    }


class TestApproveVideoWithCaptionSelection:
    """Test that approve_video:{draft_id}:{option_number} picks the right caption."""

    @pytest.mark.asyncio
    async def test_selects_caption_by_option_number(self):
        """approve_video:draft-1:2 should pick caption index 1 (second option)."""
        draft = _make_draft()
        cb = _make_callback("approve_video:draft-1:2")

        with (
            patch("bot.handlers.approval._validate_draft_access",
                  new_callable=AsyncMock, return_value=draft),
            patch("bot.handlers.approval.update_draft_status",
                  new_callable=AsyncMock),
            patch("bot.handlers.approval.create_feedback_event",
                  new_callable=AsyncMock),
            patch("bot.handlers.approval.get_supabase_client") as mock_client,
            patch("bot.handlers.approval.create_posting_job",
                  new_callable=AsyncMock, return_value={"id": "job-1"}) as mock_post,
            patch("bot.handlers.approval.enqueue_job",
                  new_callable=AsyncMock) as mock_enqueue,
        ):
            # Mock platform_targets query
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
                MagicMock(data=[{"platform_targets": ["facebook"]}])
            )
            mock_client.return_value.table.return_value = mock_table

            await handle_approve_video(cb)

            # Should use caption #2 (index 1) = "Caption two #spicy"
            post_call = mock_post.call_args
            assert post_call.kwargs["caption"] == "Caption two #spicy"

            # Enqueue should also have caption #2
            enqueue_call = mock_enqueue.call_args
            assert enqueue_call.kwargs["payload"]["caption"] == "Caption two #spicy"

    @pytest.mark.asyncio
    async def test_defaults_to_first_caption_without_option(self):
        """approve_video:draft-1 (no option) should default to first caption."""
        draft = _make_draft()
        cb = _make_callback("approve_video:draft-1")

        with (
            patch("bot.handlers.approval._validate_draft_access",
                  new_callable=AsyncMock, return_value=draft),
            patch("bot.handlers.approval.update_draft_status",
                  new_callable=AsyncMock),
            patch("bot.handlers.approval.create_feedback_event",
                  new_callable=AsyncMock),
            patch("bot.handlers.approval.get_supabase_client") as mock_client,
            patch("bot.handlers.approval.create_posting_job",
                  new_callable=AsyncMock, return_value={"id": "job-1"}) as mock_post,
            patch("bot.handlers.approval.enqueue_job",
                  new_callable=AsyncMock),
        ):
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
                MagicMock(data=[{"platform_targets": None}])
            )
            mock_client.return_value.table.return_value = mock_table

            await handle_approve_video(cb)

            post_call = mock_post.call_args
            assert post_call.kwargs["caption"] == "Caption one #hot"

    @pytest.mark.asyncio
    async def test_posts_video_url_as_asset(self):
        """Video URL should be the asset, not image URLs."""
        draft = _make_draft(video_url="https://cdn/my-video.mp4")
        cb = _make_callback("approve_video:draft-1:1")

        with (
            patch("bot.handlers.approval._validate_draft_access",
                  new_callable=AsyncMock, return_value=draft),
            patch("bot.handlers.approval.update_draft_status",
                  new_callable=AsyncMock),
            patch("bot.handlers.approval.create_feedback_event",
                  new_callable=AsyncMock),
            patch("bot.handlers.approval.get_supabase_client") as mock_client,
            patch("bot.handlers.approval.create_posting_job",
                  new_callable=AsyncMock, return_value={"id": "job-1"}) as mock_post,
            patch("bot.handlers.approval.enqueue_job",
                  new_callable=AsyncMock) as mock_enqueue,
        ):
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
                MagicMock(data=[{"platform_targets": None}])
            )
            mock_client.return_value.table.return_value = mock_table

            await handle_approve_video(cb)

            # Asset should be the video URL
            post_call = mock_post.call_args
            assert post_call.kwargs["asset_urls"] == ["https://cdn/my-video.mp4"]

            # Enqueue payload should have media_type=video
            enqueue_call = mock_enqueue.call_args
            assert enqueue_call.kwargs["payload"]["media_type"] == "video"
