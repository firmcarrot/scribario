"""Tests for brand voice learning — Feature 7."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from pipeline.posting import PostingResult


# Common base message for all brand voice tests
_BASE_MESSAGE = {
    "job_id": "job-brandvoice",
    "draft_id": "draft-bv",
    "tenant_id": "tenant-bv",
    "caption": "Stay Hungry, My Friends.",
    "image_urls": ["https://example.com/img.png"],
    "idempotency_key": "bv-key",
}


def _make_supabase_mock(
    job_status: str = "queued",
    telegram_chat_id: int | None = None,
    duplicate_exists: bool = False,
    current_example_count: int = 0,
) -> MagicMock:
    """Build a supabase mock covering all tables used in handle_post_content + brand voice."""

    # posting_jobs table
    posting_jobs_mock = MagicMock()
    posting_jobs_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{"id": "job-brandvoice", "status": job_status}]
    )
    posting_jobs_mock.update.return_value.eq.return_value.execute.return_value = MagicMock()

    # approval_requests table
    approval_mock = MagicMock()
    if telegram_chat_id is not None:
        approval_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"telegram_chat_id": telegram_chat_id}]
        )
    else:
        approval_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )

    # posting_results table
    posting_results_mock = MagicMock()
    posting_results_mock.insert.return_value.execute.return_value = MagicMock(data=[{"id": "r-1"}])

    # few_shot_examples table
    few_shot_mock = MagicMock()

    # Duplicate check: .select().eq().eq().limit().execute()
    dup_data = [{"id": "existing-id"}] if duplicate_exists else []
    few_shot_mock.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
        data=dup_data
    )

    # Insert chain
    few_shot_mock.insert.return_value.execute.return_value = MagicMock(data=[{"id": "new-id"}])

    # Keep-IDs query: .select().eq().order().limit().execute()
    keep_ids = [{"id": f"id-{i}"} for i in range(min(current_example_count, 20))]
    few_shot_mock.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
        data=keep_ids
    )

    # Delete chain for trim
    delete_chain = MagicMock()
    delete_chain.eq.return_value.not_.in_.return_value.execute.return_value = MagicMock()
    few_shot_mock.delete.return_value = delete_chain

    def table_side_effect(name: str) -> MagicMock:
        return {
            "posting_jobs": posting_jobs_mock,
            "approval_requests": approval_mock,
            "posting_results": posting_results_mock,
            "few_shot_examples": few_shot_mock,
        }.get(name, MagicMock())

    supabase_mock = MagicMock()
    supabase_mock.table.side_effect = table_side_effect
    return supabase_mock


class TestBrandVoiceLearning:
    """Feature 7: Brand voice learning on successful posts."""

    @pytest.mark.asyncio
    async def test_successful_post_inserts_few_shot_example(self):
        """After a successful post, a new few_shot_example row is inserted."""
        supabase_mock = _make_supabase_mock(job_status="queued", duplicate_exists=False)
        mock_bot = AsyncMock()
        mock_bot_class = MagicMock(return_value=mock_bot)

        fake_results = [
            PostingResult(platform="facebook", platform_post_id="p1", platform_url=None, success=True),
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

        # few_shot_examples.insert should have been called
        few_shot_table = supabase_mock.table("few_shot_examples")
        few_shot_table.insert.assert_called_once()
        insert_data = few_shot_table.insert.call_args[0][0]
        assert insert_data["caption"] == _BASE_MESSAGE["caption"]
        assert insert_data["tenant_id"] == _BASE_MESSAGE["tenant_id"]
        assert insert_data["engagement_score"] == 1.0
        assert insert_data["content_type"] == "organic"

    @pytest.mark.asyncio
    async def test_duplicate_caption_not_inserted_twice(self):
        """If the same caption already exists, skip insertion."""
        supabase_mock = _make_supabase_mock(job_status="queued", duplicate_exists=True)
        mock_bot = AsyncMock()
        mock_bot_class = MagicMock(return_value=mock_bot)

        fake_results = [
            PostingResult(platform="facebook", platform_post_id="p1", platform_url=None, success=True),
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

        # few_shot_examples.insert should NOT have been called
        few_shot_table = supabase_mock.table("few_shot_examples")
        few_shot_table.insert.assert_not_called()

    @pytest.mark.asyncio
    async def test_failed_post_does_not_insert_few_shot_example(self):
        """If posting fails, no few_shot_example is inserted."""
        supabase_mock = _make_supabase_mock(job_status="queued", duplicate_exists=False)
        mock_bot = AsyncMock()
        mock_bot_class = MagicMock(return_value=mock_bot)

        fake_results = [
            PostingResult(
                platform="facebook",
                platform_post_id=None,
                platform_url=None,
                success=False,
                error_message="timeout",
            ),
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

        few_shot_table = supabase_mock.table("few_shot_examples")
        few_shot_table.insert.assert_not_called()

    @pytest.mark.asyncio
    async def test_after_21_examples_trim_deletes_oldest(self):
        """After inserting the 21st example, delete runs to keep only 20."""
        # 20 existing examples — after insert there will be 21, trim to 20
        supabase_mock = _make_supabase_mock(
            job_status="queued",
            duplicate_exists=False,
            current_example_count=20,
        )
        mock_bot = AsyncMock()
        mock_bot_class = MagicMock(return_value=mock_bot)

        fake_results = [
            PostingResult(platform="facebook", platform_post_id="p1", platform_url=None, success=True),
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

        # Trim delete should have been called (few_shot_examples.delete())
        few_shot_table = supabase_mock.table("few_shot_examples")
        few_shot_table.insert.assert_called_once()  # Insert happened
        few_shot_table.delete.assert_called_once()  # Trim delete also ran
