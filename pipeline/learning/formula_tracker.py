from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FormulaStats:
    formula: str
    approval_count: int
    total_count: int
    approval_rate: float
    avg_engagement: float | None
    edit_count: int
    sample_size: int


async def get_formula_stats(tenant_id: str) -> dict[str, FormulaStats]:
    """Aggregate formula performance from feedback_events + few_shot_examples.

    Only reports formulas with sample_size >= 5.
    """
    from bot.db import get_supabase_client

    try:
        client = get_supabase_client()

        # Get all feedback events with formulas for this tenant
        feedback_result = (
            client.table("feedback_events")
            .select("action, chosen_formula")
            .eq("tenant_id", tenant_id)
            .not_.is_("chosen_formula", "null")
            .execute()
        )

        # Count approvals and edits per formula
        formula_approvals: dict[str, int] = {}
        formula_totals: dict[str, int] = {}
        formula_edits: dict[str, int] = {}

        for row in feedback_result.data or []:
            formula = row.get("chosen_formula")
            if not formula:
                continue
            formula_totals[formula] = formula_totals.get(formula, 0) + 1
            action = row.get("action", "")
            if action in ("approve", "approve_video"):
                formula_approvals[formula] = formula_approvals.get(formula, 0) + 1
            elif action == "edit":
                formula_edits[formula] = formula_edits.get(formula, 0) + 1

        # Get engagement scores per formula from few_shot_examples
        examples_result = (
            client.table("few_shot_examples")
            .select("formula, engagement_score")
            .eq("tenant_id", tenant_id)
            .not_.is_("formula", "null")
            .execute()
        )

        formula_engagement: dict[str, list[float]] = {}
        for row in examples_result.data or []:
            formula = row.get("formula")
            score = row.get("engagement_score")
            if formula and score is not None:
                formula_engagement.setdefault(formula, []).append(score)

        # Build stats, filtering for sample_size >= 5
        all_formulas = set(formula_totals.keys()) | set(formula_engagement.keys())
        stats: dict[str, FormulaStats] = {}

        for formula in all_formulas:
            total = formula_totals.get(formula, 0)
            approvals = formula_approvals.get(formula, 0)
            edits = formula_edits.get(formula, 0)
            engagements = formula_engagement.get(formula, [])
            # Use feedback_events total as primary sample_size (few_shot_examples
            # overlaps with approved feedback_events, so adding both double-counts)
            sample_size = max(total, len(engagements))

            if sample_size < 5:
                continue

            avg_engagement = round(sum(engagements) / len(engagements), 1) if engagements else None
            approval_rate = round(approvals / total, 2) if total > 0 else 0.0

            stats[formula] = FormulaStats(
                formula=formula,
                approval_count=approvals,
                total_count=total,
                approval_rate=approval_rate,
                avg_engagement=avg_engagement,
                edit_count=edits,
                sample_size=sample_size,
            )

        return stats
    except Exception:
        logger.exception("Failed to get formula stats", extra={"tenant_id": tenant_id})
        return {}
