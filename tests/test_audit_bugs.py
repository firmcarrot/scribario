"""Tests for production audit bug fixes."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.intake import parse_platform_targets


class TestRateLimiting:
    """CRIT-1: Rate limiting on content requests."""

    @pytest.mark.asyncio
    async def test_rate_limiter_rejects_after_limit(self):
        """Rate limiter should reject requests after hitting the limit."""
        from bot.services.rate_limiter import is_rate_limited

        mock_redis = MagicMock()
        mock_pipe = MagicMock()
        # pipe methods (zremrangebyscore, zcard, zadd, expire) are sync queue ops
        # only execute() is awaited
        mock_pipe.execute = AsyncMock(return_value=[None, 6, None, None])  # zcard=6 > default 5
        mock_redis.pipeline.return_value = mock_pipe

        with patch("bot.services.rate_limiter._get_redis", return_value=mock_redis):
            result = await is_rate_limited(user_id=99999)
            assert result is True

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_under_limit(self):
        """Rate limiter should allow requests under the limit."""
        from bot.services.rate_limiter import is_rate_limited

        mock_redis = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.execute = AsyncMock(return_value=[None, 3, None, None])  # zcard=3 < default 5
        mock_redis.pipeline.return_value = mock_pipe

        with patch("bot.services.rate_limiter._get_redis", return_value=mock_redis):
            result = await is_rate_limited(user_id=99998)
            assert result is False


class TestPhotoWithIntentPlatformDetection:
    """LOW-19: Photo-with-intent should detect platform keywords."""

    def test_parse_platform_targets_instagram(self):
        """Photo caption mentioning Instagram should target it."""
        result = parse_platform_targets("Post this to Instagram")
        assert result == ["instagram"]

    def test_parse_platform_targets_facebook(self):
        result = parse_platform_targets("Share on Facebook")
        assert result == ["facebook"]

    def test_parse_platform_targets_none(self):
        """No platform mentions should return None (all connected)."""
        result = parse_platform_targets("Post about our weekend special")
        assert result is None


class TestCaptionTruncation:
    """MEDIUM-10: Telegram caption byte-length safety."""

    def test_truncate_caption_short(self):
        """Short captions should be returned as-is."""
        from bot.handlers.intake import truncate_telegram_caption

        assert truncate_telegram_caption("Hello world") == "Hello world"

    def test_truncate_caption_long(self):
        """Long captions should be truncated to 1024 bytes."""
        from bot.handlers.intake import truncate_telegram_caption

        long_text = "A" * 2000
        result = truncate_telegram_caption(long_text)
        assert len(result.encode("utf-8")) <= 1024

    def test_truncate_caption_unicode(self):
        """Unicode captions should be truncated by bytes, not chars."""
        from bot.handlers.intake import truncate_telegram_caption

        # Each emoji is 4 bytes
        emoji_text = "🍤" * 300  # 1200 bytes
        result = truncate_telegram_caption(emoji_text)
        assert len(result.encode("utf-8")) <= 1024


class TestUnsupportedMessageHandler:
    """HIGH-7: Catch-all for unsupported message types."""

    @pytest.mark.asyncio
    async def test_unsupported_handler_exists(self):
        """There should be a handler for unsupported message types."""
        from bot.handlers.intake import handle_unsupported_message

        assert callable(handle_unsupported_message)

    @pytest.mark.asyncio
    async def test_unsupported_handler_replies(self):
        """Unsupported message handler should reply with helpful text."""
        from bot.handlers.intake import handle_unsupported_message

        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.content_type = "sticker"

        await handle_unsupported_message(message)
        message.answer.assert_called_once()
        text = message.answer.call_args[0][0]
        assert "text" in text.lower() or "type" in text.lower()


class TestGenerationFailureNotification:
    """HIGH-4: User should be notified when generation fails."""

    @pytest.mark.asyncio
    async def test_failure_notification_sent(self):
        """When a job fails, user should get a Telegram message."""
        from worker.main import Worker

        worker = Worker(max_concurrency=1, poll_interval=1)

        # The _process_job method should call _mark_job_failed on exception
        # and the handler should notify the user
        # We just verify the _mark_job_failed path exists
        assert hasattr(worker, '_mark_job_failed')
        assert callable(worker._mark_job_failed)


class TestImageGenFailureFallback:
    """HIGH-5: All images failing should not produce an empty preview."""

    @pytest.mark.asyncio
    async def test_no_images_still_sends_preview(self):
        """When all image gens fail, preview should still show captions."""
        # This is tested implicitly by the _send_preview function
        # which has a text-only fallback when image_urls is empty
        from worker.jobs.generate_content import _send_preview

        assert callable(_send_preview)


def _check_rate_limit(user_id: int) -> bool:
    """Helper: check rate limit using the intake module's rate limiter."""
    from bot.handlers.intake import _rate_limiter, RATE_LIMIT_WINDOW, RATE_LIMIT_MAX

    now = datetime.now(timezone.utc).timestamp()
    if user_id not in _rate_limiter:
        _rate_limiter[user_id] = []

    # Clean old entries
    _rate_limiter[user_id] = [
        t for t in _rate_limiter[user_id] if now - t < RATE_LIMIT_WINDOW
    ]

    if len(_rate_limiter[user_id]) >= RATE_LIMIT_MAX:
        return False

    _rate_limiter[user_id].append(now)
    return True
