"""Tests for pipeline.cost_utils — centralized Anthropic pricing."""

from pipeline.cost_utils import compute_anthropic_cost


class TestComputeAnthropicCost:
    def test_sonnet_pricing(self):
        # 1000 input tokens @ $3/M + 500 output tokens @ $15/M
        cost = compute_anthropic_cost("claude-sonnet-4-20250514", 1000, 500)
        expected = (1000 * 3.0 / 1_000_000) + (500 * 15.0 / 1_000_000)
        assert cost == expected

    def test_haiku_pricing(self):
        # 1000 input tokens @ $0.80/M + 500 output tokens @ $4/M
        cost = compute_anthropic_cost("claude-haiku-4-5-20251001", 1000, 500)
        expected = (1000 * 0.80 / 1_000_000) + (500 * 4.0 / 1_000_000)
        assert cost == expected

    def test_unknown_model_falls_back_to_sonnet(self):
        cost = compute_anthropic_cost("claude-future-model-9000", 1000, 500)
        sonnet_cost = compute_anthropic_cost("claude-sonnet-4-20250514", 1000, 500)
        assert cost == sonnet_cost

    def test_zero_tokens_returns_zero(self):
        assert compute_anthropic_cost("claude-sonnet-4-20250514", 0, 0) == 0.0
