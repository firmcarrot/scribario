"""Tests for pipeline.learning.formula_tracker module."""

from __future__ import annotations

import pytest


class FakeSupabaseTable:
    def __init__(self, data: list | None = None):
        self._data = data or []

    def select(self, *a: object, **kw: object) -> FakeSupabaseTable:
        return self

    def eq(self, *a: object, **kw: object) -> FakeSupabaseTable:
        return self

    @property
    def not_(self) -> FakeSupabaseTable:
        return self

    def is_(self, *a: object, **kw: object) -> FakeSupabaseTable:
        return self

    def execute(self) -> object:
        data = self._data

        class R:
            pass

        r = R()
        r.data = data  # type: ignore[attr-defined]
        return r


class FakeSupabaseClient:
    def __init__(self, tables: dict[str, FakeSupabaseTable] | None = None):
        self._tables = tables or {}

    def table(self, name: str) -> FakeSupabaseTable:
        return self._tables.get(name, FakeSupabaseTable())


class TestGetFormulaStats:
    @pytest.mark.asyncio
    async def test_returns_formulas_with_sample_gte_5(self, monkeypatch: pytest.MonkeyPatch):
        feedback_data = [
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            {"action": "edit", "chosen_formula": "hook_story_offer"},
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            # 5 total for hook_story_offer
            {"action": "approve", "chosen_formula": "punchy_one_liner"},
            {"action": "approve", "chosen_formula": "punchy_one_liner"},
            # only 2 for punchy_one_liner
        ]
        examples_data: list[dict] = []

        client = FakeSupabaseClient(
            tables={
                "feedback_events": FakeSupabaseTable(feedback_data),
                "few_shot_examples": FakeSupabaseTable(examples_data),
            }
        )
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.formula_tracker import get_formula_stats

        stats = await get_formula_stats("tenant-1")
        assert "hook_story_offer" in stats
        assert "punchy_one_liner" not in stats  # sample_size=2 < 5

    @pytest.mark.asyncio
    async def test_correctly_calculates_approval_rate(self, monkeypatch: pytest.MonkeyPatch):
        feedback_data = [
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            {"action": "edit", "chosen_formula": "hook_story_offer"},
            {"action": "edit", "chosen_formula": "hook_story_offer"},
        ]
        client = FakeSupabaseClient(
            tables={
                "feedback_events": FakeSupabaseTable(feedback_data),
                "few_shot_examples": FakeSupabaseTable([]),
            }
        )
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.formula_tracker import get_formula_stats

        stats = await get_formula_stats("t")
        fs = stats["hook_story_offer"]
        assert fs.approval_rate == 0.6  # 3/5
        assert fs.approval_count == 3
        assert fs.total_count == 5
        assert fs.edit_count == 2

    @pytest.mark.asyncio
    async def test_avg_engagement_from_examples(self, monkeypatch: pytest.MonkeyPatch):
        feedback_data = [
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            {"action": "approve", "chosen_formula": "hook_story_offer"},
            {"action": "approve", "chosen_formula": "hook_story_offer"},
        ]
        examples_data = [
            {"formula": "hook_story_offer", "engagement_score": 7.0},
            {"formula": "hook_story_offer", "engagement_score": 9.0},
        ]
        client = FakeSupabaseClient(
            tables={
                "feedback_events": FakeSupabaseTable(feedback_data),
                "few_shot_examples": FakeSupabaseTable(examples_data),
            }
        )
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.formula_tracker import get_formula_stats

        stats = await get_formula_stats("t")
        fs = stats["hook_story_offer"]
        assert fs.avg_engagement == 8.0  # (7+9)/2
        assert fs.sample_size == 5  # max(5 feedback, 2 examples)

    @pytest.mark.asyncio
    async def test_no_engagement_returns_none(self, monkeypatch: pytest.MonkeyPatch):
        feedback_data = [
            {"action": "approve", "chosen_formula": "hook_story_offer"},
        ] * 5
        client = FakeSupabaseClient(
            tables={
                "feedback_events": FakeSupabaseTable(feedback_data),
                "few_shot_examples": FakeSupabaseTable([]),
            }
        )
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.formula_tracker import get_formula_stats

        stats = await get_formula_stats("t")
        assert stats["hook_story_offer"].avg_engagement is None

    @pytest.mark.asyncio
    async def test_returns_empty_on_exception(self, monkeypatch: pytest.MonkeyPatch):
        def boom() -> None:
            raise RuntimeError("db down")

        monkeypatch.setattr("bot.db.get_supabase_client", boom)

        from pipeline.learning.formula_tracker import get_formula_stats

        stats = await get_formula_stats("t")
        assert stats == {}

    @pytest.mark.asyncio
    async def test_approve_video_counts_as_approval(self, monkeypatch: pytest.MonkeyPatch):
        feedback_data = [
            {"action": "approve_video", "chosen_formula": "story_lesson"},
        ] * 5
        client = FakeSupabaseClient(
            tables={
                "feedback_events": FakeSupabaseTable(feedback_data),
                "few_shot_examples": FakeSupabaseTable([]),
            }
        )
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.formula_tracker import get_formula_stats

        stats = await get_formula_stats("t")
        assert stats["story_lesson"].approval_count == 5
        assert stats["story_lesson"].approval_rate == 1.0

    @pytest.mark.asyncio
    async def test_null_formula_rows_ignored(self, monkeypatch: pytest.MonkeyPatch):
        feedback_data = [
            {"action": "approve", "chosen_formula": None},
            {"action": "approve", "chosen_formula": ""},
            {"action": "approve", "chosen_formula": "hook_story_offer"},
        ] * 5
        client = FakeSupabaseClient(
            tables={
                "feedback_events": FakeSupabaseTable(feedback_data),
                "few_shot_examples": FakeSupabaseTable([]),
            }
        )
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.formula_tracker import get_formula_stats

        stats = await get_formula_stats("t")
        assert "hook_story_offer" in stats
        assert "" not in stats

    @pytest.mark.asyncio
    async def test_engagement_only_formula_included(self, monkeypatch: pytest.MonkeyPatch):
        """Formula appears only in few_shot_examples, not feedback_events."""
        examples_data = [
            {"formula": "list_value_drop", "engagement_score": 6.0},
            {"formula": "list_value_drop", "engagement_score": 7.0},
            {"formula": "list_value_drop", "engagement_score": 8.0},
            {"formula": "list_value_drop", "engagement_score": 5.0},
            {"formula": "list_value_drop", "engagement_score": 9.0},
        ]
        client = FakeSupabaseClient(
            tables={
                "feedback_events": FakeSupabaseTable([]),
                "few_shot_examples": FakeSupabaseTable(examples_data),
            }
        )
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.formula_tracker import get_formula_stats

        stats = await get_formula_stats("t")
        assert "list_value_drop" in stats
        assert stats["list_value_drop"].approval_rate == 0.0
        assert stats["list_value_drop"].avg_engagement == 7.0
