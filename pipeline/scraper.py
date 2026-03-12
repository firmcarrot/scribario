"""Website scraper — extract brand info from a business website.

Scrapes a given URL and extracts: title, description, headings, body text,
social media links, product names (from JSON-LD), and Open Graph images.
Used during onboarding to auto-generate brand profiles.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Social platform URL patterns
_SOCIAL_PATTERNS: dict[str, re.Pattern] = {
    "instagram": re.compile(r"https?://(www\.)?instagram\.com/[\w.]+", re.I),
    "facebook": re.compile(r"https?://(www\.)?facebook\.com/[\w.]+", re.I),
    "tiktok": re.compile(r"https?://(www\.)?tiktok\.com/@[\w.]+", re.I),
    "x": re.compile(r"https?://(www\.)?(twitter\.com|x\.com)/[\w]+", re.I),
    "youtube": re.compile(r"https?://(www\.)?youtube\.com/(c/|channel/|@)[\w]+", re.I),
    "linkedin": re.compile(r"https?://(www\.)?linkedin\.com/(company|in)/[\w-]+", re.I),
    "pinterest": re.compile(r"https?://(www\.)?pinterest\.com/[\w]+", re.I),
}

_REQUEST_TIMEOUT = 15
_MAX_BODY_CHARS = 8000


@dataclass
class ScrapedWebsite:
    """Structured data extracted from a business website."""

    url: str
    title: str
    description: str
    headings: list[str]
    body_text: str
    social_links: dict[str, str]
    meta_keywords: list[str] = field(default_factory=list)
    og_image: str | None = None
    products: list[str] = field(default_factory=list)


async def scrape_website(url: str) -> ScrapedWebsite:
    """Scrape a website and extract brand-relevant information.

    Args:
        url: The website URL to scrape.

    Returns:
        ScrapedWebsite with extracted data.

    Raises:
        httpx.HTTPError: If the request fails.
    """
    # Normalize URL
    if not url.startswith("http"):
        url = f"https://{url}"

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=_REQUEST_TIMEOUT,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; ScribarioBot/1.0; "
                "+https://scribario.com)"
            ),
        },
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    html = response.text
    soup = BeautifulSoup(html, "lxml")

    # Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Meta description
    description = ""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        description = str(meta_desc["content"]).strip()

    # Meta keywords
    meta_keywords: list[str] = []
    meta_kw = soup.find("meta", attrs={"name": "keywords"})
    if meta_kw and meta_kw.get("content"):
        meta_keywords = [k.strip() for k in str(meta_kw["content"]).split(",") if k.strip()]

    # OG image
    og_image = None
    og_img_tag = soup.find("meta", attrs={"property": "og:image"})
    if og_img_tag and og_img_tag.get("content"):
        og_image = str(og_img_tag["content"])

    # Headings (h1-h3)
    headings: list[str] = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(strip=True)
        if text and len(text) > 2:
            headings.append(text)

    # Body text
    body_text = _clean_body_text(html, max_chars=_MAX_BODY_CHARS)

    # Social links
    social_links = _extract_social_links(html)

    # Products from JSON-LD
    jsonld_items = _parse_jsonld(soup)
    products = _extract_products_from_jsonld(jsonld_items)

    return ScrapedWebsite(
        url=url,
        title=title,
        description=description,
        headings=headings,
        body_text=body_text,
        social_links=social_links,
        meta_keywords=meta_keywords,
        og_image=og_image,
        products=products,
    )


def _extract_social_links(html: str) -> dict[str, str]:
    """Extract social media profile URLs from HTML."""
    links: dict[str, str] = {}
    for platform, pattern in _SOCIAL_PATTERNS.items():
        match = pattern.search(html)
        if match:
            links[platform] = match.group(0)
    return links


def _clean_body_text(html: str, max_chars: int = _MAX_BODY_CHARS) -> str:
    """Extract and clean visible text from HTML body."""
    soup = BeautifulSoup(html, "lxml")

    # Remove script, style, nav, footer, header tags
    for tag in soup.find_all(["script", "style", "nav", "footer", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    text = text.strip()

    if len(text) > max_chars:
        text = text[:max_chars]

    return text


def _parse_jsonld(soup: BeautifulSoup) -> list[dict]:
    """Parse JSON-LD structured data from the page."""
    items: list[dict] = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                items.extend(data)
            elif isinstance(data, dict):
                items.append(data)
        except (json.JSONDecodeError, TypeError):
            continue
    return items


def _extract_products_from_jsonld(jsonld_items: list[dict]) -> list[str]:
    """Extract product names from JSON-LD structured data."""
    products: list[str] = []
    for item in jsonld_items:
        item_type = item.get("@type", "")
        if item_type == "Product" and item.get("name"):
            products.append(item["name"])
        # Handle ItemList containing products
        if item_type == "ItemList":
            for element in item.get("itemListElement", []):
                if isinstance(element, dict):
                    nested = element.get("item", element)
                    if isinstance(nested, dict) and nested.get("@type") == "Product" and nested.get("name"):
                        products.append(nested["name"])
    return products
