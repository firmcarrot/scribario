"""Tests for autopilot job handlers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAutopilotDispatch:
    """Test the dispatcher job handler."""

    @pytest.mark.asyncio
    async def test_dispatch_enqueues_jobs_for_due_tenants(self):
        from worker.jobs.autopilot_dispatch import handle_autopilot_dispatch

        mock_tenants = [
            {"tenant_id": "t1", "id": "c1"},
            {"tenant_id": "t2", "id": "c2"},
        ]
        with (
            patch("worker.jobs.autopilot_dispatch.get_due_autopilot_tenants", new_callable=AsyncMock, return_value=mock_tenants),
            patch("worker.jobs.autopilot_dispatch.enqueue_job", new_callable=AsyncMock) as mock_enqueue,
            patch("worker.jobs.autopilot_dispatch.advance_next_run_at", new_callable=AsyncMock) as mock_advance,
        ):
            await handle_autopilot_dispatch({})
            assert mock_enqueue.call_count == 2
            assert mock_advance.call_count == 2

    @pytest.mark.asyncio
    async def test_dispatch_skips_when_no_tenants_due(self):
        from worker.jobs.autopilot_dispatch import handle_autopilot_dispatch

        with (
            patch("worker.jobs.autopilot_dispatch.get_due_autopilot_tenants", new_callable=AsyncMock, return_value=[]),
            patch("worker.jobs.autopilot_dispatch.enqueue_job", new_callable=AsyncMock) as mock_enqueue,
        ):
            await handle_autopilot_dispatch({})
            mock_enqueue.assert_not_called()


class TestAutopilotGenerate:
    """Test per-tenant generation job handler."""

    @pytest.mark.asyncio
    async def test_generate_aborts_if_paused(self):
        from worker.jobs.autopilot_generate import handle_autopilot_generate

        config = {"mode": "full_autopilot", "paused_at": "2026-01-01T00:00:00Z", "tenant_id": "t1"}
        with patch("worker.jobs.autopilot_generate.get_autopilot_config", new_callable=AsyncMock, return_value=config):
            # Should return early without error
            await handle_autopilot_generate({"tenant_id": "t1"})

    @pytest.mark.asyncio
    async def test_generate_aborts_if_daily_limit_reached(self):
        from worker.jobs.autopilot_generate import handle_autopilot_generate

        config = {
            "mode": "full_autopilot",
            "paused_at": None,
            "tenant_id": "t1",
            "daily_post_limit": 3,
            "weekly_post_limit": 15,
            "monthly_cost_cap_usd": 50.0,
            "content_mix": {"promotional": 100},
            "warmup_posts_remaining": 0,
            "consecutive_failures": 0,
        }
        with (
            patch("worker.jobs.autopilot_generate.get_autopilot_config", new_callable=AsyncMock, return_value=config),
            patch("worker.jobs.autopilot_generate.count_tenant_posts_today", new_callable=AsyncMock, return_value=3),
            patch("worker.jobs.autopilot_generate.enqueue_job", new_callable=AsyncMock) as mock_enqueue,
        ):
            await handle_autopilot_generate({"tenant_id": "t1"})
            mock_enqueue.assert_not_called()


class TestAutopilotTimeout:
    """Test Smart Queue timeout sweep."""

    @pytest.mark.asyncio
    async def test_timeout_auto_approves_expired_topics(self):
        from worker.jobs.autopilot_timeout import handle_autopilot_timeout

        expired = [
            {"id": "topic1", "draft_id": "d1", "tenant_id": "t1"},
        ]
        mock_draft = {
            "id": "d1",
            "tenant_id": "t1",
            "caption_variants": [{"text": "test caption"}],
            "image_urls": ["img.jpg"],
        }
        with (
            patch("worker.jobs.autopilot_timeout.get_expired_smart_queue_topics", new_callable=AsyncMock, return_value=expired),
            patch("worker.jobs.autopilot_timeout.update_autopilot_topic_status", new_callable=AsyncMock, return_value=True) as mock_update,
            patch("worker.jobs.autopilot_timeout.get_draft", new_callable=AsyncMock, return_value=mock_draft),
            patch("worker.jobs.autopilot_timeout.approve_draft", new_callable=AsyncMock) as mock_approve,
            patch("worker.jobs.autopilot_timeout._send_auto_post_notification", new_callable=AsyncMock),
        ):
            await handle_autopilot_timeout({})
            # Should be called twice: first to claim (previewing->generating), then to mark posted
            assert mock_update.call_count == 2
            mock_approve.assert_called_once()

    @pytest.mark.asyncio
    async def test_timeout_skips_already_rejected(self):
        from worker.jobs.autopilot_timeout import handle_autopilot_timeout

        expired = [
            {"id": "topic1", "draft_id": "d1", "tenant_id": "t1"},
        ]
        with (
            patch("worker.jobs.autopilot_timeout.get_expired_smart_queue_topics", new_callable=AsyncMock, return_value=expired),
            # Claim returns False = user already rejected
            patch("worker.jobs.autopilot_timeout.update_autopilot_topic_status", new_callable=AsyncMock, return_value=False),
            patch("worker.jobs.autopilot_timeout.approve_draft", new_callable=AsyncMock) as mock_approve,
        ):
            await handle_autopilot_timeout({})
            mock_approve.assert_not_called()


class TestApproveRefactor:
    """Test that approve_draft shared function works for both manual and autopilot."""

    @pytest.mark.asyncio
    async def test_approve_draft_creates_posting_job(self):
        from bot.handlers.approval import approve_draft

        mock_draft = {
            "id": "d1",
            "tenant_id": "t1",
            "request_id": "r1",
            "caption_variants": [{"text": "caption 1"}, {"text": "caption 2"}],
            "image_urls": ["img1.jpg", "img2.jpg"],
            "status": "previewing",
        }
        with (
            patch("bot.handlers.approval.get_draft", new_callable=AsyncMock, return_value=mock_draft),
            patch("bot.handlers.approval.update_draft_status", new_callable=AsyncMock),
            patch("bot.handlers.approval.create_feedback_event", new_callable=AsyncMock),
            patch("bot.handlers.approval.create_posting_job", new_callable=AsyncMock, return_value={"id": "job1"}),
            patch("bot.handlers.approval.enqueue_job", new_callable=AsyncMock),
            patch("bot.handlers.approval.get_supabase_client") as mock_client,
            patch("bot.handlers.approval._save_unchosen_to_library", new_callable=AsyncMock),
        ):
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[{"platform_targets": ["facebook"]}])
            mock_client.return_value.table.return_value = mock_table

            result = await approve_draft("d1", option_idx=0, tenant_id="t1")
            assert result is not None
