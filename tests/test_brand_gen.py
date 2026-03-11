"""Tests for pipeline.brand_gen — AI brand profile generation from scraped data."""

from __future__ import annotations

import asyncio
import json

import pytest

from pipeline.brand_gen import GeneratedBrandProfile, build_brand_prompt, generate_brand_profile


class TestGeneratedBrandProfileModel:
    """Verify the GeneratedBrandProfile data model."""

    def test_has_required_fields(self):
        profile = GeneratedBrandProfile(
            name="Mondo Shrimp",
            tone_words=["bold", "playful", "irreverent"],
            audience_description="Hot sauce enthusiasts aged 25-45",
            do_list=["Use humor", "Reference pop culture"],
            dont_list=["Be boring", "Use corporate speak"],
        )
        assert profile.name == "Mondo Shrimp"
        assert len(profile.tone_words) == 3
        assert "Hot sauce" in profile.audience_description
        assert len(profile.do_list) == 2
        assert len(profile.dont_list) == 2

    def test_optional_fields_default(self):
        profile = GeneratedBrandProfile(
            name="Brand",
            tone_words=[],
            audience_description="",
            do_list=[],
            dont_list=[],
        )
        assert profile.product_catalog == []
        assert profile.compliance_notes is None
        assert profile.tagline is None

    def test_product_catalog(self):
        profile = GeneratedBrandProfile(
            name="Brand",
            tone_words=["bold"],
            audience_description="Foodies",
            do_list=[],
            dont_list=[],
            product_catalog=[
                {"name": "Ghost Pepper Sauce", "description": "Super hot"},
            ],
        )
        assert len(profile.product_catalog) == 1
        assert profile.product_catalog[0]["name"] == "Ghost Pepper Sauce"


class TestBuildBrandPrompt:
    """Verify the prompt builder for Claude API."""

    def test_includes_website_title(self):
        from pipeline.scraper import ScrapedWebsite

        site = ScrapedWebsite(
            url="https://mondoshrimp.com",
            title="Mondo Shrimp - Hot Sauce",
            description="The most interesting sauce",
            headings=["Welcome"],
            body_text="We make hot sauce.",
            social_links={},
        )
        prompt = build_brand_prompt(site)
        assert "Mondo Shrimp" in prompt

    def test_includes_body_text(self):
        from pipeline.scraper import ScrapedWebsite

        site = ScrapedWebsite(
            url="https://example.com",
            title="Example",
            description="",
            headings=[],
            body_text="We sell artisanal hot sauce.",
            social_links={},
        )
        prompt = build_brand_prompt(site)
        assert "artisanal hot sauce" in prompt

    def test_includes_json_instruction(self):
        from pipeline.scraper import ScrapedWebsite

        site = ScrapedWebsite(
            url="https://example.com",
            title="Test",
            description="",
            headings=[],
            body_text="",
            social_links={},
        )
        prompt = build_brand_prompt(site)
        assert "JSON" in prompt


class TestGenerateBrandProfile:
    """Verify generate_brand_profile function signature."""

    def test_is_async(self):
        assert asyncio.iscoroutinefunction(generate_brand_profile)

    def test_accepts_scraped_website(self):
        import inspect
        sig = inspect.signature(generate_brand_profile)
        params = list(sig.parameters.keys())
        assert "scraped_site" in params
