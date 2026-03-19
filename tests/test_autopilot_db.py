"""Tests for autopilot database functions — verifies signatures and structure."""

from __future__ import annotations

import asyncio

from bot.db import (
    get_autopilot_config,
    upsert_autopilot_config,
    pause_autopilot,
    resume_autopilot,
    create_autopilot_topic,
    update_autopilot_topic_status,
    get_due_autopilot_tenants,
    get_expired_smart_queue_topics,
    count_tenant_posts_today,
    count_tenant_posts_this_week,
    get_tenant_monthly_cost,
    create_autopilot_run,
    update_autopilot_run,
    get_autopilot_weekly_summary,
    advance_next_run_at,
)


class TestAutopilotDbSignatures:
    """Verify all autopilot DB functions exist and are async."""

    def test_get_autopilot_config_is_async(self):
        assert asyncio.iscoroutinefunction(get_autopilot_config)

    def test_upsert_autopilot_config_is_async(self):
        assert asyncio.iscoroutinefunction(upsert_autopilot_config)

    def test_pause_autopilot_is_async(self):
        assert asyncio.iscoroutinefunction(pause_autopilot)

    def test_resume_autopilot_is_async(self):
        assert asyncio.iscoroutinefunction(resume_autopilot)

    def test_create_autopilot_topic_is_async(self):
        assert asyncio.iscoroutinefunction(create_autopilot_topic)

    def test_update_autopilot_topic_status_is_async(self):
        assert asyncio.iscoroutinefunction(update_autopilot_topic_status)

    def test_get_due_autopilot_tenants_is_async(self):
        assert asyncio.iscoroutinefunction(get_due_autopilot_tenants)

    def test_get_expired_smart_queue_topics_is_async(self):
        assert asyncio.iscoroutinefunction(get_expired_smart_queue_topics)

    def test_count_tenant_posts_today_is_async(self):
        assert asyncio.iscoroutinefunction(count_tenant_posts_today)

    def test_count_tenant_posts_this_week_is_async(self):
        assert asyncio.iscoroutinefunction(count_tenant_posts_this_week)

    def test_get_tenant_monthly_cost_is_async(self):
        assert asyncio.iscoroutinefunction(get_tenant_monthly_cost)

    def test_create_autopilot_run_is_async(self):
        assert asyncio.iscoroutinefunction(create_autopilot_run)

    def test_update_autopilot_run_is_async(self):
        assert asyncio.iscoroutinefunction(update_autopilot_run)

    def test_get_autopilot_weekly_summary_is_async(self):
        assert asyncio.iscoroutinefunction(get_autopilot_weekly_summary)

    def test_advance_next_run_at_is_async(self):
        assert asyncio.iscoroutinefunction(advance_next_run_at)
