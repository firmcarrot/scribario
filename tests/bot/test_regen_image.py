"""Tests for image-only regeneration — Feature: regen_image:{draft_id}:{option_idx}."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.services.telegram import build_preview_keyboard


class TestRegenImageButton:
    """build_preview_keyboard includes regen_image buttons."""

    def test_keyboard_contains_regen_image_buttons(self):
        keyboard = build_preview_keyboard("draft-123", num_options=3)
        all_button_texts = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert "🖼️ New Image #1" in all_button_texts
        assert "🖼️ New Image #2" in all_button_texts
        assert "🖼️ New Image #3" in all_button_texts

    def test_regen_image_callback_data_format(self):
        keyboard = build_preview_keyboard("draft-abc", num_options=2)
        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        regen_buttons = [b for b in all_buttons if "New Image" in b.text]
        assert any(b.callback_data == "regen_image:draft-abc:1" for b in regen_buttons)
        assert any(b.callback_data == "regen_image:draft-abc:2" for b in regen_buttons)

    def test_keyboard_row_order(self):
        keyboard = build_preview_keyboard("draft-xyz", num_options=2)
        rows = keyboard.inline_keyboard
        # Row 0: approve, Row 1: edit, Row 2: regen_image, Row 3: reject/regen
        assert all(btn.text.startswith("Approve") for btn in rows[0])
        assert all(btn.text.startswith("✏️ Edit") for btn in rows[1])
        assert all("New Image" in btn.text for btn in rows[2])

    def test_keyboard_has_four_rows_for_default_options(self):
        keyboard = build_preview_keyboard("draft-999", num_options=3)
        # approve + edit + regen_image + reject/regen = 4 rows
        assert len(keyboard.inline_keyboard) == 4


class TestHandleRegenImage:
    """handle_regen_image callback enqueues image-only regen job."""

    @pytest.mark.asyncio
    async def test_enqueues_regen_image_job(self):
        callback_mock = AsyncMock()
        callback_mock.data = "regen_image:draft-abc:1"
        callback_mock.from_user = MagicMock(id=12345)
        callback_mock.message = AsyncMock()
        callback_mock.message.chat.id = 99999

        draft = {
            "id": "draft-abc",
            "tenant_id": "tenant-xyz",
            "request_id": "req-111",
            "status": "previewing",
            "caption_variants": [
                {"text": "Caption 1", "visual_prompt": "shrimp on plate"},
                {"text": "Caption 2", "visual_prompt": "sauce bottle"},
                {"text": "Caption 3", "visual_prompt": "family dinner"},
            ],
            "image_urls": ["https://img1.com", "https://img2.com", "https://img3.com"],
        }
        membership = {"tenant_id": "tenant-xyz"}

        with (
            patch("bot.handlers.approval.get_draft", new_callable=AsyncMock, return_value=draft),
            patch("bot.handlers.approval.get_tenant_by_telegram_user", new_callable=AsyncMock, return_value=membership),
            patch("bot.handlers.approval.create_feedback_event", new_callable=AsyncMock),
            patch("bot.handlers.approval.enqueue_job", new_callable=AsyncMock) as mock_enqueue,
        ):
            from bot.handlers.approval import handle_regen_image
            await handle_regen_image(callback_mock)

        mock_enqueue.assert_called_once()
        call_kwargs = mock_enqueue.call_args.kwargs
        assert call_kwargs["job_type"] == "regen_image"
        payload = call_kwargs["payload"]
        assert payload["draft_id"] == "draft-abc"
        assert payload["option_idx"] == 0  # 1-indexed → 0-indexed
        assert payload["visual_prompt"] == "shrimp on plate"

    @pytest.mark.asyncio
    async def test_invalid_option_number_returns_early(self):
        callback_mock = AsyncMock()
        callback_mock.data = "regen_image:draft-abc:notanumber"
        callback_mock.from_user = MagicMock(id=12345)

        with patch("bot.handlers.approval.get_draft", new_callable=AsyncMock):
            from bot.handlers.approval import handle_regen_image
            await handle_regen_image(callback_mock)

        callback_mock.answer.assert_called()

    @pytest.mark.asyncio
    async def test_already_approved_draft_returns_early(self):
        callback_mock = AsyncMock()
        callback_mock.data = "regen_image:draft-abc:1"
        callback_mock.from_user = MagicMock(id=12345)
        callback_mock.message = AsyncMock()

        draft = {
            "id": "draft-abc",
            "tenant_id": "tenant-xyz",
            "status": "approved",
            "caption_variants": [{"text": "C1", "visual_prompt": "img"}],
            "image_urls": [],
        }
        membership = {"tenant_id": "tenant-xyz"}

        with (
            patch("bot.handlers.approval.get_draft", new_callable=AsyncMock, return_value=draft),
            patch("bot.handlers.approval.get_tenant_by_telegram_user", new_callable=AsyncMock, return_value=membership),
            patch("bot.handlers.approval.create_feedback_event", new_callable=AsyncMock),
            patch("bot.handlers.approval.enqueue_job", new_callable=AsyncMock) as mock_enqueue,
        ):
            from bot.handlers.approval import handle_regen_image
            await handle_regen_image(callback_mock)

        mock_enqueue.assert_not_called()
