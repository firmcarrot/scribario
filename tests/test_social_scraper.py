"""Tests for pipeline.social_scraper — social media content scraping for few-shot examples."""

from __future__ import annotations

import asyncio

import pytest

from pipeline.social_scraper import FewShotCandidate, build_few_shot_from_social, scrape_social_profile


class TestFewShotCandidateModel:
    def test_has_required_fields(self):
        candidate = FewShotCandidate(
            platform="instagram",
            content_type="post",
            caption="Check out our new sauce! #hotsauce",
            image_url="https://example.com/img.jpg",
        )
        assert candidate.platform == "instagram"
        assert candidate.content_type == "post"
        assert "sauce" in candidate.caption
        assert candidate.image_url is not None

    def test_optional_fields(self):
        candidate = FewShotCandidate(
            platform="facebook",
            content_type="post",
            caption="Hello world",
        )
        assert candidate.image_url is None
        assert candidate.engagement_score is None

    def test_engagement_score(self):
        candidate = FewShotCandidate(
            platform="instagram",
            content_type="reel",
            caption="Spicy!",
            engagement_score=4.5,
        )
        assert candidate.engagement_score == 4.5


class TestScrapeSocialProfile:
    def test_is_async(self):
        assert asyncio.iscoroutinefunction(scrape_social_profile)

    def test_accepts_platform_and_handle(self):
        import inspect
        sig = inspect.signature(scrape_social_profile)
        params = list(sig.parameters.keys())
        assert "platform" in params
        assert "handle" in params


class TestBuildFewShotFromSocial:
    """Test conversion from scraped social data to few-shot examples."""

    def test_is_async(self):
        assert asyncio.iscoroutinefunction(build_few_shot_from_social)

    def test_accepts_social_links(self):
        import inspect
        sig = inspect.signature(build_few_shot_from_social)
        params = list(sig.parameters.keys())
        assert "social_links" in params


class TestExtractHandleFromUrl:
    def test_extracts_instagram_handle(self):
        from pipeline.social_scraper import _extract_handle_from_url

        handle = _extract_handle_from_url("instagram", "https://www.instagram.com/mondoshrimp/")
        assert handle == "mondoshrimp"

    def test_extracts_facebook_handle(self):
        from pipeline.social_scraper import _extract_handle_from_url

        handle = _extract_handle_from_url("facebook", "https://www.facebook.com/MondoShrimp")
        assert handle == "MondoShrimp"

    def test_extracts_tiktok_handle(self):
        from pipeline.social_scraper import _extract_handle_from_url

        handle = _extract_handle_from_url("tiktok", "https://www.tiktok.com/@hotsaucebrand")
        assert handle == "hotsaucebrand"

    def test_extracts_x_handle(self):
        from pipeline.social_scraper import _extract_handle_from_url

        handle = _extract_handle_from_url("x", "https://x.com/mondoshrimp")
        assert handle == "mondoshrimp"

    def test_handles_trailing_slash(self):
        from pipeline.social_scraper import _extract_handle_from_url

        handle = _extract_handle_from_url("instagram", "https://instagram.com/brand/")
        assert handle == "brand"

    def test_returns_none_for_invalid(self):
        from pipeline.social_scraper import _extract_handle_from_url

        handle = _extract_handle_from_url("instagram", "https://google.com")
        assert handle is None
