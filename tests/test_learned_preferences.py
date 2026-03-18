"""Tests for load_learned_preferences() and load_edit_lessons() in pipeline.brand_voice."""

from __future__ import annotations

import pytest


class TestLoadLearnedPreferences:
    @pytest.mark.asyncio
    async def test_hard_rules_from_edit_signals(self, monkeypatch: pytest.MonkeyPatch):
        signals = [
            {
                "signal_type": "edit_pattern",
                "feature": "tone",
                "value": "casual",
                "confidence": 0.75,
                "occurrences": 3,
                "total_opportunities": 3,
                "lesson_text": "Always use casual tone",
            },
        ]
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return(signals),
        )

        from pipeline.brand_voice import load_learned_preferences

        result = await load_learned_preferences("tenant-1")
        assert "HARD RULES" in result
        assert "Always use casual tone" in result
        assert "3 times" in result

    @pytest.mark.asyncio
    async def test_soft_preferences_from_approval_signals(self, monkeypatch: pytest.MonkeyPatch):
        signals = [
            {
                "signal_type": "approval_structural",
                "feature": "word_count_bucket",
                "value": "short",
                "confidence": 0.8,
                "occurrences": 8,
                "total_opportunities": 10,
                "lesson_text": None,
            },
        ]
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return(signals),
        )

        from pipeline.brand_voice import load_learned_preferences

        result = await load_learned_preferences("tenant-1")
        assert "SOFT PREFERENCES" in result
        assert "short" in result
        assert "8 of 10" in result

    @pytest.mark.asyncio
    async def test_engagement_signals_as_soft_pref(self, monkeypatch: pytest.MonkeyPatch):
        signals = [
            {
                "signal_type": "engagement",
                "feature": "emoji",
                "value": "has_emoji",
                "confidence": 0.9,
                "occurrences": 10,
                "total_opportunities": 12,
                "lesson_text": None,
            },
        ]
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return(signals),
        )

        from pipeline.brand_voice import load_learned_preferences

        result = await load_learned_preferences("tenant-1")
        assert "SOFT PREFERENCES" in result
        assert "has_emoji" in result
        assert "90%" in result

    @pytest.mark.asyncio
    async def test_empty_signals_returns_empty_string(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return([]),
        )

        from pipeline.brand_voice import load_learned_preferences

        result = await load_learned_preferences("tenant-1")
        assert result == ""

    @pytest.mark.asyncio
    async def test_variety_reminder_present(self, monkeypatch: pytest.MonkeyPatch):
        signals = [
            {
                "signal_type": "edit_pattern",
                "feature": "tone",
                "value": "casual",
                "confidence": 0.75,
                "occurrences": 2,
                "total_opportunities": 2,
                "lesson_text": "Be casual",
            },
        ]
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return(signals),
        )

        from pipeline.brand_voice import load_learned_preferences

        result = await load_learned_preferences("tenant-1")
        assert "break from these patterns" in result

    @pytest.mark.asyncio
    async def test_edit_signal_without_lesson_uses_feature_value(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        signals = [
            {
                "signal_type": "edit_pattern",
                "feature": "emoji",
                "value": "no_emoji",
                "confidence": 0.5,
                "occurrences": 1,
                "total_opportunities": 1,
                "lesson_text": None,
            },
        ]
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return(signals),
        )

        from pipeline.brand_voice import load_learned_preferences

        result = await load_learned_preferences("tenant-1")
        assert "emoji: no_emoji" in result

    @pytest.mark.asyncio
    async def test_exception_returns_empty_string(self, monkeypatch: pytest.MonkeyPatch):
        async def boom(*a: object, **kw: object) -> list:
            raise RuntimeError("db down")

        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            boom,
        )

        from pipeline.brand_voice import load_learned_preferences

        result = await load_learned_preferences("tenant-1")
        assert result == ""

    @pytest.mark.asyncio
    async def test_singular_time_for_one_occurrence(self, monkeypatch: pytest.MonkeyPatch):
        signals = [
            {
                "signal_type": "edit_pattern",
                "feature": "tone",
                "value": "casual",
                "confidence": 0.5,
                "occurrences": 1,
                "total_opportunities": 1,
                "lesson_text": "Be casual",
            },
        ]
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return(signals),
        )

        from pipeline.brand_voice import load_learned_preferences

        result = await load_learned_preferences("tenant-1")
        assert "1 time)" in result
        assert "1 times)" not in result


