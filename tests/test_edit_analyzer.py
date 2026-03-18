"""Tests for pipeline.learning.edit_analyzer module."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from unittest.mock import AsyncMock

import pytest


@dataclass
class FakeContentBlock:
    text: str


@dataclass
class FakeResponse:
    content: list[FakeContentBlock]


class TestAnalyzeEdit:
    @pytest.mark.asyncio
    async def test_calls_accumulate_with_parsed_json(self, monkeypatch: pytest.MonkeyPatch):
        haiku_response = FakeResponse(
            content=[
                FakeContentBlock(
                    text=json.dumps(
                        {"feature": "tone", "value": "casual", "lesson": "Use casual tone"}
                    )
                )
            ]
        )

        mock_create = AsyncMock(return_value=haiku_response)

        class FakeAnthropic:
            def __init__(self, **kw: object):
                pass

            class messages:
                create = mock_create

        monkeypatch.setattr("pipeline.learning.edit_analyzer.anthropic.AsyncAnthropic", FakeAnthropic)

        # Mock settings
        class FakeSettings:
            anthropic_api_key = "test-key"

        monkeypatch.setattr("pipeline.learning.edit_analyzer.get_settings", lambda: FakeSettings())

        # Track accumulate_edit_signal calls
        captured: list[dict] = []

        async def fake_accumulate(**kwargs: object) -> None:
            captured.append(kwargs)

        async def fake_accumulate_fn(
            tenant_id: str, feature: str, value: str, lesson_text: str | None = None
        ) -> None:
            captured.append(
                {
                    "tenant_id": tenant_id,
                    "feature": feature,
                    "value": value,
                    "lesson_text": lesson_text,
                }
            )

        monkeypatch.setattr(
            "pipeline.learning.preference_engine.accumulate_edit_signal", fake_accumulate_fn
        )

        # Mock log_usage_event
        from bot import db as _db_mod
        monkeypatch.setattr(_db_mod, "log_usage_event", AsyncMock())

        from pipeline.learning.edit_analyzer import analyze_edit

        await analyze_edit("tenant-1", "Original text", "Make it casual", "Casual text")

        assert len(captured) == 1
        assert captured[0]["feature"] == "tone"
        assert captured[0]["value"] == "casual"
        assert captured[0]["lesson_text"] == "Use casual tone"

    @pytest.mark.asyncio
    async def test_handles_markdown_code_block(self, monkeypatch: pytest.MonkeyPatch):
        json_str = json.dumps({"feature": "emoji", "value": "no_emoji", "lesson": "Remove emoji"})
        haiku_response = FakeResponse(
            content=[FakeContentBlock(text=f"```json\n{json_str}\n```")]
        )

        mock_create = AsyncMock(return_value=haiku_response)

        class FakeAnthropic:
            def __init__(self, **kw: object):
                pass

            class messages:
                create = mock_create

        monkeypatch.setattr("pipeline.learning.edit_analyzer.anthropic.AsyncAnthropic", FakeAnthropic)

        class FakeSettings:
            anthropic_api_key = "test-key"

        monkeypatch.setattr("pipeline.learning.edit_analyzer.get_settings", lambda: FakeSettings())

        captured: list[dict] = []

        async def fake_accumulate_fn(
            tenant_id: str, feature: str, value: str, lesson_text: str | None = None
        ) -> None:
            captured.append({"feature": feature, "value": value})

        monkeypatch.setattr(
            "pipeline.learning.preference_engine.accumulate_edit_signal", fake_accumulate_fn
        )
        from bot import db as _db_mod
        monkeypatch.setattr(_db_mod, "log_usage_event", AsyncMock())

        from pipeline.learning.edit_analyzer import analyze_edit

        await analyze_edit("t", "orig", "instr", "edited")

        assert len(captured) == 1
        assert captured[0]["feature"] == "emoji"

    @pytest.mark.asyncio
    async def test_handles_malformed_json_gracefully(self, monkeypatch: pytest.MonkeyPatch):
        haiku_response = FakeResponse(
            content=[FakeContentBlock(text="not valid json at all")]
        )

        mock_create = AsyncMock(return_value=haiku_response)

        class FakeAnthropic:
            def __init__(self, **kw: object):
                pass

            class messages:
                create = mock_create

        monkeypatch.setattr("pipeline.learning.edit_analyzer.anthropic.AsyncAnthropic", FakeAnthropic)

        class FakeSettings:
            anthropic_api_key = "test-key"

        monkeypatch.setattr("pipeline.learning.edit_analyzer.get_settings", lambda: FakeSettings())

        from pipeline.learning.edit_analyzer import analyze_edit

        # Should NOT raise
        await analyze_edit("t", "orig", "instr", "edited")

    @pytest.mark.asyncio
    async def test_handles_empty_response_content(self, monkeypatch: pytest.MonkeyPatch):
        haiku_response = FakeResponse(content=[FakeContentBlock(text="")])

        mock_create = AsyncMock(return_value=haiku_response)

        class FakeAnthropic:
            def __init__(self, **kw: object):
                pass

            class messages:
                create = mock_create

        monkeypatch.setattr("pipeline.learning.edit_analyzer.anthropic.AsyncAnthropic", FakeAnthropic)

        class FakeSettings:
            anthropic_api_key = "test-key"

        monkeypatch.setattr("pipeline.learning.edit_analyzer.get_settings", lambda: FakeSettings())

        from pipeline.learning.edit_analyzer import analyze_edit

        # Should not raise
        await analyze_edit("t", "orig", "instr", "edited")

    @pytest.mark.asyncio
    async def test_api_exception_does_not_propagate(self, monkeypatch: pytest.MonkeyPatch):
        mock_create = AsyncMock(side_effect=RuntimeError("API down"))

        class FakeAnthropic:
            def __init__(self, **kw: object):
                pass

            class messages:
                create = mock_create

        monkeypatch.setattr("pipeline.learning.edit_analyzer.anthropic.AsyncAnthropic", FakeAnthropic)

        class FakeSettings:
            anthropic_api_key = "test-key"

        monkeypatch.setattr("pipeline.learning.edit_analyzer.get_settings", lambda: FakeSettings())

        from pipeline.learning.edit_analyzer import analyze_edit

        # Should NOT raise
        await analyze_edit("t", "orig", "instr", "edited")


class TestFireAndForgetEditAnalysis:
    @pytest.mark.asyncio
    async def test_creates_task_without_blocking(self, monkeypatch: pytest.MonkeyPatch):
        called = False

        async def fake_analyze(*args: object) -> None:
            nonlocal called
            called = True

        monkeypatch.setattr(
            "pipeline.learning.edit_analyzer.analyze_edit", fake_analyze
        )

        from pipeline.learning.edit_analyzer import fire_and_forget_edit_analysis

        fire_and_forget_edit_analysis("t", "orig", "instr", "edited")

        # Let the event loop run the task
        await asyncio.sleep(0.01)
        assert called is True

    @pytest.mark.asyncio
    async def test_no_event_loop_does_not_crash(self, monkeypatch: pytest.MonkeyPatch):
        # Simulate no running event loop by making get_running_loop raise
        monkeypatch.setattr(
            "pipeline.learning.edit_analyzer.asyncio.get_running_loop",
            lambda: (_ for _ in ()).throw(RuntimeError("no loop")),
        )

        from pipeline.learning.edit_analyzer import fire_and_forget_edit_analysis

        # Should not raise
        fire_and_forget_edit_analysis("t", "orig", "instr", "edited")

    @pytest.mark.asyncio
    async def test_task_exception_is_suppressed(self, monkeypatch: pytest.MonkeyPatch):
        async def failing_analyze(*args: object) -> None:
            raise ValueError("boom")

        monkeypatch.setattr(
            "pipeline.learning.edit_analyzer.analyze_edit", failing_analyze
        )

        from pipeline.learning.edit_analyzer import fire_and_forget_edit_analysis

        fire_and_forget_edit_analysis("t", "orig", "instr", "edited")

        # Let the task run and fail
        await asyncio.sleep(0.01)
        # No unhandled exception = success
