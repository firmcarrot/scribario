"""Tests for the /logo command and logo upload flow."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.logo import _pending_logo_uploads, _get_pending, _set_pending, router


class TestLogoCommand:
    @pytest.mark.asyncio
    async def test_logo_command_prompts_for_photo(self) -> None:
        from bot.handlers.logo import cmd_logo

        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 12345
        msg.answer = AsyncMock()

        with patch("bot.handlers.logo.get_tenant_by_telegram_user",
                    new_callable=AsyncMock,
                    return_value={"tenant_id": "t1", "onboarding_status": "complete"}):
            await cmd_logo(msg)

        msg.answer.assert_called_once()
        answer_text = msg.answer.call_args[0][0]
        assert "logo" in answer_text.lower()
        assert _get_pending(12345) == "t1"

    @pytest.mark.asyncio
    async def test_logo_command_rejects_unauthenticated(self) -> None:
        from bot.handlers.logo import cmd_logo

        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 99999
        msg.answer = AsyncMock()

        with patch("bot.handlers.logo.get_tenant_by_telegram_user",
                    new_callable=AsyncMock, return_value=None):
            await cmd_logo(msg)

        msg.answer.assert_called_once()
        assert _get_pending(99999) is None


class TestPendingTTL:
    def test_fresh_entry_returns_tenant(self) -> None:
        _set_pending(11111, "t1")
        assert _get_pending(11111) == "t1"
        _pending_logo_uploads.pop(11111, None)

    def test_expired_entry_returns_none(self) -> None:
        # Manually insert an expired entry
        _pending_logo_uploads[22222] = ("t2", time.monotonic() - 400)
        assert _get_pending(22222) is None
        assert 22222 not in _pending_logo_uploads


class TestLogoPhotoHandler:
    @pytest.mark.asyncio
    async def test_stores_logo_and_updates_db(self) -> None:
        from bot.handlers.logo import handle_logo_photo

        _set_pending(12345, "t1")

        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 12345
        msg.photo = [MagicMock(), MagicMock(), MagicMock()]
        msg.photo[-1].file_id = "big_photo_file_id"
        msg.photo[-1].file_unique_id = "big_photo_unique"
        msg.answer = AsyncMock()
        msg.bot = MagicMock()

        with patch("bot.handlers.logo.save_logo_from_telegram",
                    new_callable=AsyncMock,
                    return_value="reference-photos/t1/logo_big_photo_unique.jpg") as mock_save:
            await handle_logo_photo(msg)

        mock_save.assert_called_once_with(
            bot=msg.bot,
            file_id="big_photo_file_id",
            file_unique_id="big_photo_unique",
            tenant_id="t1",
        )
        msg.answer.assert_called_once()
        assert "logo" in msg.answer.call_args[0][0].lower()
        assert _get_pending(12345) is None

    @pytest.mark.asyncio
    async def test_skips_photo_without_pending(self) -> None:
        from aiogram.dispatcher.event.bases import SkipHandler

        from bot.handlers.logo import handle_logo_photo

        _pending_logo_uploads.clear()

        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 99999
        msg.photo = [MagicMock()]

        with pytest.raises(SkipHandler):
            await handle_logo_photo(msg)

    @pytest.mark.asyncio
    async def test_handles_download_error(self) -> None:
        """Error during download/store should send error message, not crash."""
        from bot.handlers.logo import handle_logo_photo

        _set_pending(77777, "t2")

        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 77777
        msg.photo = [MagicMock()]
        msg.photo[-1].file_id = "file_id"
        msg.photo[-1].file_unique_id = "unique_id"
        msg.answer = AsyncMock()
        msg.bot = MagicMock()

        with patch("bot.handlers.logo.save_logo_from_telegram",
                    new_callable=AsyncMock,
                    side_effect=RuntimeError("Telegram API down")):
            await handle_logo_photo(msg)

        msg.answer.assert_called_once()
        assert "wrong" in msg.answer.call_args[0][0].lower()
        assert _get_pending(77777) is None

    @pytest.mark.asyncio
    async def test_handles_value_error(self) -> None:
        """ValueError (bad file) should show specific rejection message."""
        from bot.handlers.logo import handle_logo_photo

        _set_pending(88888, "t3")

        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 88888
        msg.photo = [MagicMock()]
        msg.photo[-1].file_id = "file_id"
        msg.photo[-1].file_unique_id = "unique_id"
        msg.answer = AsyncMock()
        msg.bot = MagicMock()

        with patch("bot.handlers.logo.save_logo_from_telegram",
                    new_callable=AsyncMock,
                    side_effect=ValueError("File too large")):
            await handle_logo_photo(msg)

        msg.answer.assert_called_once()
        assert "file too large" in msg.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_expired_pending_skips(self) -> None:
        """Photo sent after TTL expires should raise SkipHandler."""
        from aiogram.dispatcher.event.bases import SkipHandler

        from bot.handlers.logo import handle_logo_photo

        # Manually insert expired entry
        _pending_logo_uploads[55555] = ("t1", time.monotonic() - 400)

        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 55555
        msg.photo = [MagicMock()]
        msg.answer = AsyncMock()

        with pytest.raises(SkipHandler):
            await handle_logo_photo(msg)

        # Should not have tried to save
        msg.answer.assert_not_called()
