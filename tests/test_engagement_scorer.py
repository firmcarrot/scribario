"""Tests for pipeline.learning.engagement_scorer module."""

from __future__ import annotations

from pipeline.learning.engagement_scorer import compute_engagement_score


class TestComputeEngagementScore:
    def test_normal_case(self):
        # raw = (10*1 + 5*3 + 2*5) / 1000 * 1000 = 35.0, capped at 10.0
        score = compute_engagement_score(likes=10, comments=5, shares=2, views=1000)
        assert score == 10.0

    def test_normal_moderate_engagement(self):
        # raw = (10*1 + 2*3 + 0*5) / 5000 * 1000 = 16/5000*1000 = 3.2
        score = compute_engagement_score(likes=10, comments=2, shares=0, views=5000)
        assert score == 3.2

    def test_zero_views_falls_back_to_raw_count(self):
        # raw = 10 + 5*3 + 2*5 = 10 + 15 + 10 = 35 => 35/10 = 3.5
        score = compute_engagement_score(likes=10, comments=5, shares=2, views=0)
        assert score == 3.5

    def test_negative_views_falls_back_to_raw_count(self):
        score = compute_engagement_score(likes=5, comments=0, shares=0, views=-1)
        # raw = 5 + 0 + 0 = 5 => 5/10 = 0.5
        assert score == 0.5

    def test_high_engagement_caps_at_10(self):
        # Huge numbers -> cap
        score = compute_engagement_score(likes=10000, comments=5000, shares=2000, views=100)
        assert score == 10.0

    def test_all_zeros_returns_zero(self):
        score = compute_engagement_score(likes=0, comments=0, shares=0, views=0)
        assert score == 0.0

    def test_shares_weighted_highest(self):
        # shares only: (0 + 0 + 1*5) / 1000 * 1000 = 5.0
        score_shares = compute_engagement_score(likes=0, comments=0, shares=1, views=1000)
        # likes only: (1 + 0 + 0) / 1000 * 1000 = 1.0
        score_likes = compute_engagement_score(likes=1, comments=0, shares=0, views=1000)
        assert score_shares > score_likes

    def test_comments_weighted_middle(self):
        score_comments = compute_engagement_score(likes=0, comments=1, shares=0, views=1000)
        score_likes = compute_engagement_score(likes=1, comments=0, shares=0, views=1000)
        assert score_comments > score_likes

    def test_rounding(self):
        # (3*1 + 1*3 + 0*5) / 700 * 1000 = 6000/700 = 8.571...
        score = compute_engagement_score(likes=3, comments=1, shares=0, views=700)
        assert score == 8.6  # rounded to 1 decimal

    def test_zero_views_with_all_zeros(self):
        score = compute_engagement_score(likes=0, comments=0, shares=0, views=0)
        assert score == 0.0

    def test_zero_views_caps_at_10(self):
        # raw = 0 + 100*3 + 100*5 = 800 => 800/10 = 80 => min(80, 10) = 10
        score = compute_engagement_score(likes=0, comments=100, shares=100, views=0)
        assert score == 10.0
