"""Brand voice loader — fetches brand profile + few-shot examples for prompt injection."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BrandProfile:
    """Brand identity and voice configuration."""

    tenant_id: str
    name: str
    tone_words: list[str]
    audience_description: str
    do_list: list[str]
    dont_list: list[str]
    product_catalog: dict | None = None
    compliance_notes: str = ""


@dataclass
class FewShotExample:
    """A real post example for few-shot prompting."""

    platform: str
    content_type: str
    caption: str
    image_url: str | None = None
    engagement_score: float | None = None


def format_brand_context(profile: BrandProfile, examples: list[FewShotExample]) -> str:
    """Format brand profile and examples into a prompt context block."""
    parts = [
        f"# Brand: {profile.name}",
        f"\n## Tone: {', '.join(profile.tone_words)}",
        f"\n## Target Audience: {profile.audience_description}",
    ]

    if profile.do_list:
        parts.append("\n## DO:")
        for item in profile.do_list:
            parts.append(f"- {item}")

    if profile.dont_list:
        parts.append("\n## DON'T:")
        for item in profile.dont_list:
            parts.append(f"- {item}")

    if profile.product_catalog:
        parts.append(f"\n## Products: {profile.product_catalog}")

    if profile.compliance_notes:
        parts.append(f"\n## Compliance Notes: {profile.compliance_notes}")

    if examples:
        parts.append("\n## Example Posts (for style reference):")
        for i, ex in enumerate(examples, 1):
            parts.append(f"\n### Example {i} ({ex.platform}, {ex.content_type}):")
            parts.append(ex.caption)

    return "\n".join(parts)


async def load_brand_profile(tenant_id: str) -> BrandProfile | None:
    """Load brand profile from Supabase for a tenant.

    TODO: Wire up Supabase client query.
    """
    logger.info("Loading brand profile", extra={"tenant_id": tenant_id})
    # TODO: Query brand_profiles table
    return None


async def load_few_shot_examples(
    tenant_id: str, platform: str | None = None, limit: int = 5
) -> list[FewShotExample]:
    """Load few-shot examples from Supabase.

    TODO: Wire up Supabase client query.
    """
    logger.info(
        "Loading few-shot examples",
        extra={"tenant_id": tenant_id, "platform": platform, "limit": limit},
    )
    # TODO: Query few_shot_examples table, optionally filtered by platform
    return []
