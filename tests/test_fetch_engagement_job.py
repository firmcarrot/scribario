"""Tests for worker.jobs.fetch_engagement — engagement polling job handler."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worker.jobs.fetch_engagement import handle_fetch_engagement


class TestHandleFetchEngagement:
    @pytest.mark.asyncio
    async def test_skips_when_no_posting_results(self):
        """No posts with platform_post_id → nothing to fetch."""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.not_.is_.return_value.gte.return_value.execute.return_value.data = []

        with patch("worker.jobs.fetch_engagement.get_supabase_client", return_value=mock_client):
            await handle_fetch_engagement({})

    @pytest.mark.asyncio
    async def test_fetches_and_upserts_engagement(self):
        """Happy path: fetch engagement, upsert metrics, update few-shot score."""
        mock_client = MagicMock()

        # posting_results query returns one post
        posting_results_chain = mock_client.table.return_value.select.return_value
        posting_results_chain.eq.return_value.not_.is_.return_value.gte.return_value.execute.return_value.data = [
            {
                "id": "pr-1",
                "platform_post_id": "postiz-abc",
                "platform": "facebook",
                "posting_job_id": "pj-1",
                "tenant_id": "t-1",
                "posted_at": "2026-03-01T00:00:00Z",
            }
        ]

        # posting_jobs lookup for draft_id
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
            {"draft_id": "d-1"}
        ]

        # engagement_metrics upsert
        mock_client.table.return_value.upsert.return_value.execute.return_value.data = [{}]

        # few_shot_examples update
        mock_client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        mock_engagement = AsyncMock(return_value=MagicMock(
            likes=10, comments=3, shares=1, views=500,
        ))

        with (
            patch("worker.jobs.fetch_engagement.get_supabase_client", return_value=mock_client),
            patch("worker.jobs.fetch_engagement.fetch_post_engagement", mock_engagement),
        ):
            await handle_fetch_engagement({})

        mock_engagement.assert_called_once_with(postiz_id="postiz-abc")

    @pytest.mark.asyncio
    async def test_continues_on_single_post_failure(self):
        """If one post's engagement fetch fails, continue to next."""
        mock_client = MagicMock()

        posting_results_chain = mock_client.table.return_value.select.return_value
        posting_results_chain.eq.return_value.not_.is_.return_value.gte.return_value.execute.return_value.data = [
            {
                "id": "pr-1",
                "platform_post_id": "postiz-abc",
                "platform": "facebook",
                "posting_job_id": "pj-1",
                "tenant_id": "t-1",
                "posted_at": "2026-03-01T00:00:00Z",
            },
            {
                "id": "pr-2",
                "platform_post_id": "postiz-def",
                "platform": "instagram",
                "posting_job_id": "pj-2",
                "tenant_id": "t-1",
                "posted_at": "2026-03-01T00:00:00Z",
            },
        ]

        # Return None for first (failed), data for second
        mock_engagement = AsyncMock(side_effect=[
            None,
            MagicMock(likes=5, comments=1, shares=0, views=200),
        ])

        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
            {"draft_id": "d-1"}
        ]
        mock_client.table.return_value.upsert.return_value.execute.return_value.data = [{}]
        mock_client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        with (
            patch("worker.jobs.fetch_engagement.get_supabase_client", return_value=mock_client),
            patch("worker.jobs.fetch_engagement.fetch_post_engagement", mock_engagement),
        ):
            # Should not raise
            await handle_fetch_engagement({})

        assert mock_engagement.call_count == 2
