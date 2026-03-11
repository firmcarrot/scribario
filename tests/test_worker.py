"""Tests for worker.main module."""

from __future__ import annotations

import asyncio

import pytest

from worker.main import JOB_HANDLERS, Worker, register_handler


@pytest.fixture(autouse=True)
def _clear_handlers():
    """Clear registered handlers between tests."""
    JOB_HANDLERS.clear()
    yield
    JOB_HANDLERS.clear()


class TestRegisterHandler:
    def test_registers_handler(self):
        async def my_handler(msg: dict) -> None:
            pass

        register_handler("test_job", my_handler)
        assert "test_job" in JOB_HANDLERS
        assert JOB_HANDLERS["test_job"] is my_handler

    def test_overwrites_existing(self):
        async def handler1(msg: dict) -> None:
            pass

        async def handler2(msg: dict) -> None:
            pass

        register_handler("test_job", handler1)
        register_handler("test_job", handler2)
        assert JOB_HANDLERS["test_job"] is handler2


class TestWorker:
    @pytest.mark.asyncio
    async def test_stop_terminates_loop(self):
        worker = Worker(max_concurrency=1, poll_interval=1)

        async def stop_after_delay():
            await asyncio.sleep(0.1)
            worker.stop()

        asyncio.create_task(stop_after_delay())
        await worker.run()
        # If we get here, the worker stopped correctly
        assert not worker._running

    @pytest.mark.asyncio
    async def test_processes_job_with_handler(self):
        results: list[dict] = []

        async def capture_handler(msg: dict) -> None:
            results.append(msg)

        register_handler("test_type", capture_handler)

        worker = Worker(max_concurrency=1, poll_interval=1)

        # Override poll_once to return one message then None
        call_count = 0

        async def mock_poll() -> dict | None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"id": "job-1", "type": "test_type", "data": "hello"}
            worker.stop()
            return None

        worker.poll_once = mock_poll  # type: ignore[assignment]
        await worker.run()

        assert len(results) == 1
        assert results[0]["data"] == "hello"

    @pytest.mark.asyncio
    async def test_respects_concurrency_limit(self):
        active_count = 0
        max_seen = 0

        async def slow_handler(msg: dict) -> None:
            nonlocal active_count, max_seen
            active_count += 1
            max_seen = max(max_seen, active_count)
            await asyncio.sleep(0.05)
            active_count -= 1

        register_handler("slow", slow_handler)

        worker = Worker(max_concurrency=2, poll_interval=0)

        call_count = 0

        async def mock_poll() -> dict | None:
            nonlocal call_count
            call_count += 1
            if call_count <= 5:
                return {"id": f"job-{call_count}", "type": "slow"}
            await asyncio.sleep(0.2)
            worker.stop()
            return None

        worker.poll_once = mock_poll  # type: ignore[assignment]
        await worker.run()

        # Concurrency should never exceed 2
        assert max_seen <= 2
