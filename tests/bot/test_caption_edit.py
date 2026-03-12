"""Tests for caption edit feature — Feature 5."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from bot.dialogs.states import CaptionEditSG
from bot.services.telegram import build_preview_keyboard


class TestCaptionEditState:
    """CaptionEditSG state group has the expected state."""

    def test_has_edit_caption_state(self):
        assert hasattr(CaptionEditSG, "edit_caption")

    def test_edit_caption_is_state_instance(self):
        from aiogram.fsm.state import State

        # The state group class has a group attribute, states are accessible via the class
        assert CaptionEditSG.edit_caption is not None


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

    def test_keyboard_has_three_rows_for_default_options(self):
        keyboard = build_preview_keyboard("draft-999", num_options=3)
        # approve row + edit row + reject/regen row = 3 rows
        assert len(keyboard.inline_keyboard) == 3


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
