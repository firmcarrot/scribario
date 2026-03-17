"""Tests for build_video_preview_keyboard in bot.services.telegram."""

from bot.services.telegram import build_video_preview_keyboard


class TestBuildVideoPreviewKeyboard:
    def test_has_per_option_approve_buttons(self):
        kb = build_video_preview_keyboard("draft-123", num_options=3)
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        approve_btns = [b for b in buttons if (b.callback_data or "").startswith("approve_video:")]
        assert len(approve_btns) == 3
        assert approve_btns[0].callback_data == "approve_video:draft-123:1"
        assert approve_btns[1].callback_data == "approve_video:draft-123:2"
        assert approve_btns[2].callback_data == "approve_video:draft-123:3"

    def test_approve_button_labels(self):
        kb = build_video_preview_keyboard("draft-123", num_options=3)
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        approve_btns = [b for b in buttons if (b.callback_data or "").startswith("approve_video:")]
        assert approve_btns[0].text == "Approve #1"
        assert approve_btns[1].text == "Approve #2"
        assert approve_btns[2].text == "Approve #3"

    def test_has_edit_buttons(self):
        kb = build_video_preview_keyboard("draft-123", num_options=2)
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        edit_btns = [b for b in buttons if (b.callback_data or "").startswith("edit:")]
        assert len(edit_btns) == 2

    def test_no_make_video_button(self):
        kb = build_video_preview_keyboard("draft-123", num_options=3)
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        video_btns = [b for b in buttons if "make_video" in (b.callback_data or "")]
        assert len(video_btns) == 0

    def test_no_new_image_buttons(self):
        kb = build_video_preview_keyboard("draft-123", num_options=3)
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        img_btns = [b for b in buttons if "regen_image" in (b.callback_data or "")]
        assert len(img_btns) == 0

    def test_has_reject_button(self):
        kb = build_video_preview_keyboard("draft-123")
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        reject_btns = [b for b in buttons if b.callback_data == "reject:draft-123"]
        assert len(reject_btns) == 1
        assert reject_btns[0].text == "Reject All"

    def test_has_regenerate_button(self):
        kb = build_video_preview_keyboard("draft-123")
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        regen_btns = [b for b in buttons if b.callback_data == "regen:draft-123"]
        assert len(regen_btns) == 1

    def test_single_option(self):
        kb = build_video_preview_keyboard("draft-1", num_options=1)
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        approve_btns = [b for b in buttons if (b.callback_data or "").startswith("approve_video:")]
        assert len(approve_btns) == 1
        assert approve_btns[0].callback_data == "approve_video:draft-1:1"

    def test_draft_id_in_all_callbacks(self):
        kb = build_video_preview_keyboard("my-unique-id")
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert all("my-unique-id" in (btn.callback_data or "") for btn in buttons)
