"""Worker — pgmq consumer and job dispatcher.

Polls the job queue and dispatches to the appropriate handler.
Respects MAX_WORKER_CONCURRENCY to prevent API cost explosion.
"""

from __future__ import annotations

import asyncio
import logging
import signal
from typing import Any

from bot.config import settings

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
        self._max_concurrency = max_concurrency or settings.max_worker_concurrency
        self._poll_interval = poll_interval or settings.worker_poll_interval_seconds
        self._semaphore = asyncio.Semaphore(self._max_concurrency)
        self._running = True
        self._active_tasks: set[asyncio.Task] = set()  # type: ignore[type-arg]

    def stop(self) -> None:
        """Signal the worker to stop after current jobs complete."""
        self._running = False
        logger.info("Worker stop requested")

    async def poll_once(self) -> dict | None:
        """Poll pgmq for one message.

        TODO: Wire up actual pgmq via Supabase client.
        Fallback: SELECT ... FROM jobs WHERE status='queued'
                  ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1
        """
        # Placeholder — will be replaced with real pgmq or fallback query
        return None

    async def _process_job(self, message: dict) -> None:
        """Process a single job with concurrency limiting."""
        async with self._semaphore:
            job_type = message.get("type", "unknown")
            job_id = message.get("id", "unknown")

            handler = JOB_HANDLERS.get(job_type)
            if not handler:
                logger.error("No handler for job type", extra={"job_type": job_type})
                return

            try:
                logger.info("Processing job", extra={"job_id": job_id, "type": job_type})
                await handler(message)
                logger.info("Job completed", extra={"job_id": job_id, "type": job_type})
                # TODO: Delete message from pgmq / mark job as completed
            except Exception:
                logger.exception("Job failed", extra={"job_id": job_id, "type": job_type})
                # TODO: Increment retry count, re-enqueue or mark as failed

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
    from worker.jobs.generate_image import handle_generate_image
    from worker.jobs.post_content import handle_post_content

    register_handler("generate_caption", handle_generate_caption)
    register_handler("generate_image", handle_generate_image)
    register_handler("post_content", handle_post_content)

    worker = Worker()

    # Graceful shutdown on SIGTERM/SIGINT
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.stop)

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
