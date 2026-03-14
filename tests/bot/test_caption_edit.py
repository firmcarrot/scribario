"""Tests for caption edit feature — Feature 5."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.dialogs.states import CaptionEditSG
from bot.services.telegram import build_preview_keyboard


class TestCaptionEditState:
    """CaptionEditSG state group has the expected state."""

    def test_has_waiting_for_edit_instruction_state(self):
        assert hasattr(CaptionEditSG, "waiting_for_edit_instruction")

    def test_waiting_for_edit_instruction_is_state_instance(self):
        assert CaptionEditSG.waiting_for_edit_instruction is not None


class TestBuildPreviewKeyboardEditButtons:
    """build_preview_keyboard includes edit buttons."""

    def test_keyboard_contains_edit_buttons_for_each_option(self):
        keyboard = build_preview_keyboard("draft-123", num_options=3)
        all_button_texts = [
            btn.text for row in keyboard.inline_keyboard for btn in row
        ]
        assert "✏️ Edit #1" in all_button_texts
        assert "✏️ Edit #2" in all_button_texts
        assert "✏️ Edit #3" in all_button_texts

    def test_edit_button_callback_data_format(self):
        keyboard = build_preview_keyboard("draft-abc", num_options=2)
        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        edit_buttons = [b for b in all_buttons if b.text.startswith("✏️ Edit")]
        assert any(b.callback_data == "edit:draft-abc:1" for b in edit_buttons)
        assert any(b.callback_data == "edit:draft-abc:2" for b in edit_buttons)

    def test_edit_row_inserted_after_approve_row(self):
        keyboard = build_preview_keyboard("draft-xyz", num_options=2)
        rows = keyboard.inline_keyboard
        # Row 0: approve buttons, Row 1: edit buttons, Row 2: reject/regen
        assert all(btn.text.startswith("Approve") for btn in rows[0])
        assert all(btn.text.startswith("✏️ Edit") for btn in rows[1])

    def test_keyboard_has_five_rows_for_default_options(self):
        keyboard = build_preview_keyboard("draft-999", num_options=3)
        # approve row + edit row + regen_image row + video row + reject/regen row = 5 rows
        assert len(keyboard.inline_keyboard) == 5


class TestUpdateDraftCaption:
    """update_draft_caption read-modify-write pattern."""

    @pytest.mark.asyncio
    async def test_updates_caption_at_correct_index(self):
        """update_draft_caption should write new text at the specified index."""
        existing_variants = [
            {"text": "Original caption one", "platform": "facebook"},
            {"text": "Original caption two", "platform": "instagram"},
        ]

        content_drafts_mock = MagicMock()
        content_drafts_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"caption_variants": existing_variants}]
        )

        # Capture what update() is called with
        update_chain = MagicMock()
        update_chain.eq.return_value.execute.return_value = MagicMock()
        content_drafts_mock.update.return_value = update_chain

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = content_drafts_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import update_draft_caption

            await update_draft_caption("draft-123", 0, "New caption one")

        # Verify update was called with the full updated list
        content_drafts_mock.update.assert_called_once()
        call_args = content_drafts_mock.update.call_args[0][0]
        updated = call_args["caption_variants"]
        assert updated[0]["text"] == "New caption one"
        assert updated[1]["text"] == "Original caption two"  # unchanged

    @pytest.mark.asyncio
    async def test_updates_second_variant_leaves_first_unchanged(self):
        existing_variants = [
            {"text": "Caption A"},
            {"text": "Caption B"},
            {"text": "Caption C"},
        ]

        content_drafts_mock = MagicMock()
        content_drafts_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"caption_variants": existing_variants}]
        )
        update_chain = MagicMock()
        update_chain.eq.return_value.execute.return_value = MagicMock()
        content_drafts_mock.update.return_value = update_chain

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = content_drafts_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import update_draft_caption

            await update_draft_caption("draft-456", 2, "New Caption C")

        call_args = content_drafts_mock.update.call_args[0][0]
        updated = call_args["caption_variants"]
        assert updated[0]["text"] == "Caption A"
        assert updated[1]["text"] == "Caption B"
        assert updated[2]["text"] == "New Caption C"

    @pytest.mark.asyncio
    async def test_raises_value_error_when_draft_not_found(self):
        content_drafts_mock = MagicMock()
        content_drafts_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = content_drafts_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import update_draft_caption

            with pytest.raises(ValueError, match="not found"):
                await update_draft_caption("nonexistent-draft", 0, "anything")

    @pytest.mark.asyncio
    async def test_raises_index_error_for_out_of_range_index(self):
        existing_variants = [{"text": "Only one"}]

        content_drafts_mock = MagicMock()
        content_drafts_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"caption_variants": existing_variants}]
        )

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = content_drafts_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import update_draft_caption

            with pytest.raises(IndexError):
                await update_draft_caption("draft-789", 5, "boom")


class TestHandleEditInstruction:
    """handle_edit_instruction calls revise_caption and sends re-preview."""

    def _make_draft(self, draft_id: str = "draft-123", tenant_id: str = "tenant-abc") -> dict:
        return {
            "id": draft_id,
            "tenant_id": tenant_id,
            "caption_variants": [
                {"text": "Caption option 1"},
                {"text": "Caption option 2"},
            ],
            "image_urls": ["https://img.example.com/1.jpg", "https://img.example.com/2.jpg"],
        }

    @pytest.mark.asyncio
    async def test_calls_revise_caption_with_instruction(self):
        """handle_edit_instruction passes the instruction to revise_caption."""
        from bot.handlers.caption_edit import handle_edit_instruction

        message = MagicMock()
        message.text = "make it shorter"
        message.answer = AsyncMock()
        message.answer_photo = AsyncMock()

        state = AsyncMock()
        state.get_data = AsyncMock(return_value={"draft_id": "draft-123", "option_idx": 0})

        draft = self._make_draft()

        with (
            patch("bot.handlers.caption_edit.get_draft", AsyncMock(return_value=draft)),
            patch("bot.handlers.caption_edit.get_tenant_by_telegram_user", AsyncMock(return_value={"tenant_id": "tenant-abc"})),
            patch("bot.handlers.caption_edit.load_brand_profile", AsyncMock(return_value=MagicMock())),
            patch("bot.handlers.caption_edit.load_few_shot_examples", AsyncMock(return_value=[])),
            patch("bot.handlers.caption_edit.revise_caption", AsyncMock(return_value="Short! 🔥")) as mock_revise,
            patch("bot.handlers.caption_edit.update_draft_caption", AsyncMock()),
        ):
            await handle_edit_instruction(message, state)

        mock_revise.assert_called_once()
        call_kwargs = mock_revise.call_args
        assert call_kwargs[1]["instruction"] == "make it shorter" or call_kwargs[0][1] == "make it shorter"

    @pytest.mark.asyncio
    async def test_revised_caption_appears_in_re_preview(self):
        """The revised caption text is included in the bot's reply."""
        from bot.handlers.caption_edit import handle_edit_instruction

        message = MagicMock()
        message.text = "add emojis"
        message.answer = AsyncMock()
        message.answer_photo = AsyncMock()

        state = AsyncMock()
        state.get_data = AsyncMock(return_value={"draft_id": "draft-123", "option_idx": 0})

        draft = self._make_draft()

        with (
            patch("bot.handlers.caption_edit.get_draft", AsyncMock(return_value=draft)),
            patch("bot.handlers.caption_edit.get_tenant_by_telegram_user", AsyncMock(return_value={"tenant_id": "tenant-abc"})),
            patch("bot.handlers.caption_edit.load_brand_profile", AsyncMock(return_value=MagicMock())),
            patch("bot.handlers.caption_edit.load_few_shot_examples", AsyncMock(return_value=[])),
            patch("bot.handlers.caption_edit.revise_caption", AsyncMock(return_value="Caption with emojis 🔥🌶️")),
            patch("bot.handlers.caption_edit.update_draft_caption", AsyncMock()),
        ):
            await handle_edit_instruction(message, state)

        # Check that the revised caption appears somewhere in the sent message
        all_calls = message.answer_photo.call_args_list + message.answer.call_args_list
        all_text = " ".join(
            str(c) for c in all_calls
        )
        assert "Caption with emojis 🔥🌶️" in all_text

    @pytest.mark.asyncio
    async def test_re_preview_has_post_edit_again_cancel_buttons(self):
        """Re-preview keyboard has Post it, Edit Again, and Cancel buttons."""
        from bot.handlers.caption_edit import handle_edit_instruction

        message = MagicMock()
        message.text = "stronger CTA"
        message.answer = AsyncMock()
        message.answer_photo = AsyncMock()

        state = AsyncMock()
        state.get_data = AsyncMock(return_value={"draft_id": "draft-123", "option_idx": 1})

        draft = self._make_draft()

        with (
            patch("bot.handlers.caption_edit.get_draft", AsyncMock(return_value=draft)),
            patch("bot.handlers.caption_edit.get_tenant_by_telegram_user", AsyncMock(return_value={"tenant_id": "tenant-abc"})),
            patch("bot.handlers.caption_edit.load_brand_profile", AsyncMock(return_value=MagicMock())),
            patch("bot.handlers.caption_edit.load_few_shot_examples", AsyncMock(return_value=[])),
            patch("bot.handlers.caption_edit.revise_caption", AsyncMock(return_value="Revised!")),
            patch("bot.handlers.caption_edit.update_draft_caption", AsyncMock()),
        ):
            await handle_edit_instruction(message, state)

        # Find the keyboard from the answer_photo or answer call
        keyboard = None
        if message.answer_photo.called:
            keyboard = message.answer_photo.call_args[1].get("reply_markup")
        elif message.answer.called:
            keyboard = message.answer.call_args[1].get("reply_markup")

        assert keyboard is not None
        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        button_texts = [b.text for b in all_buttons]
        assert "✅ Post it" in button_texts
        assert "✏️ Edit Again" in button_texts
        assert "❌ Discard" in button_texts

    @pytest.mark.asyncio
    async def test_empty_instruction_asks_to_retry(self):
        """Empty instruction message prompts user to try again."""
        from bot.handlers.caption_edit import handle_edit_instruction

        message = MagicMock()
        message.text = "   "  # whitespace only
        message.answer = AsyncMock()

        state = AsyncMock()
        state.get_data = AsyncMock(return_value={"draft_id": "draft-123", "option_idx": 0})

        await handle_edit_instruction(message, state)

        message.answer.assert_called_once()
        assert "try again" in message.answer.call_args[0][0].lower() or \
               "empty" in message.answer.call_args[0][0].lower()
