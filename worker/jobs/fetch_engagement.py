"""Job handler — fetch engagement metrics from Postiz for recent posts."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from bot.db import get_supabase_client
from pipeline.engagement import fetch_post_engagement
from pipeline.learning.engagement_scorer import compute_engagement_score

logger = logging.getLogger(__name__)

# Only fetch engagement for posts less than 30 days old
MAX_POST_AGE_DAYS = 30
# Don't update few_shot engagement_score for posts younger than this
# (they haven't had time to accumulate meaningful engagement)
MIN_POST_AGE_HOURS = 24


async def handle_fetch_engagement(message: dict) -> None:
    """Poll Postiz for engagement metrics on recent posts.

    Finds posting_results with platform_post_id set (meaning Postiz returned
    a post ID on publish), fetches current engagement, upserts into
    engagement_metrics, and updates few_shot_examples.engagement_score.
    """
    client = get_supabase_client()

    cutoff = (datetime.now(UTC) - timedelta(days=MAX_POST_AGE_DAYS)).isoformat()

    # 1. Find posting_results with platform_post_id, posted in last 30 days
    # NOTE: This is a system-level sweep across all tenants (by design).
    # Uses service role client. Each result row includes its own tenant_id
    # which is used for tenant-scoped writes downstream.
    result = (
        client.table("posting_results")
        .select("id, platform_post_id, platform, posting_job_id, tenant_id, posted_at")
        .eq("success", True)
        .not_.is_("platform_post_id", "null")
        .gte("posted_at", cutoff)
        .execute()
    )

    posts = result.data or []
    if not posts:
        logger.info("No recent posts with platform_post_id — nothing to fetch")
        return

    logger.info("Fetching engagement for %d posts", len(posts))

    fetched = 0
    failed = 0

    for post in posts:
        postiz_id = post["platform_post_id"]
        posting_job_id = post.get("posting_job_id")
        tenant_id = post.get("tenant_id")

        # Resolve draft_id via posting_jobs (3-hop: posting_results → posting_jobs → draft_id)
        draft_id = None
        if posting_job_id:
            try:
                pj_result = (
                    client.table("posting_jobs")
                    .select("draft_id")
                    .eq("id", posting_job_id)
                    .limit(1)
                    .execute()
                )
                if pj_result.data:
                    draft_id = pj_result.data[0].get("draft_id")
            except Exception:
                logger.warning("Could not resolve draft_id for posting_job %s", posting_job_id)

        # 2. Fetch engagement from Postiz
        engagement = await fetch_post_engagement(postiz_id=postiz_id)
        if engagement is None:
            failed += 1
            continue

        # 3. Compute engagement score
        score = compute_engagement_score(
            likes=engagement.likes,
            comments=engagement.comments,
            shares=engagement.shares,
            views=engagement.views,
        )

        # 4. Upsert into engagement_metrics
        try:
            client.table("engagement_metrics").upsert(
                {
                    "result_id": post["id"],
                    "platform": post["platform"],
                    "likes": engagement.likes,
                    "comments": engagement.comments,
                    "shares": engagement.shares,
                    "views": engagement.views,
                    "fetched_at": datetime.now(UTC).isoformat(),
                    "tenant_id": tenant_id,
                    "draft_id": draft_id,
                },
                on_conflict="result_id",
            ).execute()
        except Exception:
            logger.exception(
                "Failed to upsert engagement_metrics",
                extra={"result_id": post["id"]},
            )
            failed += 1
            continue

        # 5. Update few_shot_examples.engagement_score if we have a draft_id
        # Skip if post is less than 24h old — too early for meaningful engagement
        posted_at_str = post.get("posted_at", "")
        post_age_ok = True
        try:
            posted_at = datetime.fromisoformat(posted_at_str.replace("Z", "+00:00"))
            if (datetime.now(UTC) - posted_at).total_seconds() < MIN_POST_AGE_HOURS * 3600:
                post_age_ok = False
        except (ValueError, TypeError):
            pass  # If we can't parse the date, update anyway

        if draft_id and tenant_id and post_age_ok:
            try:
                client.table("few_shot_examples").update(
                    {"engagement_score": score}
                ).eq("draft_id", draft_id).eq("tenant_id", tenant_id).execute()
            except Exception:
                logger.warning(
                    "Could not update few_shot_examples engagement_score",
                    extra={"draft_id": draft_id},
                )

        fetched += 1

    # 6. Phase 4C: Aggregate engagement by formula per tenant → preference_signals
    await _upsert_engagement_preference_signals(client, posts)

    logger.info(
        "Engagement fetch complete",
        extra={"fetched": fetched, "failed": failed, "total": len(posts)},
    )


async def _upsert_engagement_preference_signals(client: object, posts: list[dict]) -> None:
    """Aggregate engagement scores by formula per tenant and upsert into preference_signals.

    This is Phase 4C of the learning system: engagement data becomes "audience truth"
    that overrides approval patterns. For each formula with 5+ posts and engagement data,
    we create a preference_signal with signal_type='engagement'.
    """
    from collections import defaultdict

    # Collect (tenant_id, draft_id) pairs from posts that have both
    tenant_drafts: dict[str, list[str]] = defaultdict(list)
    for post in posts:
        tenant_id = post.get("tenant_id")
        posting_job_id = post.get("posting_job_id")
        if tenant_id and posting_job_id:
            tenant_drafts[tenant_id].append(posting_job_id)

    if not tenant_drafts:
        return

    now = datetime.now(UTC).isoformat()

    for tenant_id in tenant_drafts:
        try:
            # Get engagement scores per formula for this tenant
            # Join: few_shot_examples (has formula + engagement_score + draft_id)
            result = (
                client.table("few_shot_examples")
                .select("formula, engagement_score")
                .eq("tenant_id", tenant_id)
                .not_.is_("formula", "null")
                .not_.is_("engagement_score", "null")
                .execute()
            )

            if not result.data:
                continue

            # Aggregate by formula
            formula_scores: dict[str, list[float]] = defaultdict(list)
            for row in result.data:
                formula = row.get("formula")
                score = row.get("engagement_score")
                if formula and score is not None and score > 0:
                    formula_scores[formula].append(float(score))

            # Only create signals for formulas with 5+ data points
            for formula, scores in formula_scores.items():
                if len(scores) < 5:
                    continue

                avg_score = sum(scores) / len(scores)
                # Normalize to 0-1 confidence: score/10 (engagement is 0-10 scale)
                confidence = min(round(avg_score / 10.0, 3), 1.0)

                # Upsert into preference_signals
                existing = (
                    client.table("preference_signals")
                    .select("id, occurrences, total_opportunities")
                    .eq("tenant_id", tenant_id)
                    .eq("signal_type", "engagement")
                    .eq("feature", "formula")
                    .eq("value", formula)
                    .limit(1)
                    .execute()
                )

                if existing.data:
                    row = existing.data[0]
                    (
                        client.table("preference_signals")
                        .update({
                            "occurrences": len(scores),
                            "total_opportunities": len(scores),
                            "confidence": confidence,
                            "last_seen_at": now,
                            "updated_at": now,
                        })
                        .eq("id", row["id"])
                        .execute()
                    )
                else:
                    (
                        client.table("preference_signals")
                        .insert({
                            "tenant_id": tenant_id,
                            "signal_type": "engagement",
                            "feature": "formula",
                            "value": formula,
                            "occurrences": len(scores),
                            "total_opportunities": len(scores),
                            "confidence": confidence,
                            "last_seen_at": now,
                        })
                        .execute()
                    )

            logger.info(
                "Upserted engagement preference signals",
                extra={"tenant_id": tenant_id, "formulas": len(formula_scores)},
            )
        except Exception:
            logger.exception(
                "Failed to upsert engagement preference signals for tenant",
                extra={"tenant_id": tenant_id},
            )
