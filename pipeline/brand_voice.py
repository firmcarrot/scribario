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
    default_image_style: str = "photorealistic"
    voice_pool: list[dict] | None = None  # [{voice_id, gender, style_label}]


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
    """Load brand profile from Supabase for a tenant."""
    from bot.db import get_supabase_client

    logger.info("Loading brand profile", extra={"tenant_id": tenant_id})

    try:
        client = get_supabase_client()
        result = (
            client.table("brand_profiles")
            .select("*, tenants(name)")
            .eq("tenant_id", tenant_id)
            .limit(1)
            .execute()
        )

        if not result.data:
            return None

        row = result.data[0]
        tenant_name = "Brand"
        tenants_data = row.get("tenants")
        if isinstance(tenants_data, dict):
            tenant_name = tenants_data.get("name", tenant_name)

        return BrandProfile(
            tenant_id=tenant_id,
            name=tenant_name,
            tone_words=row.get("tone_words", []),
            audience_description=row.get("audience_description", ""),
            do_list=row.get("do_list", []),
            dont_list=row.get("dont_list", []),
            product_catalog=row.get("product_catalog"),
            compliance_notes=row.get("compliance_notes", ""),
            default_image_style=row.get("default_image_style", "photorealistic"),
            voice_pool=row.get("voice_pool"),
        )
    except Exception:
        logger.exception("Failed to load brand profile", extra={"tenant_id": tenant_id})
        return None


async def load_few_shot_examples(
    tenant_id: str, platform: str | None = None, limit: int = 5
) -> list[FewShotExample]:
    """Load few-shot examples from Supabase."""
    from bot.db import get_supabase_client

    logger.info(
        "Loading few-shot examples",
        extra={"tenant_id": tenant_id, "platform": platform, "limit": limit},
    )

    try:
        client = get_supabase_client()
        query = (
            client.table("few_shot_examples")
            .select("*")
            .eq("tenant_id", tenant_id)
            .order("engagement_score", desc=True)
            .limit(limit)
        )

        if platform:
            query = query.eq("platform", platform)

        result = query.execute()

        return [
            FewShotExample(
                platform=row["platform"],
                content_type=row["content_type"],
                caption=row["caption"],
                image_url=row.get("image_url"),
                engagement_score=row.get("engagement_score"),
            )
            for row in result.data
        ]
    except Exception:
        logger.exception("Failed to load few-shot examples", extra={"tenant_id": tenant_id})
        return []
