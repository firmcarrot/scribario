"""Tests for video detection in bot.handlers.intake module."""

from __future__ import annotations

import pytest

from bot.handlers.intake import detect_video_request, parse_video_aspect_ratio


class TestDetectVideoRequest:
    """Tests for video keyword detection."""

    def test_detects_video_keyword(self):
        assert detect_video_request("make a video about our sauce") is True

    def test_detects_reel_keyword(self):
        assert detect_video_request("create a reel for Instagram") is True

    def test_detects_clip_keyword(self):
        assert detect_video_request("make a short clip of our product") is True

    def test_detects_animate_keyword(self):
        assert detect_video_request("animate our logo reveal") is True

    def test_detects_case_insensitive(self):
        assert detect_video_request("Make a VIDEO about shrimp") is True

    def test_no_video_keywords(self):
        assert detect_video_request("post about our weekend special") is False

    def test_empty_string(self):
        assert detect_video_request("") is False

    def test_detects_reel_in_sentence(self):
        assert detect_video_request("I want a quick reel showing our sauce") is True

    def test_does_not_false_positive_on_review(self):
        """'review' contains 'revi' not 'reel', should not match."""
        assert detect_video_request("post a review of our sauce") is False

    def test_detects_motion_keyword(self):
        assert detect_video_request("make a motion graphic of our logo") is True


class TestParseVideoAspectRatio:
    """Tests for video aspect ratio detection."""

    def test_reel_returns_vertical(self):
        assert parse_video_aspect_ratio("make a reel about our sauce") == "9:16"

    def test_story_returns_vertical(self):
        assert parse_video_aspect_ratio("create a story for Instagram") == "9:16"

    def test_tiktok_returns_vertical(self):
        assert parse_video_aspect_ratio("make a tiktok video") == "9:16"

    def test_shorts_returns_vertical(self):
        assert parse_video_aspect_ratio("make a YouTube shorts clip") == "9:16"

    def test_default_is_landscape(self):
        assert parse_video_aspect_ratio("make a video about our sauce") == "16:9"

    def test_empty_string_returns_landscape(self):
        assert parse_video_aspect_ratio("") == "16:9"

    def test_case_insensitive(self):
        assert parse_video_aspect_ratio("Make a REEL") == "9:16"
