"""Tests for pipeline.learning.preference_engine module."""

from __future__ import annotations

import pytest


# --- Fake Supabase helpers ---


class FakeSupabaseTable:
    def __init__(self, data: list | None = None):
        self._data = data or []
        self._inserted: dict | None = None
        self._updated: dict | None = None

    def select(self, *a: object, **kw: object) -> FakeSupabaseTable:
        return self

    def eq(self, *a: object, **kw: object) -> FakeSupabaseTable:
        return self

    def gte(self, *a: object, **kw: object) -> FakeSupabaseTable:
        return self

    @property
    def not_(self) -> FakeSupabaseTable:
        return self

    def is_(self, *a: object, **kw: object) -> FakeSupabaseTable:
        return self

    def order(self, *a: object, **kw: object) -> FakeSupabaseTable:
        return self

    def limit(self, *a: object, **kw: object) -> FakeSupabaseTable:
        return self

    def insert(self, data: dict) -> FakeSupabaseTable:
        self._inserted = data
        return self

    def update(self, data: dict) -> FakeSupabaseTable:
        self._updated = data
        return self

    def in_(self, *a: object, **kw: object) -> FakeSupabaseTable:
        return self

    def execute(self) -> object:
        data = self._data

        class R:
            pass

        r = R()
        r.data = data  # type: ignore[attr-defined]
        r.count = len(data)  # type: ignore[attr-defined]
        return r


class FakeSupabaseClient:
    def __init__(self, tables: dict[str, FakeSupabaseTable] | None = None):
        self._tables = tables or {}

    def table(self, name: str) -> FakeSupabaseTable:
        return self._tables.get(name, FakeSupabaseTable())


# --- Tests ---


class TestAccumulateApprovalSignals:
    @pytest.mark.asyncio
    async def test_first_approval_creates_new_signal(self, monkeypatch: pytest.MonkeyPatch):
        pref_table = FakeSupabaseTable(data=[])  # no existing
        client = FakeSupabaseClient(tables={"preference_signals": pref_table})
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.preference_engine import accumulate_approval_signals

        chosen = {"text": "Short caption!", "formula": "punchy_one_liner"}
        rejected_1 = {"text": "A " * 50 + "long text.", "formula": "hook_story_offer"}
        rejected_2 = {"text": "B " * 50 + "long text.", "formula": "story_lesson"}

        await accumulate_approval_signals("tenant-1", 0, [chosen, rejected_1, rejected_2])

        assert pref_table._inserted is not None
        assert pref_table._inserted["occurrences"] == 1
        assert pref_table._inserted["total_opportunities"] == 1
        assert pref_table._inserted["signal_type"] == "approval_structural"

    @pytest.mark.asyncio
    async def test_second_approval_increments(self, monkeypatch: pytest.MonkeyPatch):
        existing_row = {
            "id": "sig-1",
            "occurrences": 1,
            "total_opportunities": 1,
        }
        pref_table = FakeSupabaseTable(data=[existing_row])
        client = FakeSupabaseClient(tables={"preference_signals": pref_table})
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.preference_engine import accumulate_approval_signals

        chosen = {"text": "Short!", "formula": "punchy_one_liner"}
        rejected = {"text": "A " * 50 + "long.", "formula": "hook_story_offer"}

        await accumulate_approval_signals("tenant-1", 0, [chosen, rejected])

        assert pref_table._updated is not None
        assert pref_table._updated["occurrences"] == 2
        assert pref_table._updated["total_opportunities"] == 2

    @pytest.mark.asyncio
    async def test_non_discriminating_features_not_stored(self, monkeypatch: pytest.MonkeyPatch):
        pref_table = FakeSupabaseTable(data=[])
        client = FakeSupabaseClient(tables={"preference_signals": pref_table})
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.preference_engine import accumulate_approval_signals

        # Same formula, same word count bucket, same everything
        cap = {"text": "Hello world today!", "formula": "hook_story_offer"}
        await accumulate_approval_signals("tenant-1", 0, [cap, cap, cap])

        # Nothing discriminating -> nothing inserted
        assert pref_table._inserted is None


