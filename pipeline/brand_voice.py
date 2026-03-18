"""Brand voice loader — fetches brand profile + few-shot examples for prompt injection."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

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
    formula: str | None = None


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
            # Show formula + engagement when available (Phase 3D)
            meta_parts = [ex.platform]
            if ex.formula:
                meta_parts.append(ex.formula)
            else:
                meta_parts.append(ex.content_type)
            if ex.engagement_score and ex.engagement_score > 1.0:
                meta_parts.append(f"engagement: {ex.engagement_score}/10")
            parts.append(f"\n### Example {i} ({', '.join(meta_parts)}):")
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
    """Load few-shot examples with recency decay + formula diversity.

    Phase 3C: Smarter selection replaces simple ORDER BY engagement_score DESC.
    1. Fetch top 20 examples
    2. Apply recency decay with floor: effective_score = max(score * 0.95^days, score * 0.3)
    3. Formula diversity: max 2 examples per formula
    4. Return top `limit` after re-ranking
    """
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
            .limit(20)  # Fetch more for re-ranking
        )

        if platform:
            query = query.eq("platform", platform)

        result = query.execute()
        rows = result.data or []

        if not rows:
            return []

        # Apply recency decay
        now = datetime.now(UTC)
        scored_rows: list[tuple[float, dict]] = []
        for row in rows:
            score = row.get("engagement_score") or 1.0
            created = row.get("created_at", "")
            days_old = 0.0
            if created:
                try:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    days_old = (now - created_dt).total_seconds() / 86400
                except (ValueError, TypeError):
                    pass
            # Recency decay with floor (DA fix I3)
            effective = max(score * (0.95 ** days_old), score * 0.3)
            scored_rows.append((effective, row))

        # Sort by effective score descending
        scored_rows.sort(key=lambda x: x[0], reverse=True)

        # Formula diversity: max 2 per formula
        formula_counts: dict[str, int] = {}
        selected: list[tuple[float, dict]] = []
        for effective, row in scored_rows:
            formula = row.get("formula") or "unknown"
            count = formula_counts.get(formula, 0)
            if count >= 2:
                continue
            formula_counts[formula] = count + 1
            selected.append((effective, row))
            if len(selected) >= limit:
                break

        return [
            FewShotExample(
                platform=row["platform"],
                content_type=row["content_type"],
                caption=row["caption"],
                image_url=row.get("image_url"),
                engagement_score=row.get("engagement_score"),
                formula=row.get("formula"),
            )
            for _, row in selected
        ]
    except Exception:
        logger.exception("Failed to load few-shot examples", extra={"tenant_id": tenant_id})
        return []


async def load_learned_preferences(tenant_id: str) -> str:
    """Build a learned preferences prompt block from preference_signals.

    Phase 3A: Returns formatted text for Layer 11, or empty string if
    no signals meet thresholds.
    """
    try:
        from pipeline.learning.preference_engine import load_preference_signals

        signals = await load_preference_signals(tenant_id)
        if not signals:
            return ""

        hard_rules: list[str] = []
        soft_prefs: list[str] = []

        for sig in signals:
            signal_type = sig["signal_type"]
            feature = sig["feature"]
            value = sig["value"]
            confidence = sig["confidence"]
            occurrences = sig["occurrences"]
            total = sig["total_opportunities"]
            lesson = sig.get("lesson_text")

            if signal_type == "edit_pattern":
                # Edit patterns are hard rules
                desc = lesson or f"{feature}: {value}"
                hard_rules.append(
                    f"- {desc} (you corrected this {occurrences} time"
                    f"{'s' if occurrences > 1 else ''})"
                )
            elif signal_type == "approval_structural":
                desc = f"You tend to pick {value} ({occurrences} of {total} times)"
                soft_prefs.append(f"- {desc}")
            elif signal_type == "engagement":
                desc = (
                    f"Your audience responds best to {value} "
                    f"(confidence: {confidence:.0%})"
                )
                soft_prefs.append(f"- {desc}")

        if not hard_rules and not soft_prefs:
            return ""

        parts = ["## Learned from your feedback (apply these):"]
        if hard_rules:
            parts.append("\nHARD RULES (from your edits):")
            parts.extend(hard_rules)
        if soft_prefs:
            parts.append(
                "\nSOFT PREFERENCES (lean toward these but maintain variety):"
            )
            parts.extend(soft_prefs)
        parts.append(
            "\nALWAYS: One of the 3 caption options must break from these "
            "patterns for variety."
        )

        return "\n".join(parts)
    except Exception:
        logger.exception(
            "Failed to load learned preferences", extra={"tenant_id": tenant_id}
        )
        return ""


async def load_edit_lessons(tenant_id: str) -> str:
    """Build edit lessons prompt block (lessons only, no bad examples).

    Phase 3E (DA fix I2): Only inject the extracted lesson text,
    never show the original "bad" caption.
    """
    try:
        from pipeline.learning.preference_engine import load_preference_signals

        signals = await load_preference_signals(
            tenant_id, min_confidence=0.5, min_opportunities_edit=2
        )
        edit_signals = [
            s for s in signals if s["signal_type"] == "edit_pattern"
        ]

        if len(edit_signals) < 2:
            return ""  # Need 2+ edit signals before injecting

        lessons: list[str] = []
        for sig in edit_signals:
            lesson = sig.get("lesson_text")
            if lesson:
                lessons.append(f"- {lesson}")
            else:
                lessons.append(f"- {sig['feature']}: {sig['value']}")

        if not lessons:
            return ""

        parts = ["## Lessons from your past edits (follow these):"]
        parts.extend(lessons)
        return "\n".join(parts)
    except Exception:
        logger.exception(
            "Failed to load edit lessons", extra={"tenant_id": tenant_id}
        )
        return ""
