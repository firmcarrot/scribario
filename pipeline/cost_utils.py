"""Centralized Anthropic pricing -- single place to update when models change."""

from __future__ import annotations

ANTHROPIC_PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.0},
}


def compute_anthropic_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Compute USD cost from token counts. Falls back to Sonnet pricing for unknown models."""
    pricing = ANTHROPIC_PRICING.get(model, {"input": 3.0, "output": 15.0})
    return (input_tokens * pricing["input"] / 1_000_000) + (
        output_tokens * pricing["output"] / 1_000_000
    )
