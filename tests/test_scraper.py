"""Tests for pipeline.scraper — website scraping for brand profile auto-generation."""

from __future__ import annotations

import asyncio

import pytest

from pipeline.scraper import ScrapedWebsite, scrape_website


class TestScrapedWebsiteModel:
    """Verify the ScrapedWebsite data model."""

    def test_has_required_fields(self):
        site = ScrapedWebsite(
            url="https://example.com",
            title="Example",
            description="A test site",
            headings=["Welcome"],
            body_text="Some text about the business.",
            social_links={},
        )
        assert site.url == "https://example.com"
        assert site.title == "Example"
        assert site.description == "A test site"
        assert site.headings == ["Welcome"]
        assert site.body_text == "Some text about the business."
        assert site.social_links == {}

    def test_optional_fields_default(self):
        site = ScrapedWebsite(
            url="https://example.com",
            title="",
            description="",
            headings=[],
            body_text="",
            social_links={},
        )
        assert site.meta_keywords == []
        assert site.og_image is None
        assert site.products == []

    def test_social_links_dict(self):
        site = ScrapedWebsite(
            url="https://example.com",
            title="",
            description="",
            headings=[],
            body_text="",
            social_links={
                "instagram": "https://instagram.com/brand",
                "facebook": "https://facebook.com/brand",
            },
        )
        assert site.social_links["instagram"] == "https://instagram.com/brand"

    def test_products_list(self):
        site = ScrapedWebsite(
            url="https://example.com",
            title="",
            description="",
            headings=[],
            body_text="",
            social_links={},
            products=["Hot Sauce", "BBQ Sauce"],
        )
        assert len(site.products) == 2


class TestScrapeWebsiteFunction:
    """Verify scrape_website function signature."""

    def test_is_async(self):
        assert asyncio.iscoroutinefunction(scrape_website)

    def test_accepts_url_parameter(self):
        import inspect
        sig = inspect.signature(scrape_website)
        params = list(sig.parameters.keys())
        assert "url" in params


class TestExtractSocialLinks:
    """Test the social link extraction helper."""

    def test_extracts_instagram_from_html(self):
        from pipeline.scraper import _extract_social_links

        html = '<a href="https://www.instagram.com/mondoshrimp/">Instagram</a>'
        links = _extract_social_links(html)
        assert "instagram" in links
        assert "mondoshrimp" in links["instagram"]

    def test_extracts_facebook_from_html(self):
        from pipeline.scraper import _extract_social_links

        html = '<a href="https://www.facebook.com/MondoShrimp">Facebook</a>'
        links = _extract_social_links(html)
        assert "facebook" in links

    def test_extracts_tiktok_from_html(self):
        from pipeline.scraper import _extract_social_links

        html = '<a href="https://www.tiktok.com/@brand">TikTok</a>'
        links = _extract_social_links(html)
        assert "tiktok" in links

    def test_extracts_twitter_x_from_html(self):
        from pipeline.scraper import _extract_social_links

        html = '<a href="https://x.com/brand">X</a>'
        links = _extract_social_links(html)
        assert "x" in links or "twitter" in links

    def test_ignores_non_social_links(self):
        from pipeline.scraper import _extract_social_links

        html = '<a href="https://google.com">Google</a>'
        links = _extract_social_links(html)
        assert len(links) == 0

    def test_handles_empty_html(self):
        from pipeline.scraper import _extract_social_links

        links = _extract_social_links("")
        assert links == {}


class TestExtractProducts:
    """Test product name extraction from page text."""

    def test_extracts_product_names_from_structured_data(self):
        from pipeline.scraper import _extract_products_from_jsonld

        jsonld = {
            "@type": "Product",
            "name": "Ghost Pepper Sauce",
        }
        products = _extract_products_from_jsonld([jsonld])
        assert "Ghost Pepper Sauce" in products

    def test_handles_product_list(self):
        from pipeline.scraper import _extract_products_from_jsonld

        jsonld_list = [
            {"@type": "Product", "name": "Sauce A"},
            {"@type": "Product", "name": "Sauce B"},
        ]
        products = _extract_products_from_jsonld(jsonld_list)
        assert len(products) == 2

    def test_handles_empty_jsonld(self):
        from pipeline.scraper import _extract_products_from_jsonld

        products = _extract_products_from_jsonld([])
        assert products == []

    def test_ignores_non_product_types(self):
        from pipeline.scraper import _extract_products_from_jsonld

        jsonld = [{"@type": "Organization", "name": "Acme Corp"}]
        products = _extract_products_from_jsonld(jsonld)
        assert products == []


class TestCleanBodyText:
    """Test HTML body text extraction and cleaning."""

    def test_strips_script_tags(self):
        from pipeline.scraper import _clean_body_text

        html = "<body><script>alert('x')</script><p>Hello world</p></body>"
        text = _clean_body_text(html)
        assert "alert" not in text
        assert "Hello world" in text

    def test_strips_style_tags(self):
        from pipeline.scraper import _clean_body_text

        html = "<body><style>.x{color:red}</style><p>Content</p></body>"
        text = _clean_body_text(html)
        assert "color" not in text
        assert "Content" in text

    def test_collapses_whitespace(self):
        from pipeline.scraper import _clean_body_text

        html = "<body><p>Hello</p>   \n\n\n   <p>World</p></body>"
        text = _clean_body_text(html)
        assert "\n\n\n" not in text

    def test_truncates_long_text(self):
        from pipeline.scraper import _clean_body_text

        html = "<body>" + "x" * 20000 + "</body>"
        text = _clean_body_text(html, max_chars=5000)
        assert len(text) <= 5000
