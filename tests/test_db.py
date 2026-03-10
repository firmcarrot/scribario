"""Tests for bot.db module — verifies function signatures and data structures."""

from __future__ import annotations

import pytest

from bot.db import (
    create_content_request,
    create_feedback_event,
    enqueue_job,
    get_tenant_by_telegram_user,
    update_draft_status,
)


class TestDbFunctionSignatures:
    """Verify db functions have correct signatures (without hitting real DB)."""

    def test_get_tenant_by_telegram_user_is_async(self):
        import asyncio
        assert asyncio.iscoroutinefunction(get_tenant_by_telegram_user)

    def test_create_content_request_is_async(self):
        import asyncio
        assert asyncio.iscoroutinefunction(create_content_request)

    def test_update_draft_status_is_async(self):
        import asyncio
        assert asyncio.iscoroutinefunction(update_draft_status)

    def test_create_feedback_event_is_async(self):
        import asyncio
        assert asyncio.iscoroutinefunction(create_feedback_event)

    def test_enqueue_job_is_async(self):
        import asyncio
        assert asyncio.iscoroutinefunction(enqueue_job)
