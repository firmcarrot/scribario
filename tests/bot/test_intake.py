"""Tests for bot.handlers.intake module."""

from __future__ import annotations

import pytest

from bot.handlers.intake import parse_platform_targets


class TestParsePlatformTargets:
    """Tests for platform mention detection."""

    def test_returns_none_when_no_platforms_mentioned(self):
        assert parse_platform_targets("Post something about our new sauce") is None

    def test_returns_none_for_empty_string(self):
        assert parse_platform_targets("") is None

    def test_detects_lowercase_facebook(self):
        result = parse_platform_targets("post this to facebook")
        assert result is not None
        assert "facebook" in result

    def test_detects_titlecase_facebook(self):
        result = parse_platform_targets("Share on Facebook please")
        assert result is not None
        assert "facebook" in result

    def test_detects_lowercase_instagram(self):
        result = parse_platform_targets("post to instagram")
        assert result is not None
        assert "instagram" in result

    def test_detects_titlecase_instagram(self):
        result = parse_platform_targets("Instagram post about our sauce")
        assert result is not None
        assert "instagram" in result

    def test_detects_lowercase_linkedin(self):
        result = parse_platform_targets("share on linkedin")
        assert result is not None
        assert "linkedin" in result

    def test_detects_titlecase_linkedin(self):
        result = parse_platform_targets("Post to LinkedIn")
        assert result is not None
        assert "linkedin" in result

    def test_detects_lowercase_twitter(self):
        result = parse_platform_targets("tweet on twitter")
        assert result is not None
        assert "twitter" in result

    def test_detects_titlecase_twitter(self):
        result = parse_platform_targets("Post on Twitter")
        assert result is not None
        assert "twitter" in result

    def test_detects_x_as_twitter(self):
        result = parse_platform_targets("post on X")
        assert result is not None
        assert "twitter" in result

    def test_detects_lowercase_tiktok(self):
        result = parse_platform_targets("make a tiktok video")
        assert result is not None
        assert "tiktok" in result

    def test_detects_titlecase_tiktok(self):
        result = parse_platform_targets("post on TikTok")
        assert result is not None
        assert "tiktok" in result

    def test_detects_multiple_platforms(self):
        result = parse_platform_targets("post to facebook and instagram")
        assert result is not None
        assert "facebook" in result
        assert "instagram" in result

    def test_returns_deduplicated_list(self):
        result = parse_platform_targets("post to facebook and Facebook")
        assert result is not None
        assert result.count("facebook") == 1

    def test_does_not_return_empty_list(self):
        """None is returned, not an empty list, when no platforms mentioned."""
        result = parse_platform_targets("a sauce for chicken wings")
        assert result is None

    def test_three_platforms_detected(self):
        result = parse_platform_targets("post to instagram, facebook, and LinkedIn")
        assert result is not None
        assert "instagram" in result
        assert "facebook" in result
        assert "linkedin" in result
        assert len(result) == 3

    def test_no_false_positive_on_unrelated_words(self):
        """Words that contain platform names but aren't them should not match."""
        # "instagramming" — only exact word-boundary matches wanted
        result = parse_platform_targets("I was just browsing")
        assert result is None