class TestLoadEditLessons:
    @pytest.mark.asyncio
    async def test_needs_2_plus_edit_signals(self, monkeypatch: pytest.MonkeyPatch):
        # Only 1 edit signal -> empty
        signals = [
            {
                "signal_type": "edit_pattern",
                "feature": "tone",
                "value": "casual",
                "confidence": 0.5,
                "occurrences": 2,
                "total_opportunities": 2,
                "lesson_text": "Be casual",
            },
        ]
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return(signals),
        )

        from pipeline.brand_voice import load_edit_lessons

        result = await load_edit_lessons("tenant-1")
        assert result == ""

    @pytest.mark.asyncio
    async def test_two_edit_signals_generates_output(self, monkeypatch: pytest.MonkeyPatch):
        signals = [
            {
                "signal_type": "edit_pattern",
                "feature": "tone",
                "value": "casual",
                "confidence": 0.75,
                "occurrences": 3,
                "total_opportunities": 3,
                "lesson_text": "Always be casual",
            },
            {
                "signal_type": "edit_pattern",
                "feature": "emoji",
                "value": "no_emoji",
                "confidence": 0.5,
                "occurrences": 2,
                "total_opportunities": 2,
                "lesson_text": "Never use emoji",
            },
        ]
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return(signals),
        )

        from pipeline.brand_voice import load_edit_lessons

        result = await load_edit_lessons("tenant-1")
        assert "Lessons from your past edits" in result
        assert "Always be casual" in result
        assert "Never use emoji" in result

    @pytest.mark.asyncio
    async def test_filters_to_edit_signals_only(self, monkeypatch: pytest.MonkeyPatch):
        signals = [
            {
                "signal_type": "edit_pattern",
                "feature": "tone",
                "value": "casual",
                "confidence": 0.75,
                "occurrences": 3,
                "total_opportunities": 3,
                "lesson_text": "Be casual",
            },
            {
                "signal_type": "approval_structural",
                "feature": "word_count",
                "value": "short",
                "confidence": 0.8,
                "occurrences": 8,
                "total_opportunities": 10,
                "lesson_text": None,
            },
            {
                "signal_type": "edit_pattern",
                "feature": "emoji",
                "value": "no_emoji",
                "confidence": 0.5,
                "occurrences": 2,
                "total_opportunities": 2,
                "lesson_text": "No emoji",
            },
        ]
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return(signals),
        )

        from pipeline.brand_voice import load_edit_lessons

        result = await load_edit_lessons("tenant-1")
        assert "Be casual" in result
        assert "No emoji" in result
        assert "short" not in result  # approval signal excluded

    @pytest.mark.asyncio
    async def test_no_lesson_text_falls_back_to_feature_value(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        signals = [
            {
                "signal_type": "edit_pattern",
                "feature": "punctuation",
                "value": "no_exclamation",
                "confidence": 0.75,
                "occurrences": 3,
                "total_opportunities": 3,
                "lesson_text": None,
            },
            {
                "signal_type": "edit_pattern",
                "feature": "tone",
                "value": "casual",
                "confidence": 0.5,
                "occurrences": 2,
                "total_opportunities": 2,
                "lesson_text": "Be casual",
            },
        ]
        monkeypatch.setattr(
            "pipeline.learning.preference_engine.load_preference_signals",
            _async_return(signals),
        )

        from pipeline.brand_voice import load_edit_lessons

        result = await load_edit_lessons("tenant-1")
        assert "punctuation: no_exclamation" in result


# --- Helpers ---


def _async_return(value: object):
    """Create an async function that returns value."""

    async def _fn(*args: object, **kwargs: object):  # noqa: ANN202
        return value

    return _fn
