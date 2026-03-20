from __future__ import annotations

import logging
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


async def accumulate_approval_signals(
    tenant_id: str,
    chosen_idx: int,  # index of chosen option
    all_options: list[dict],  # all 3 caption variant dicts
) -> None:
    """Extract structural preferences from an approval and upsert into preference_signals.

    Called async after every approval. Non-blocking, non-critical.

    For each discriminating feature dimension:
    - The CHOSEN value gets occurrences+1 AND total_opportunities+1
    - The REJECTED values get ONLY total_opportunities+1 (no occurrences bump)
    This way confidence = occurrences / total_opportunities reflects true preference rate.
    E.g., picking "short" 6 of 10 times → confidence = 0.6, not 1.0.
    """
    from bot.db import get_supabase_client
    from pipeline.learning.structural_diff import compute_pairwise_diff, extract_features

    try:
        chosen = all_options[chosen_idx] if chosen_idx < len(all_options) else {}
        chosen_features = extract_features(chosen)
        rejected = [opt for i, opt in enumerate(all_options) if i != chosen_idx]
        rejected_features = [extract_features(r) for r in rejected]

        diffs = compute_pairwise_diff(chosen_features, rejected_features)

        if not diffs:
            return  # No discriminating features -- nothing to learn

        client = get_supabase_client()
        now = datetime.now(UTC).isoformat()

        # Collect all rejected values per feature for the "losing" side
        from pipeline.learning.structural_diff import _bucket_word_count

        rejected_values_by_feature: dict[str, set[str]] = {}
        for feature in diffs:
            vals: set[str] = set()
            for rf in rejected_features:
                if feature == "word_count_bucket":
                    vals.add(_bucket_word_count(rf.word_count))
                elif feature == "formula":
                    vals.add(rf.formula)
                elif feature == "emoji":
                    vals.add("has_emoji" if rf.has_emoji else "no_emoji")
                elif feature == "question_hook":
                    vals.add("uses_question" if rf.question_mark_count > 0 else "no_question")
                elif feature == "exclamation":
                    vals.add("has_exclamation" if rf.exclamation_count > 0 else "no_exclamation")
                elif feature == "hashtag_density":
                    vals.add("many_hashtags" if rf.hashtag_count > 3 else "few_hashtags")
            rejected_values_by_feature[feature] = vals

        for feature, chosen_value in diffs.items():
            # Winning side: increment both occurrences and total_opportunities
            _upsert_approval_signal(
                client, tenant_id, feature, chosen_value, now,
                increment_occurrences=True,
            )

            # Losing side(s): increment only total_opportunities
            for rejected_value in rejected_values_by_feature.get(feature, set()):
                if rejected_value != chosen_value:
                    _upsert_approval_signal(
                        client, tenant_id, feature, rejected_value, now,
                        increment_occurrences=False,
                    )

        logger.info(
            "Accumulated approval signals",
            extra={"tenant_id": tenant_id, "features": list(diffs.keys())},
        )
    except Exception:
        logger.exception("Failed to accumulate approval signals -- non-fatal")


def _upsert_approval_signal(
    client: object,
    tenant_id: str,
    feature: str,
    value: str,
    now: str,
    increment_occurrences: bool,
) -> None:
    """Upsert a single approval_structural signal row."""
    existing = (
        client.table("preference_signals")
        .select("id, occurrences, total_opportunities")
        .eq("tenant_id", tenant_id)
        .eq("signal_type", "approval_structural")
        .eq("feature", feature)
        .eq("value", value)
        .limit(1)
        .execute()
    )

    if existing.data:
        row = existing.data[0]
        new_occ = row["occurrences"] + (1 if increment_occurrences else 0)
        new_total = row["total_opportunities"] + 1
        (
            client.table("preference_signals")
            .update(
                {
                    "occurrences": new_occ,
                    "total_opportunities": new_total,
                    "confidence": round(new_occ / new_total, 3),
                    "last_seen_at": now,
                    "updated_at": now,
                }
            )
            .eq("id", row["id"])
            .execute()
        )
    else:
        (
            client.table("preference_signals")
            .insert(
                {
                    "tenant_id": tenant_id,
                    "signal_type": "approval_structural",
                    "feature": feature,
                    "value": value,
                    "occurrences": 1 if increment_occurrences else 0,
                    "total_opportunities": 1,
                    "confidence": 1.0 if increment_occurrences else 0.0,
                    "last_seen_at": now,
                }
            )
            .execute()
        )


async def accumulate_edit_signal(
    tenant_id: str,
    feature: str,
    value: str,
    lesson_text: str | None = None,
) -> None:
    """Upsert an edit-derived preference signal.

    Edit signals start at confidence 0.5 (higher than approval) because
    the user actively changed something.
    """
    from bot.db import get_supabase_client

    try:
        client = get_supabase_client()
        now = datetime.now(UTC).isoformat()

        existing = (
            client.table("preference_signals")
            .select("id, occurrences, total_opportunities, lesson_text")
            .eq("tenant_id", tenant_id)
            .eq("signal_type", "edit_pattern")
            .eq("feature", feature)
            .eq("value", value)
            .limit(1)
            .execute()
        )

        if existing.data:
            row = existing.data[0]
            new_occ = row["occurrences"] + 1
            new_total = row["total_opportunities"] + 1
            # Edit confidence: starts at 0.5, grows faster
            confidence = min(0.5 + (new_occ - 1) * 0.25, 1.0)
            update_data: dict = {
                "occurrences": new_occ,
                "total_opportunities": new_total,
                "confidence": round(confidence, 3),
                "last_seen_at": now,
                "updated_at": now,
            }
            if lesson_text:
                update_data["lesson_text"] = lesson_text
            (client.table("preference_signals").update(update_data).eq("id", row["id"]).execute())
        else:
            (
                client.table("preference_signals")
                .insert(
                    {
                        "tenant_id": tenant_id,
                        "signal_type": "edit_pattern",
                        "feature": feature,
                        "value": value,
                        "occurrences": 1,
                        "total_opportunities": 1,
                        "confidence": 0.5,
                        "lesson_text": lesson_text,
                        "last_seen_at": now,
                    }
                )
                .execute()
            )

        logger.info(
            "Accumulated edit signal",
            extra={"tenant_id": tenant_id, "feature": feature, "value": value},
        )
    except Exception:
        logger.exception("Failed to accumulate edit signal -- non-fatal")


async def load_preference_signals(
    tenant_id: str,
    min_confidence: float = 0.5,
    min_opportunities_approval: int = 8,
    min_opportunities_edit: int = 2,
) -> list[dict]:
    """Load preference signals that meet confidence and sample size thresholds."""
    from bot.db import get_supabase_client

    try:
        client = get_supabase_client()
        result = (
            client.table("preference_signals")
            .select("*")
            .eq("tenant_id", tenant_id)
            .gte("confidence", min_confidence)
            .order("confidence", desc=True)
            .execute()
        )

        # Filter by opportunity thresholds based on signal type
        signals = []
        for row in result.data or []:
            if row["signal_type"] == "edit_pattern":
                if row["total_opportunities"] >= min_opportunities_edit:
                    signals.append(row)
            elif row["signal_type"] == "approval_structural":
                if row["total_opportunities"] >= min_opportunities_approval:
                    signals.append(row)
            else:
                # engagement signals: require 5+ opportunities
                if row["total_opportunities"] >= 5:
                    signals.append(row)

        return signals
    except Exception:
        logger.exception("Failed to load preference signals")
        return []
