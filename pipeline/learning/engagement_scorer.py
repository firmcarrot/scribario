from __future__ import annotations


def compute_engagement_score(
    likes: int,
    comments: int,
    shares: int,
    views: int,
) -> float:
    """Normalize engagement metrics to a 0-10 score.

    Weighted: shares (5x) > comments (3x) > likes (1x), normalized by views.
    """
    if views <= 0:
        # No view data -- fall back to raw interaction count
        raw = likes + comments * 3 + shares * 5
        return min(round(raw / 10, 1), 10.0)

    raw = (likes * 1.0 + comments * 3.0 + shares * 5.0) / max(views, 1) * 1000
    return min(round(raw, 1), 10.0)
