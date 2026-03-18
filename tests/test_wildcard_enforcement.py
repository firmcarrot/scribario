"""Tests for _build_formula_performance_block() in pipeline.prompt_engine.engine."""

from __future__ import annotations

import pytest

from pipeline.learning.formula_tracker import FormulaStats


class TestBuildFormulaPerformanceBlock:
    @pytest.mark.asyncio
    async def test_wildcard_not_in_top_2(self, monkeypatch: pytest.MonkeyPatch):
        stats = {
            "hook_story_offer": FormulaStats(
                formula="hook_story_offer",
                approval_count=8,
                total_count=10,
                approval_rate=0.8,
                avg_engagement=8.5,
                edit_count=2,
                sample_size=10,
            ),
            "problem_agitate_solution": FormulaStats(
                formula="problem_agitate_solution",
                approval_count=6,
                total_count=8,
                approval_rate=0.75,
                avg_engagement=7.0,
                edit_count=2,
                sample_size=8,
            ),
            "punchy_one_liner": FormulaStats(
                formula="punchy_one_liner",
                approval_count=3,
                total_count=6,
                approval_rate=0.5,
                avg_engagement=5.0,
                edit_count=3,
                sample_size=6,
            ),
        }

        monkeypatch.setattr(
            "pipeline.learning.formula_tracker.get_formula_stats",
            _async_return(stats),
        )

        from pipeline.prompt_engine.engine import _build_formula_performance_block

        block, assignments = await _build_formula_performance_block("tenant-1")

        assert assignments is not None
        assert len(assignments) == 3
        # Top 2 should be the ones with best engagement
        assert assignments[0] == "hook_story_offer"
        assert assignments[1] == "problem_agitate_solution"
        # Wildcard must NOT be in top 2
        assert assignments[2] not in assignments[:2]

    @pytest.mark.asyncio
    async def test_empty_stats_returns_empty(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "pipeline.learning.formula_tracker.get_formula_stats",
            _async_return({}),
        )

        from pipeline.prompt_engine.engine import _build_formula_performance_block

        block, assignments = await _build_formula_performance_block("tenant-1")
        assert block == ""
        assert assignments is None

    @pytest.mark.asyncio
    async def test_only_1_formula_no_assignments(self, monkeypatch: pytest.MonkeyPatch):
        stats = {
            "hook_story_offer": FormulaStats(
                formula="hook_story_offer",
                approval_count=5,
                total_count=5,
                approval_rate=1.0,
                avg_engagement=9.0,
                edit_count=0,
                sample_size=5,
            ),
        }

        monkeypatch.setattr(
            "pipeline.learning.formula_tracker.get_formula_stats",
            _async_return(stats),
        )

        from pipeline.prompt_engine.engine import _build_formula_performance_block

        block, assignments = await _build_formula_performance_block("tenant-1")
        assert "hook_story_offer" in block
        assert assignments is None  # need 2+ top formulas

    @pytest.mark.asyncio
    async def test_block_contains_formula_names(self, monkeypatch: pytest.MonkeyPatch):
        stats = {
            "hook_story_offer": FormulaStats(
                formula="hook_story_offer",
                approval_count=8,
                total_count=10,
                approval_rate=0.8,
                avg_engagement=8.5,
                edit_count=2,
                sample_size=10,
            ),
            "story_lesson": FormulaStats(
                formula="story_lesson",
                approval_count=6,
                total_count=8,
                approval_rate=0.75,
                avg_engagement=7.0,
                edit_count=2,
                sample_size=8,
            ),
        }
        monkeypatch.setattr(
            "pipeline.learning.formula_tracker.get_formula_stats",
            _async_return(stats),
        )

        from pipeline.prompt_engine.engine import _build_formula_performance_block

        block, _assignments = await _build_formula_performance_block("t")
        assert "hook_story_offer" in block
        assert "story_lesson" in block
        assert "Formula Performance" in block

    @pytest.mark.asyncio
    async def test_block_shows_engagement_and_approval(self, monkeypatch: pytest.MonkeyPatch):
        stats = {
            "hook_story_offer": FormulaStats(
                formula="hook_story_offer",
                approval_count=8,
                total_count=10,
                approval_rate=0.8,
                avg_engagement=8.5,
                edit_count=2,
                sample_size=10,
            ),
            "punchy_one_liner": FormulaStats(
                formula="punchy_one_liner",
                approval_count=4,
                total_count=8,
                approval_rate=0.5,
                avg_engagement=5.0,
                edit_count=4,
                sample_size=8,
            ),
        }
        monkeypatch.setattr(
            "pipeline.learning.formula_tracker.get_formula_stats",
            _async_return(stats),
        )

        from pipeline.prompt_engine.engine import _build_formula_performance_block

        block, _assignments = await _build_formula_performance_block("t")
        assert "8.5/10" in block
        assert "80%" in block

    @pytest.mark.asyncio
    async def test_no_engagement_shows_na(self, monkeypatch: pytest.MonkeyPatch):
        stats = {
            "hook_story_offer": FormulaStats(
                formula="hook_story_offer",
                approval_count=5,
                total_count=5,
                approval_rate=1.0,
                avg_engagement=None,
                edit_count=0,
                sample_size=5,
            ),
            "story_lesson": FormulaStats(
                formula="story_lesson",
                approval_count=4,
                total_count=5,
                approval_rate=0.8,
                avg_engagement=None,
                edit_count=1,
                sample_size=5,
            ),
        }
        monkeypatch.setattr(
            "pipeline.learning.formula_tracker.get_formula_stats",
            _async_return(stats),
        )

        from pipeline.prompt_engine.engine import _build_formula_performance_block

        block, _assignments = await _build_formula_performance_block("t")
        assert "n/a" in block

    @pytest.mark.asyncio
    async def test_wildcard_label_in_block(self, monkeypatch: pytest.MonkeyPatch):
        stats = {
            "hook_story_offer": FormulaStats(
                formula="hook_story_offer",
                approval_count=8,
                total_count=10,
                approval_rate=0.8,
                avg_engagement=8.5,
                edit_count=2,
                sample_size=10,
            ),
            "story_lesson": FormulaStats(
                formula="story_lesson",
                approval_count=6,
                total_count=8,
                approval_rate=0.75,
                avg_engagement=7.0,
                edit_count=2,
                sample_size=8,
            ),
        }
        monkeypatch.setattr(
            "pipeline.learning.formula_tracker.get_formula_stats",
            _async_return(stats),
        )

        from pipeline.prompt_engine.engine import _build_formula_performance_block

        block, assignments = await _build_formula_performance_block("t")
        assert "WILDCARD" in block
        assert assignments is not None

    @pytest.mark.asyncio
    async def test_exception_returns_empty(self, monkeypatch: pytest.MonkeyPatch):
        async def boom(*a: object, **kw: object) -> dict:
            raise RuntimeError("db down")

        monkeypatch.setattr(
            "pipeline.learning.formula_tracker.get_formula_stats",
            boom,
        )

        from pipeline.prompt_engine.engine import _build_formula_performance_block

        block, assignments = await _build_formula_performance_block("t")
        assert block == ""
        assert assignments is None

    @pytest.mark.asyncio
    async def test_sorted_by_engagement_then_approval(self, monkeypatch: pytest.MonkeyPatch):
        stats = {
            "low_eng": FormulaStats(
                formula="low_eng",
                approval_count=9,
                total_count=10,
                approval_rate=0.9,
                avg_engagement=2.0,
                edit_count=1,
                sample_size=10,
            ),
            "high_eng": FormulaStats(
                formula="high_eng",
                approval_count=5,
                total_count=10,
                approval_rate=0.5,
                avg_engagement=9.0,
                edit_count=5,
                sample_size=10,
            ),
        }
        monkeypatch.setattr(
            "pipeline.learning.formula_tracker.get_formula_stats",
            _async_return(stats),
        )

        from pipeline.prompt_engine.engine import _build_formula_performance_block

        block, assignments = await _build_formula_performance_block("t")
        # high_eng should be first (higher engagement)
        assert assignments is not None
        assert assignments[0] == "high_eng"
        assert assignments[1] == "low_eng"


# --- Helpers ---


def _async_return(value: object):
    """Create an async function that returns value."""

    async def _fn(*args: object, **kwargs: object):  # noqa: ANN202
        return value

    return _fn
