"""Tests for worker.jobs.post_content module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.posting import PostingResult


# Common message fixture
_BASE_MESSAGE = {
    "job_id": "job-123",
    "draft_id": "draft-abc",
    "tenant_id": "tenant-xyz",
    "caption": "Hello world",
    "image_urls": ["https://example.com/img.png"],
    "idempotency_key": "some-key",
}


def _make_supabase_mock(
    job_status: str = "queued",
    telegram_chat_id: int | None = 999,
) -> tuple[MagicMock, MagicMock, MagicMock]:
    """Return (supabase_mock, posting_jobs_table_mock, approval_requests_table_mock)."""
    posting_jobs_mock = MagicMock()
    posting_jobs_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{"id": "job-123", "status": job_status}]
    )
    posting_jobs_mock.update.return_value.eq.return_value.execute.return_value = MagicMock()

    approval_mock = MagicMock()
    if telegram_chat_id is not None:
        approval_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"telegram_chat_id": telegram_chat_id}]
        )
    else:
        approval_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )

    posting_results_mock = MagicMock()
    posting_results_mock.insert.return_value.execute.return_value = MagicMock(data=[{"id": "r-1"}])

    table_map = {
        "posting_jobs": posting_jobs_mock,
        "approval_requests": approval_mock,
        "posting_results": posting_results_mock,
    }

    supabase_mock = MagicMock()
    supabase_mock.table.side_effect = lambda name: table_map.get(name, MagicMock())

    return supabase_mock, posting_jobs_mock, approval_mock


class TestHandlePostContent:
    """Tests for the handle_post_content job handler."""

    @pytest.mark.asyncio
    async def test_idempotency_check_skips_already_posted_job(self):
        """If posting_jobs row already has status=posted, skip and return without posting."""
        supabase_mock, _, _ = _make_supabase_mock(job_status="posted")
        mock_bot = AsyncMock()
        mock_bot_class = MagicMock(return_value=mock_bot)

        with (
            patch("bot.db.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.Bot", mock_bot_class),
            patch("pipeline.posting.PostizClient.post", new_callable=AsyncMock) as mock_post,
        ):
            from worker.jobs.post_content import handle_post_content

            await handle_post_content(_BASE_MESSAGE)

            # PostizClient.post should NOT be called if already posted
            mock_post.assert_not_called()

    @pytest.mark.asyncio
    async def test_posts_and_updates_status_to_posted_on_all_success(self):
        """All platforms succeed → posting_jobs status updated to 'posted'."""
        supabase_mock, posting_jobs_mock, _ = _make_supabase_mock(job_status="queued", telegram_chat_id=999)
        mock_bot = AsyncMock()
        mock_bot_class = MagicMock(return_value=mock_bot)

        fake_results = [
            PostingResult(platform="facebook", platform_post_id="p1", platform_url="https://fb.com/p1", success=True),
            PostingResult(platform="instagram", platform_post_id="p2", platform_url="https://ig.com/p2", success=True),
        ]

        with (
            patch("bot.db.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.Bot", mock_bot_class),
            patch("worker.jobs.post_content.get_settings") as mock_settings,
            patch("pipeline.posting.PostizClient.post", new_callable=AsyncMock, return_value=fake_results),
        ):
            mock_settings.return_value.telegram_bot_token = "fake-token"

            from worker.jobs.post_content import handle_post_content

            await handle_post_content(_BASE_MESSAGE)

        posting_jobs_mock.update.assert_called_with({"status": "posted"})

    @pytest.mark.asyncio
    async def test_posts_and_updates_status_to_failed_on_all_failure(self):
        """All platforms fail → posting_jobs status updated to 'failed'."""
        supabase_mock, posting_jobs_mock, _ = _make_supabase_mock(job_status="queued", telegram_chat_id=999)
        mock_bot = AsyncMock()
        mock_bot_class = MagicMock(return_value=mock_bot)

        fake_results = [
            PostingResult(platform="facebook", platform_post_id=None, platform_url=None, success=False, error_message="timeout"),
        ]

        with (
            patch("bot.db.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.Bot", mock_bot_class),
            patch("worker.jobs.post_content.get_settings") as mock_settings,
            patch("pipeline.posting.PostizClient.post", new_callable=AsyncMock, return_value=fake_results),
        ):
            mock_settings.return_value.telegram_bot_token = "fake-token"

            from worker.jobs.post_content import handle_post_content

            await handle_post_content(_BASE_MESSAGE)

        posting_jobs_mock.update.assert_called_with({"status": "failed"})

    @pytest.mark.asyncio
    async def test_sends_confirmation_telegram_message_on_success(self):
        """After posting successfully, a Telegram confirmation is sent to the user."""
        supabase_mock, _, _ = _make_supabase_mock(job_status="queued", telegram_chat_id=12345)
        mock_bot = AsyncMock()
        mock_bot_class = MagicMock(return_value=mock_bot)

        fake_results = [
            PostingResult(platform="facebook", platform_post_id=None, platform_url=None, success=True),
        ]

        with (
            patch("bot.db.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.Bot", mock_bot_class),
            patch("worker.jobs.post_content.get_settings") as mock_settings,
            patch("pipeline.posting.PostizClient.post", new_callable=AsyncMock, return_value=fake_results),
        ):
            mock_settings.return_value.telegram_bot_token = "fake-token"

            from worker.jobs.post_content import handle_post_content

            await handle_post_content(_BASE_MESSAGE)

            # Bot.send_message should have been called with chat_id=12345 and success text
            mock_bot.send_message.assert_called_once()
            call_kwargs = mock_bot.send_message.call_args.kwargs
            assert call_kwargs.get("chat_id") == 12345
            assert "✅" in call_kwargs.get("text", "")

    @pytest.mark.asyncio
    async def test_sends_partial_message_on_mixed_results(self):
        """Mixed success/failure → status is 'partial' and warning message sent."""
        supabase_mock, posting_jobs_mock, _ = _make_supabase_mock(job_status="queued", telegram_chat_id=12345)
        mock_bot = AsyncMock()
        mock_bot_class = MagicMock(return_value=mock_bot)

        fake_results = [
            PostingResult(platform="facebook", platform_post_id=None, platform_url=None, success=True),
            PostingResult(platform="instagram", platform_post_id=None, platform_url=None, success=False, error_message="error"),
        ]

        with (
            patch("bot.db.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.Bot", mock_bot_class),
            patch("worker.jobs.post_content.get_settings") as mock_settings,
            patch("pipeline.posting.PostizClient.post", new_callable=AsyncMock, return_value=fake_results),
        ):
            mock_settings.return_value.telegram_bot_token = "fake-token"

            from worker.jobs.post_content import handle_post_content

            await handle_post_content(_BASE_MESSAGE)

            mock_bot.send_message.assert_called_once()
            sent_text = mock_bot.send_message.call_args.kwargs.get("text", "")
            assert "⚠️" in sent_text

        posting_jobs_mock.update.assert_called_with({"status": "partial"})

    @pytest.mark.asyncio
    async def test_no_telegram_confirmation_when_no_chat_id(self):
        """If no telegram_chat_id found, post still completes but no Telegram message sent."""
        supabase_mock, _, _ = _make_supabase_mock(job_status="queued", telegram_chat_id=None)
        mock_bot = AsyncMock()
        mock_bot_class = MagicMock(return_value=mock_bot)

        fake_results = [
            PostingResult(platform="facebook", platform_post_id=None, platform_url=None, success=True),
        ]

        with (
            patch("bot.db.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.post_content.Bot", mock_bot_class),
            patch("worker.jobs.post_content.get_settings") as mock_settings,
            patch("pipeline.posting.PostizClient.post", new_callable=AsyncMock, return_value=fake_results),
        ):
            mock_settings.return_value.telegram_bot_token = "fake-token"

            from worker.jobs.post_content import handle_post_content

            await handle_post_content(_BASE_MESSAGE)

            # No Telegram message sent when no chat_id found
            mock_bot.send_message.assert_not_called()
