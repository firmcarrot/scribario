"""Worker — pgmq consumer and job dispatcher.

Polls the job queue and dispatches to the appropriate handler.
Respects MAX_WORKER_CONCURRENCY to prevent API cost explosion.
"""

from __future__ import annotations

import asyncio
import logging
import signal
from typing import Any

from datetime import UTC, datetime

from bot.config import get_settings

logger = logging.getLogger(__name__)

# Job type → handler mapping (registered at startup)
JOB_HANDLERS: dict[str, Any] = {}


def register_handler(job_type: str, handler: Any) -> None:
    """Register a job handler for a given job type."""
    JOB_HANDLERS[job_type] = handler
    logger.info("Registered handler", extra={"job_type": job_type})


class Worker:
    """Background worker that polls pgmq and dispatches jobs."""

    def __init__(
        self,
        max_concurrency: int | None = None,
        poll_interval: int | None = None,
    ) -> None:
        self._max_concurrency = max_concurrency or get_settings().max_worker_concurrency
        self._poll_interval = poll_interval or get_settings().worker_poll_interval_seconds
        self._semaphore = asyncio.Semaphore(self._max_concurrency)
        self._running = True
        self._active_tasks: set[asyncio.Task] = set()  # type: ignore[type-arg]

    def stop(self) -> None:
        """Signal the worker to stop after current jobs complete."""
        self._running = False
        logger.info("Worker stop requested")

    async def poll_once(self) -> dict | None:
        """Poll job_queue table for one queued job.

        Uses the fallback job_queue table with status-based locking.
        Atomically claims the job by setting status='processing' and locked_by.
        """
        from bot.db import get_supabase_client

        try:
            client = get_supabase_client()

            # Find and claim one queued job
            result = (
                client.table("job_queue")
                .select("*")
                .eq("status", "queued")
                .lte("scheduled_for", datetime.now(UTC).isoformat())
                .order("created_at")
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            job = result.data[0]
            job_id = job["id"]

            # Claim the job (optimistic — if another worker claimed it, the update returns empty)
            claim_result = (
                client.table("job_queue")
                .update({"status": "processing", "locked_by": f"worker-{id(self)}"})
                .eq("id", job_id)
                .eq("status", "queued")  # Only claim if still queued
                .execute()
            )

            if not claim_result.data:
                return None  # Another worker claimed it

            claimed = claim_result.data[0]
            payload = claimed.get("payload", {})
            payload["id"] = job_id
            payload["type"] = claimed["job_type"]
            payload["_queue_id"] = job_id  # For marking complete/failed later
            return payload

        except Exception:
            logger.exception("Error polling job queue")
            return None

    async def _mark_job_complete(self, queue_id: str) -> None:
        """Mark a job as completed in the queue."""
        from bot.db import get_supabase_client
        try:
            client = get_supabase_client()
            client.table("job_queue").update({
                "status": "completed",
                "completed_at": "now()",
            }).eq("id", queue_id).execute()
        except Exception:
            logger.exception("Failed to mark job complete", extra={"queue_id": queue_id})

    async def _mark_job_failed(self, queue_id: str, error: str) -> None:
        """Mark a job as failed, or re-queue if retries remain."""
        from bot.db import get_supabase_client
        try:
            client = get_supabase_client()
            # Get current retry count
            result = client.table("job_queue").select("retry_count, max_retries").eq("id", queue_id).execute()
            if result.data:
                job = result.data[0]
                if job["retry_count"] < job["max_retries"]:
                    # Re-queue with incremented retry count
                    client.table("job_queue").update({
                        "status": "queued",
                        "retry_count": job["retry_count"] + 1,
                        "locked_by": None,
                        "error_message": error,
                    }).eq("id", queue_id).execute()
                else:
                    # Max retries exceeded — mark as dead
                    client.table("job_queue").update({
                        "status": "dead",
                        "failed_at": "now()",
                        "error_message": error,
                    }).eq("id", queue_id).execute()
                    logger.critical(
                        "DEAD LETTER: Job exceeded max retries",
                        extra={
                            "queue_id": queue_id,
                            "retry_count": job["retry_count"],
                            "max_retries": job["max_retries"],
                            "error": error[:200],
                        },
                    )
        except Exception:
            logger.exception("Failed to mark job failed", extra={"queue_id": queue_id})

    async def _process_job(self, message: dict) -> None:
        """Process a single job with concurrency limiting."""
        async with self._semaphore:
            job_type = message.get("type", "unknown")
            job_id = message.get("id", "unknown")
            queue_id = message.get("_queue_id", job_id)

            handler = JOB_HANDLERS.get(job_type)
            if not handler:
                logger.error("No handler for job type", extra={"job_type": job_type})
                return

            try:
                logger.info("Processing job", extra={"job_id": job_id, "type": job_type})
                await handler(message)
                logger.info("Job completed", extra={"job_id": job_id, "type": job_type})
                await self._mark_job_complete(queue_id)
            except Exception as e:
                logger.exception("Job failed", extra={"job_id": job_id, "type": job_type})
                await self._mark_job_failed(queue_id, str(e))

    async def run(self) -> None:
        """Main worker loop — poll, dispatch, repeat."""
        logger.info(
            "Worker started",
            extra={
                "max_concurrency": self._max_concurrency,
                "poll_interval": self._poll_interval,
            },
        )

        while self._running:
            message = await self.poll_once()
            if message:
                task = asyncio.create_task(self._process_job(message))
                self._active_tasks.add(task)
                task.add_done_callback(self._active_tasks.discard)
            else:
                await asyncio.sleep(self._poll_interval)

        # Wait for active tasks to complete on shutdown
        if self._active_tasks:
            logger.info("Waiting for active tasks to complete", extra={"count": len(self._active_tasks)})
            await asyncio.gather(*self._active_tasks, return_exceptions=True)

        logger.info("Worker stopped")


async def main() -> None:
    """Entry point for the worker process."""
    logging.basicConfig(level=logging.INFO)

    # Register job handlers
    from worker.jobs.generate_caption import handle_generate_caption
    from worker.jobs.generate_content import handle_generate_content
    from worker.jobs.generate_image import handle_generate_image
    from worker.jobs.post_content import handle_post_content
    from worker.jobs.regen_image import handle_regen_image_job
    from worker.jobs.generate_video import handle_generate_video
    from worker.jobs.autopilot_dispatch import handle_autopilot_dispatch
    from worker.jobs.autopilot_generate import handle_autopilot_generate
    from worker.jobs.autopilot_timeout import handle_autopilot_timeout
    from worker.jobs.autopilot_digest import handle_autopilot_digest

    register_handler("generate_content", handle_generate_content)
    register_handler("generate_caption", handle_generate_caption)
    register_handler("generate_image", handle_generate_image)
    register_handler("post_content", handle_post_content)
    register_handler("regen_image", handle_regen_image_job)
    register_handler("generate_video", handle_generate_video)
    register_handler("autopilot_dispatch", handle_autopilot_dispatch)
    register_handler("autopilot_generate", handle_autopilot_generate)
    register_handler("autopilot_timeout", handle_autopilot_timeout)
    register_handler("autopilot_digest", handle_autopilot_digest)
    # generate_long_video handler removed — long video is deprecated

    worker = Worker()

    # Graceful shutdown on SIGTERM/SIGINT
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.stop)

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
