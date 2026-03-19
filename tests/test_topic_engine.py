"""Tests for pipeline.topic_engine — AI topic generation + moderation."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from pipeline.topic_engine import (
    generate_topic,
    moderate_content,
    _is_too_similar,
)


class TestGenerateTopic:
    """Test topic generation."""

    @pytest.fixture
    def mock_brand_profile(self):
        return {
            "tenant_id": "test-tenant",
            "name": "Test Brand",
            "tone_words": ["friendly", "professional"],
            "audience_description": "Small business owners",
            "product_catalog": {"products": [{"name": "Widget", "description": "A great widget"}]},
        }

    @pytest.fixture
    def content_mix(self):
        return {
            "promotional": 40,
            "educational": 30,
            "entertaining": 20,
            "behind_the_scenes": 10,
        }

    @pytest.mark.asyncio
    async def test_generate_topic_returns_topic_and_category(
        self, mock_brand_profile, content_mix
    ):
        with patch("pipeline.topic_engine._call_claude") as mock_claude:
            mock_claude.return_value = {
                "topic": "5 ways our Widget saves you time",
                "category": "educational",
            }
            result = await generate_topic(
                tenant_id="test-tenant",
                content_mix=content_mix,
                brand_profile=mock_brand_profile,
                recent_topics=[],
            )
            assert "topic" in result
            assert "category" in result
            assert result["category"] in content_mix

    @pytest.mark.asyncio
    async def test_generate_topic_rejects_duplicate(
        self, mock_brand_profile, content_mix
    ):
        """Topic too similar to recent ones should be retried."""
        with patch("pipeline.topic_engine._call_claude") as mock_claude:
            # First call returns duplicate, second returns unique
            mock_claude.side_effect = [
                {"topic": "5 ways Widget saves time", "category": "educational"},
                {"topic": "Behind the scenes at our factory", "category": "behind_the_scenes"},
            ]
            result = await generate_topic(
                tenant_id="test-tenant",
                content_mix=content_mix,
                brand_profile=mock_brand_profile,
                recent_topics=["5 ways our Widget saves you time"],
                max_retries=2,
            )
            assert result["topic"] == "Behind the scenes at our factory"


class TestModerateContent:
    """Test content moderation for Full Autopilot."""

    @pytest.mark.asyncio
    async def test_moderate_passes_clean_content(self):
        with patch("pipeline.topic_engine._call_claude_moderation") as mock_mod:
            mock_mod.return_value = {"safe": True, "reason": ""}
            result = await moderate_content("Check out our amazing new product!")
            assert result["safe"] is True

    @pytest.mark.asyncio
    async def test_moderate_flags_offensive_content(self):
        with patch("pipeline.topic_engine._call_claude_moderation") as mock_mod:
            mock_mod.return_value = {"safe": False, "reason": "potentially offensive"}
            result = await moderate_content("some bad content")
            assert result["safe"] is False
            assert result["reason"]


class TestSimilarity:
    """Test topic deduplication."""

    def test_identical_topics_are_similar(self):
        assert _is_too_similar("Widget saves time", ["Widget saves time"]) is True

    def test_very_different_topics_are_not_similar(self):
        assert _is_too_similar(
            "Behind the scenes at our factory",
            ["5 ways Widget saves you time"],
        ) is False

    def test_minor_variation_is_similar(self):
        assert _is_too_similar(
            "5 ways our Widget saves time",
            ["5 ways Widget saves you time"],
        ) is True

    def test_empty_recent_topics(self):
        assert _is_too_similar("Any topic", []) is False
