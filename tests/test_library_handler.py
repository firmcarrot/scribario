"""Tests for /library command handler and keyboard builder."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestBuildLibraryKeyboard:
    """Tests for build_library_keyboard."""

    def test_single_item_no_nav_buttons(self):
        from bot.services.telegram import build_library_keyboard

        kb = build_library_keyboard(item_id="lib-1", current_offset=0, total_count=1)
        buttons = kb.inline_keyboard

        # Should have 2 rows: info row + action row
        all_text = [btn.text for row in buttons for btn in row]
        assert "Previous" not in all_text
        assert "Next" not in all_text
        assert "Post This" in all_text
        assert "Delete" in all_text

    def test_first_item_has_next_no_prev(self):
        from bot.services.telegram import build_library_keyboard

        kb = build_library_keyboard(item_id="lib-1", current_offset=0, total_count=3)
        all_text = [btn.text for row in kb.inline_keyboard for btn in row]

        assert "Next" in all_text
        assert "Previous" not in all_text

    def test_last_item_has_prev_no_next(self):
        from bot.services.telegram import build_library_keyboard

        kb = build_library_keyboard(item_id="lib-3", current_offset=2, total_count=3)
        all_text = [btn.text for row in kb.inline_keyboard for btn in row]

        assert "Previous" in all_text
        assert "Next" not in all_text

    def test_middle_item_has_both_nav(self):
        from bot.services.telegram import build_library_keyboard

        kb = build_library_keyboard(item_id="lib-2", current_offset=1, total_count=3)
        all_text = [btn.text for row in kb.inline_keyboard for btn in row]

        assert "Previous" in all_text
        assert "Next" in all_text

    def test_callback_data_format(self):
        from bot.services.telegram import build_library_keyboard

        kb = build_library_keyboard(item_id="lib-2", current_offset=1, total_count=3)
        all_buttons = [btn for row in kb.inline_keyboard for btn in row]

        callbacks = {btn.text: btn.callback_data for btn in all_buttons}
        assert callbacks["Previous"] == "lib_nav:0"
        assert callbacks["Next"] == "lib_nav:2"
        assert callbacks["Post This"] == "lib_post:lib-2"
        assert callbacks["Delete"] == "lib_delete:lib-2"

    def test_shows_position_indicator(self):
        from bot.services.telegram import build_library_keyboard

        kb = build_library_keyboard(item_id="lib-2", current_offset=1, total_count=5)
        all_text = [btn.text for row in kb.inline_keyboard for btn in row]

        assert "2 / 5" in all_text


class TestLibraryCommandHandler:
    """Tests for /library command."""

    @pytest.mark.asyncio
    async def test_empty_library_sends_message(self):
        with (
            patch("bot.handlers.library.get_tenant_by_telegram_user", new_callable=AsyncMock) as mock_tenant,
            patch("bot.handlers.library.get_library_items", new_callable=AsyncMock) as mock_items,
            patch("bot.handlers.library.count_library_items", new_callable=AsyncMock) as mock_count,
        ):
            mock_tenant.return_value = {"tenant_id": "t-1"}
            mock_items.return_value = []
            mock_count.return_value = 0

            from bot.handlers.library import handle_library_command

            message = AsyncMock()
            message.from_user = MagicMock(id=123)

            await handle_library_command(message)

            message.answer.assert_called_once()
            assert "empty" in message.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_shows_first_item_with_image(self):
        with (
            patch("bot.handlers.library.get_tenant_by_telegram_user", new_callable=AsyncMock) as mock_tenant,
            patch("bot.handlers.library.get_library_items", new_callable=AsyncMock) as mock_items,
            patch("bot.handlers.library.count_library_items", new_callable=AsyncMock) as mock_count,
            patch("bot.handlers.library.build_library_keyboard") as mock_kb,
        ):
            mock_tenant.return_value = {"tenant_id": "t-1"}
            mock_items.return_value = [{
                "id": "lib-1",
                "caption": "Great sauce!",
                "image_url": "https://img.com/1.jpg",
                "video_url": None,
                "media_type": "image",
            }]
            mock_count.return_value = 3
            mock_kb.return_value = MagicMock()

            from bot.handlers.library import handle_library_command

            message = AsyncMock()
            message.from_user = MagicMock(id=123)

            await handle_library_command(message)

            message.answer_photo.assert_called_once()
            call_kwargs = message.answer_photo.call_args
            assert "Great sauce!" in str(call_kwargs)

    @pytest.mark.asyncio
    async def test_shows_video_item(self):
        with (
            patch("bot.handlers.library.get_tenant_by_telegram_user", new_callable=AsyncMock) as mock_tenant,
            patch("bot.handlers.library.get_library_items", new_callable=AsyncMock) as mock_items,
            patch("bot.handlers.library.count_library_items", new_callable=AsyncMock) as mock_count,
            patch("bot.handlers.library.build_library_keyboard") as mock_kb,
        ):
            mock_tenant.return_value = {"tenant_id": "t-1"}
            mock_items.return_value = [{
                "id": "lib-1",
                "caption": "Video caption",
                "image_url": None,
                "video_url": "https://cdn.kie.ai/v.mp4",
                "media_type": "video",
            }]
            mock_count.return_value = 1
            mock_kb.return_value = MagicMock()

            from bot.handlers.library import handle_library_command

            message = AsyncMock()
            message.from_user = MagicMock(id=123)

            await handle_library_command(message)

            message.answer_video.assert_called_once()

    @pytest.mark.asyncio
    async def test_unregistered_user_gets_error(self):
        with patch(
            "bot.handlers.library.get_tenant_by_telegram_user",
            new_callable=AsyncMock,
            return_value=None,
        ):
            from bot.handlers.library import handle_library_command

            message = AsyncMock()
            message.from_user = MagicMock(id=999)

            await handle_library_command(message)

            message.answer.assert_called_once()
            assert "register" in message.answer.call_args[0][0].lower() or "set up" in message.answer.call_args[0][0].lower()


class TestLibPostCallback:
    """Tests for lib_post callback — posting from library."""

    @pytest.mark.asyncio
    async def test_post_enqueues_job_and_updates_status(self):
        with (
            patch("bot.handlers.library.get_tenant_by_telegram_user", new_callable=AsyncMock) as mock_tenant,
            patch("bot.handlers.library.get_library_item", new_callable=AsyncMock) as mock_item,
            patch("bot.handlers.library.create_posting_job", new_callable=AsyncMock) as mock_create_job,
            patch("bot.handlers.library.enqueue_job", new_callable=AsyncMock) as mock_enqueue,
            patch("bot.handlers.library.update_library_item_status", new_callable=AsyncMock) as mock_update,
        ):
            mock_tenant.return_value = {"tenant_id": "t-1"}
            mock_item.return_value = {
                "id": "lib-1",
                "tenant_id": "t-1",
                "caption": "Saved caption",
                "image_url": "https://img.com/1.jpg",
                "video_url": None,
                "media_type": "image",
                "platform_targets": ["facebook"],
                "status": "saved",
            }
            mock_create_job.return_value = {"id": "job-1"}

            from bot.handlers.library import handle_lib_post

            callback = AsyncMock()
            callback.data = "lib_post:lib-1"
            callback.from_user = MagicMock(id=123)
            callback.message = AsyncMock()

            await handle_lib_post(callback)

            mock_create_job.assert_called_once()
            mock_enqueue.assert_called_once()
            mock_update.assert_called_once_with("lib-1", tenant_id="t-1", status="posted")
            callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_already_posted_item(self):
        with (
            patch("bot.handlers.library.get_tenant_by_telegram_user", new_callable=AsyncMock) as mock_tenant,
            patch("bot.handlers.library.get_library_item", new_callable=AsyncMock) as mock_item,
        ):
            mock_tenant.return_value = {"tenant_id": "t-1"}
            mock_item.return_value = {
                "id": "lib-1",
                "tenant_id": "t-1",
                "status": "posted",
            }

            from bot.handlers.library import handle_lib_post

            callback = AsyncMock()
            callback.data = "lib_post:lib-1"
            callback.from_user = MagicMock(id=123)

            await handle_lib_post(callback)

            callback.answer.assert_called_once()
            assert "already" in callback.answer.call_args[0][0].lower()


class TestLibDeleteCallback:
    """Tests for lib_delete callback."""

    @pytest.mark.asyncio
    async def test_delete_marks_item_deleted(self):
        with (
            patch("bot.handlers.library.get_tenant_by_telegram_user", new_callable=AsyncMock) as mock_tenant,
            patch("bot.handlers.library.get_library_item", new_callable=AsyncMock) as mock_item,
            patch("bot.handlers.library.update_library_item_status", new_callable=AsyncMock) as mock_update,
            patch("bot.handlers.library.get_library_items", new_callable=AsyncMock) as mock_items,
            patch("bot.handlers.library.count_library_items", new_callable=AsyncMock) as mock_count,
        ):
            mock_tenant.return_value = {"tenant_id": "t-1"}
            mock_item.return_value = {
                "id": "lib-1",
                "tenant_id": "t-1",
                "status": "saved",
            }
            mock_items.return_value = []
            mock_count.return_value = 0

            from bot.handlers.library import handle_lib_delete

            callback = AsyncMock()
            callback.data = "lib_delete:lib-1"
            callback.from_user = MagicMock(id=123)
            callback.message = AsyncMock()

            await handle_lib_delete(callback)

            mock_update.assert_called_once_with("lib-1", tenant_id="t-1", status="deleted")
