"""Tests for bot.services.telegram module."""

from bot.services.telegram import build_preview_caption, build_preview_keyboard


class TestBuildPreviewKeyboard:
    def test_has_per_option_approve_buttons(self):
        kb = build_preview_keyboard("draft-123", num_options=3)
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        approve_btns = [b for b in buttons if (b.callback_data or "").startswith("approve:")]
        assert len(approve_btns) == 3
        assert approve_btns[0].callback_data == "approve:draft-123:1"
        assert approve_btns[1].callback_data == "approve:draft-123:2"
        assert approve_btns[2].callback_data == "approve:draft-123:3"

    def test_approve_button_labels(self):
        kb = build_preview_keyboard("draft-123", num_options=3)
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        approve_btns = [b for b in buttons if (b.callback_data or "").startswith("approve:")]
        assert approve_btns[0].text == "Approve #1"
        assert approve_btns[1].text == "Approve #2"
        assert approve_btns[2].text == "Approve #3"

    def test_has_reject_button(self):
        kb = build_preview_keyboard("draft-123")
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        reject_btns = [b for b in buttons if b.callback_data == "reject:draft-123"]
        assert len(reject_btns) == 1
        assert reject_btns[0].text == "Reject All"

    def test_has_regenerate_button(self):
        kb = build_preview_keyboard("draft-123")
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        regen_btns = [b for b in buttons if b.callback_data == "regen:draft-123"]
        assert len(regen_btns) == 1

    def test_draft_id_in_callback_data(self):
        kb = build_preview_keyboard("my-unique-id")
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert all("my-unique-id" in (btn.callback_data or "") for btn in buttons)

    def test_single_option(self):
        kb = build_preview_keyboard("draft-1", num_options=1)
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        approve_btns = [b for b in buttons if (b.callback_data or "").startswith("approve:")]
        assert len(approve_btns) == 1
        assert approve_btns[0].callback_data == "approve:draft-1:1"


class TestBuildPreviewCaption:
    def test_includes_caption_text(self):
        result = build_preview_caption("Buy our sauce!", ["instagram"])
        assert "Buy our sauce!" in result

    def test_includes_platform_names(self):
        result = build_preview_caption("Test", ["instagram", "facebook"])
        assert "Instagram" in result
        assert "Facebook" in result

    def test_includes_instructions(self):
        result = build_preview_caption("Test", ["instagram"])
        assert "Approve" in result
