"""Tests for bot/handlers/photos.py — photo intake with album debounce and labeling."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_message(
    text: str | None = None,
    photo: list | None = None,
    media_group_id: str | None = None,
    user_id: int = 7560539974,
    chat_id: int = 7560539974,
    caption: str | None = None,
) -> MagicMock:
    """Build a fake aiogram Message."""
    msg = MagicMock()
    msg.from_user = MagicMock()
    msg.from_user.id = user_id
    msg.chat = MagicMock()
    msg.chat.id = chat_id
    msg.text = text
    msg.caption = caption
    msg.media_group_id = media_group_id

    if photo:
        photo_size = MagicMock()
        photo_size.file_id = "AgACtest123"
        photo_size.file_unique_id = "AQADtest_unique"
        photo_size.file_size = 50000
        msg.photo = [photo_size]
    else:
        msg.photo = None

    msg.answer = AsyncMock()
    msg.reply = AsyncMock()
    return msg


class TestPhotoWithTextIsGenerationRequest:
    """Photo + text = generate content using photo as reference."""

    @pytest.mark.asyncio
    async def test_photo_with_text_triggers_generation_flow(self):
        from bot.handlers.photos import handle_photo_message

        msg = _make_message(
            photo=["photo_data"],
            caption="put me eating mondo shrimp over a volcano, theme dangerously good",
        )
        membership = {"tenant_id": "tenant-uuid-123"}

        with (
            patch("bot.handlers.photos.get_tenant_by_telegram_user", return_value=membership),
            patch("bot.handlers.photos.download_and_store", new_callable=AsyncMock, return_value="ref-photos/t/u.jpg"),
            patch("bot.handlers.photos.create_content_request", new_callable=AsyncMock, return_value={"id": "req-1"}),
            patch("bot.handlers.photos.enqueue_job", new_callable=AsyncMock),
        ):
            await handle_photo_message(msg, bot=AsyncMock())

        # Should ack generation, not ask for label
        call_args = msg.answer.call_args[0][0]
        assert "generating" in call_args.lower() or "got it" in call_args.lower()

    @pytest.mark.asyncio
    async def test_photo_with_text_downloads_and_stores_photo(self):
        from bot.handlers.photos import handle_photo_message

        msg = _make_message(
            photo=["photo_data"],
            caption="post about our shrimp",
        )
        membership = {"tenant_id": "tenant-uuid-123"}
        mock_bot = AsyncMock()
        mock_bot.get_file = AsyncMock(return_value=MagicMock(file_path="photos/file.jpg"))

        with (
            patch("bot.handlers.photos.get_tenant_by_telegram_user", return_value=membership),
            patch("bot.handlers.photos.download_and_store", new_callable=AsyncMock, return_value="ref-photos/t/u.jpg") as mock_store,
            patch("bot.handlers.photos.create_content_request", new_callable=AsyncMock, return_value={"id": "req-1"}),
            patch("bot.handlers.photos.enqueue_job", new_callable=AsyncMock),
            patch("bot.handlers.photos.BOT_TOKEN", "test-token"),
        ):
            await handle_photo_message(msg, bot=mock_bot)

        mock_store.assert_called_once()


class TestPhotoWithoutTextShowsDisambiguation:
    """Photo without text = ask: Save as Reference or Create a Post."""

    @pytest.mark.asyncio
    async def test_photo_without_text_asks_what_to_do(self):
        from bot.handlers.photos import handle_photo_message

        msg = _make_message(photo=["photo_data"])
        membership = {"tenant_id": "tenant-uuid-123"}

        with patch("bot.handlers.photos.get_tenant_by_telegram_user", return_value=membership):
            await handle_photo_message(msg, bot=AsyncMock())

        msg.answer.assert_called_once()
        call_args = msg.answer.call_args
        # Should send reply_markup with inline buttons
        assert call_args.kwargs.get("reply_markup") is not None or (
            len(call_args.args) > 1 and call_args.args[1] is not None
        )

    @pytest.mark.asyncio
    async def test_photo_without_text_no_tenant_prompts_setup(self):
        from bot.handlers.photos import handle_photo_message

        msg = _make_message(photo=["photo_data"])

        with patch("bot.handlers.photos.get_tenant_by_telegram_user", return_value=None):
            await handle_photo_message(msg, bot=AsyncMock())

        msg.answer.assert_called_once()
        assert "start" in msg.answer.call_args[0][0].lower()


class TestLabelingCallback:
    """Callback when user taps Me/My Partner/My Product/Other."""

    @pytest.mark.asyncio
    async def test_label_me_saves_as_owner(self):
        import bot.handlers.photos as photos_mod
        from bot.handlers.photos import handle_label_callback

        # Pre-populate pending cache (simulates handle_save_reference_callback storing the photo)
        photos_mod._pending_photos["AQADtest"] = {
            "file_unique_id": "AQADtest_unique",
            "storage_path": "ref-photos/tenant/file.jpg",
        }

        mock_msg = MagicMock()
        mock_msg.edit_text = AsyncMock()

        callback = MagicMock()
        callback.from_user = MagicMock()
        callback.from_user.id = 7560539974
        callback.data = "photo_label:owner:AQADtest"
        callback.answer = AsyncMock()
        callback.message = mock_msg

        membership = {"tenant_id": "tenant-uuid-123"}

        with (
            patch("bot.handlers.photos._get_message", return_value=mock_msg),
            patch("bot.handlers.photos.get_tenant_by_telegram_user", return_value=membership),
            patch("bot.handlers.photos.create_reference_photo", new_callable=AsyncMock, return_value={"id": "photo-uuid"}),
            patch("bot.handlers.photos.count_reference_photos", new_callable=AsyncMock, return_value=1),
        ):
            await handle_label_callback(callback)

        callback.answer.assert_called_once()
        edit_call = mock_msg.edit_text.call_args[0][0]
        assert "saved" in edit_call.lower() or "owner" in edit_call.lower()

    @pytest.mark.asyncio
    async def test_label_product_saves_as_product(self):
        import bot.handlers.photos as photos_mod
        from bot.handlers.photos import handle_label_callback

        photos_mod._pending_photos["AQADtest"] = {
            "file_unique_id": "AQADtest_unique",
            "storage_path": "ref-photos/tenant/file.jpg",
        }

        mock_msg = MagicMock()
        mock_msg.edit_text = AsyncMock()

        callback = MagicMock()
        callback.from_user = MagicMock()
        callback.from_user.id = 7560539974
        callback.data = "photo_label:product:AQADtest"
        callback.answer = AsyncMock()
        callback.message = mock_msg

        membership = {"tenant_id": "tenant-uuid-123"}

        with (
            patch("bot.handlers.photos._get_message", return_value=mock_msg),
            patch("bot.handlers.photos.get_tenant_by_telegram_user", return_value=membership),
            patch("bot.handlers.photos.create_reference_photo", new_callable=AsyncMock, return_value={"id": "photo-uuid"}),
            patch("bot.handlers.photos.count_reference_photos", new_callable=AsyncMock, return_value=5),
        ):
            await handle_label_callback(callback)

        callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_at_limit_rejects_new_photo(self):
        import bot.handlers.photos as photos_mod
        from bot.db import MAX_PHOTOS_PER_TENANT
        from bot.handlers.photos import handle_label_callback

        photos_mod._pending_photos["AQADtest"] = {
            "file_unique_id": "AQADtest_unique",
            "storage_path": "ref-photos/tenant/file.jpg",
        }

        mock_msg = MagicMock()
        mock_msg.edit_text = AsyncMock()

        callback = MagicMock()
        callback.from_user = MagicMock()
        callback.from_user.id = 7560539974
        callback.data = "photo_label:owner:AQADtest"
        callback.answer = AsyncMock()
        callback.message = mock_msg

        membership = {"tenant_id": "tenant-uuid-123"}

        with (
            patch("bot.handlers.photos._get_message", return_value=mock_msg),
            patch("bot.handlers.photos.get_tenant_by_telegram_user", return_value=membership),
            patch("bot.handlers.photos.count_reference_photos", new_callable=AsyncMock, return_value=MAX_PHOTOS_PER_TENANT),
        ):
            await handle_label_callback(callback)

        edit_call = mock_msg.edit_text.call_args[0][0]
        assert "limit" in edit_call.lower() or "photos" in edit_call.lower()


class TestSaveAsReferenceCallback:
    """Callback when user taps 'Save as Reference' from disambiguation."""

    @pytest.mark.asyncio
    async def test_save_as_reference_asks_for_label(self):
        from bot.handlers.photos import handle_save_reference_callback

        mock_msg = MagicMock()
        mock_msg.edit_text = AsyncMock()

        callback = MagicMock()
        callback.from_user = MagicMock()
        callback.from_user.id = 7560539974
        callback.data = "photo_action:save:AQADtest_unique:AgACfile_id"
        callback.answer = AsyncMock()
        callback.message = mock_msg

        membership = {"tenant_id": "tenant-uuid-123"}
        mock_bot = AsyncMock()
        mock_bot.get_file = AsyncMock(return_value=MagicMock(file_path="photos/f.jpg"))

        with (
            patch("bot.handlers.photos._get_message", return_value=mock_msg),
            patch("bot.handlers.photos.get_tenant_by_telegram_user", return_value=membership),
            patch("bot.handlers.photos.count_reference_photos", new_callable=AsyncMock, return_value=0),
            patch("bot.handlers.photos.download_and_store", new_callable=AsyncMock, return_value="ref-photos/t/u.jpg"),
            patch("bot.handlers.photos.BOT_TOKEN", "test-token"),
        ):
            await handle_save_reference_callback(callback, bot=mock_bot)

        mock_msg.edit_text.assert_called_once()
        call_kwargs = mock_msg.edit_text.call_args
        assert call_kwargs.kwargs.get("reply_markup") is not None
