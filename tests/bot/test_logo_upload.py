"""Tests for the /logo command and logo upload flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.logo import _pending_logo_uploads, router


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
        assert 12345 in _pending_logo_uploads

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
        assert 99999 not in _pending_logo_uploads


class TestLogoPhotoHandler:
    @pytest.mark.asyncio
    async def test_stores_logo_and_updates_db(self) -> None:
        from bot.handlers.logo import handle_logo_photo

        _pending_logo_uploads[12345] = "t1"

        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 12345
        msg.photo = [MagicMock(), MagicMock(), MagicMock()]
        msg.photo[-1].file_id = "big_photo_file_id"
        msg.photo[-1].file_unique_id = "big_photo_unique"
        msg.answer = AsyncMock()

        with (
            patch("bot.handlers.logo.get_settings") as mock_settings,
            patch("bot.handlers.logo.save_logo_from_telegram",
                  new_callable=AsyncMock,
                  return_value="reference-photos/t1/logo_big_photo_unique.jpg") as mock_save,
        ):
            mock_settings.return_value.telegram_bot_token = "test-token"
            await handle_logo_photo(msg)

        mock_save.assert_called_once_with(
            bot_token="test-token",
            file_id="big_photo_file_id",
            file_unique_id="big_photo_unique",
            tenant_id="t1",
        )
        msg.answer.assert_called_once()
        assert "logo" in msg.answer.call_args[0][0].lower()
        assert 12345 not in _pending_logo_uploads

    @pytest.mark.asyncio
    async def test_ignores_photo_without_pending(self) -> None:
        from bot.handlers.logo import handle_logo_photo

        _pending_logo_uploads.clear()

        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 99999
        msg.photo = [MagicMock()]

        result = await handle_logo_photo(msg)

    @pytest.mark.asyncio
    async def test_handles_download_error(self) -> None:
        """Error during download/store should send error message, not crash."""
        from bot.handlers.logo import handle_logo_photo

        _pending_logo_uploads[77777] = "t2"

        msg = MagicMock()
        msg.from_user = MagicMock()
        msg.from_user.id = 77777
        msg.photo = [MagicMock()]
        msg.photo[-1].file_id = "file_id"
        msg.photo[-1].file_unique_id = "unique_id"
        msg.answer = AsyncMock()

        with (
            patch("bot.handlers.logo.get_settings") as mock_settings,
            patch("bot.handlers.logo.save_logo_from_telegram",
                  new_callable=AsyncMock,
                  side_effect=RuntimeError("Telegram API down")),
        ):
            mock_settings.return_value.telegram_bot_token = "test-token"
            await handle_logo_photo(msg)

        msg.answer.assert_called_once()
        assert "wrong" in msg.answer.call_args[0][0].lower()
        assert 77777 not in _pending_logo_uploads