class TestAccumulateEditSignal:
    @pytest.mark.asyncio
    async def test_first_edit_creates_signal_at_05(self, monkeypatch: pytest.MonkeyPatch):
        pref_table = FakeSupabaseTable(data=[])
        client = FakeSupabaseClient(tables={"preference_signals": pref_table})
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.preference_engine import accumulate_edit_signal

        await accumulate_edit_signal("tenant-1", "tone", "casual", "Use casual tone")

        assert pref_table._inserted is not None
        assert pref_table._inserted["confidence"] == 0.5
        assert pref_table._inserted["signal_type"] == "edit_pattern"
        assert pref_table._inserted["lesson_text"] == "Use casual tone"

    @pytest.mark.asyncio
    async def test_second_edit_raises_confidence_to_075(self, monkeypatch: pytest.MonkeyPatch):
        existing = {
            "id": "sig-2",
            "occurrences": 1,
            "total_opportunities": 1,
            "lesson_text": "Use casual tone",
        }
        pref_table = FakeSupabaseTable(data=[existing])
        client = FakeSupabaseClient(tables={"preference_signals": pref_table})
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.preference_engine import accumulate_edit_signal

        await accumulate_edit_signal("tenant-1", "tone", "casual", "Use casual tone always")

        assert pref_table._updated is not None
        assert pref_table._updated["occurrences"] == 2
        # confidence = min(0.5 + (2-1)*0.25, 1.0) = 0.75
        assert pref_table._updated["confidence"] == 0.75

    @pytest.mark.asyncio
    async def test_lesson_text_stored(self, monkeypatch: pytest.MonkeyPatch):
        pref_table = FakeSupabaseTable(data=[])
        client = FakeSupabaseClient(tables={"preference_signals": pref_table})
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.preference_engine import accumulate_edit_signal

        await accumulate_edit_signal("t", "emoji", "no_emoji", "Never use emoji")

        assert pref_table._inserted["lesson_text"] == "Never use emoji"

    @pytest.mark.asyncio
    async def test_confidence_caps_at_1(self, monkeypatch: pytest.MonkeyPatch):
        existing = {
            "id": "sig-3",
            "occurrences": 5,
            "total_opportunities": 5,
            "lesson_text": None,
        }
        pref_table = FakeSupabaseTable(data=[existing])
        client = FakeSupabaseClient(tables={"preference_signals": pref_table})
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.preference_engine import accumulate_edit_signal

        await accumulate_edit_signal("t", "tone", "casual")

        # confidence = min(0.5 + (6-1)*0.25, 1.0) = min(1.75, 1.0) = 1.0
        assert pref_table._updated["confidence"] == 1.0


class TestLoadPreferenceSignals:
    @pytest.mark.asyncio
    async def test_filters_by_opportunity_thresholds(self, monkeypatch: pytest.MonkeyPatch):
        rows = [
            {
                "signal_type": "approval_structural",
                "total_opportunities": 10,
                "confidence": 0.8,
            },
            {
                "signal_type": "approval_structural",
                "total_opportunities": 3,  # below 8 threshold
                "confidence": 0.9,
            },
            {
                "signal_type": "edit_pattern",
                "total_opportunities": 2,
                "confidence": 0.5,
            },
            {
                "signal_type": "edit_pattern",
                "total_opportunities": 1,  # below 2 threshold
                "confidence": 0.5,
            },
        ]
        pref_table = FakeSupabaseTable(data=rows)
        client = FakeSupabaseClient(tables={"preference_signals": pref_table})
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.preference_engine import load_preference_signals

        result = await load_preference_signals("tenant-1")
        assert len(result) == 2
        assert result[0]["total_opportunities"] == 10
        assert result[1]["total_opportunities"] == 2

    @pytest.mark.asyncio
    async def test_returns_empty_on_exception(self, monkeypatch: pytest.MonkeyPatch):
        def boom() -> None:
            raise RuntimeError("db down")

        monkeypatch.setattr("bot.db.get_supabase_client", boom)

        from pipeline.learning.preference_engine import load_preference_signals

        result = await load_preference_signals("tenant-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_engagement_signals_require_5_opportunities(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        rows = [
            {"signal_type": "engagement", "total_opportunities": 5, "confidence": 0.7},
            {"signal_type": "engagement", "total_opportunities": 4, "confidence": 0.8},
        ]
        pref_table = FakeSupabaseTable(data=rows)
        client = FakeSupabaseClient(tables={"preference_signals": pref_table})
        monkeypatch.setattr("bot.db.get_supabase_client", lambda: client)

        from pipeline.learning.preference_engine import load_preference_signals

        result = await load_preference_signals("tenant-1")
        assert len(result) == 1
        assert result[0]["total_opportunities"] == 5
