"""Autopilot dispatcher — the single cron-triggered job that fans out per-tenant work.

Runs every 5 minutes via pg_cron. Queries autopilot_configs for tenants
whose next_run_at <= now() and are not paused, then enqueues an
autopilot_generate job for each.
"""

from __future__ import annotations

import logging

from bot.db import advance_next_run_at, enqueue_job, get_due_autopilot_tenants

logger = logging.getLogger(__name__)


async def handle_autopilot_dispatch(message: dict) -> None:
    """Dispatch autopilot generation jobs for all due tenants."""
    due_tenants = await get_due_autopilot_tenants()

    if not due_tenants:
        logger.debug("No tenants due for autopilot generation")
        return

    logger.info("Dispatching autopilot jobs", extra={"count": len(due_tenants)})

    for config in due_tenants:
        tenant_id = config["tenant_id"]
        try:
            await enqueue_job(
                queue_name="content_generation",
                job_type="autopilot_generate",
                payload={"tenant_id": tenant_id},
                idempotency_key=f"autopilot_generate:{tenant_id}:{config.get('next_run_at', '')}",
            )
            await advance_next_run_at(tenant_id)
            logger.info("Dispatched autopilot_generate", extra={"tenant_id": tenant_id})
        except Exception:
            logger.exception(
                "Failed to dispatch for tenant",
                extra={"tenant_id": tenant_id},
            )
