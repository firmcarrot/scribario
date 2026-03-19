"""Redis-backed rate limiter — survives bot restarts, works across workers."""

from __future__ import annotations

import logging
import time

import redis.asyncio as aioredis

from bot.config import get_settings

logger = logging.getLogger(__name__)

# Defaults
DEFAULT_WINDOW = 60  # seconds
DEFAULT_MAX_REQUESTS = 5

_redis_client: aioredis.Redis | None = None


def _get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            get_settings().redis_url, decode_responses=True
        )
    return _redis_client


async def is_rate_limited(
    user_id: int,
    window: int = DEFAULT_WINDOW,
    max_requests: int = DEFAULT_MAX_REQUESTS,
) -> bool:
    """Check if a user is rate-limited. Returns True if they should be blocked.

    Uses Redis sorted sets with timestamp scores for sliding window.
    """
    try:
        r = _get_redis()
        key = f"rate_limit:{user_id}"
        now = time.time()
        cutoff = now - window

        pipe = r.pipeline()
        # Remove expired entries
        pipe.zremrangebyscore(key, 0, cutoff)
        # Count remaining entries in window
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set TTL on key so it auto-cleans
        pipe.expire(key, window + 10)

        results = await pipe.execute()
        count = results[1]  # zcard result

        if count >= max_requests:
            logger.info(
                "Rate limited",
                extra={"user_id": user_id, "count": count, "max": max_requests},
            )
            return True

        return False

    except Exception:
        # If Redis fails, fall through (don't block users due to infra issues)
        logger.warning("Rate limiter Redis error, allowing request", exc_info=True)
        return False
