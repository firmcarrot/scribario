"""Tests for auto-save unchosen options to content library."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestSaveUnchosenToLibrary:
    """Tests for _save_unchosen_to_library helper."""

    @pytest.mark.asyncio
    async def test_saves_unchosen_options_on_approve_option_2(self):
        """Approving option 2 saves options 1 and 3."""
        with patch(
            "bot.handlers.approval.save_to_content_library",
            new_callable=AsyncMock,
        ) as mock_save:
            from bot.handlers.approval import _save_unchosen_to_library

            draft = {
                "id": "draft-1",
                "tenant_id": "t-1",
                "caption_variants": [
                    {"text": "Caption A"},
                    {"text": "Caption B"},
                    {"text": "Caption C"},
                ],
                "image_urls": [
                    "https://img.com/a.jpg",
                    "https://img.com/b.jpg",
                    "https://img.com/c.jpg",
                ],
                "video_url": None,
            }

            await _save_unchosen_to_library(draft, chosen_idx=1, platform_targets=["facebook"])

            assert mock_save.call_count == 2
            # First call: option 0 (Caption A)
            call_0 = mock_save.call_args_list[0]
            assert call_0.kwargs["caption"] == "Caption A"
            assert call_0.kwargs["image_url"] == "https://img.com/a.jpg"
            assert call_0.kwargs["tenant_id"] == "t-1"
            assert call_0.kwargs["media_type"] == "image"
            # Second call: option 2 (Caption C)
            call_1 = mock_save.call_args_list[1]
            assert call_1.kwargs["caption"] == "Caption C"
            assert call_1.kwargs["image_url"] == "https://img.com/c.jpg"

    @pytest.mark.asyncio
    async def test_saves_unchosen_on_approve_option_1(self):
        """Approving option 1 (idx=0) saves options 2 and 3."""
        with patch(
            "bot.handlers.approval.save_to_content_library",
            new_callable=AsyncMock,
        ) as mock_save:
            from bot.handlers.approval import _save_unchosen_to_library

            draft = {
                "id": "draft-1",
                "tenant_id": "t-1",
                "caption_variants": [
                    {"text": "A"},
                    {"text": "B"},
                    {"text": "C"},
                ],
                "image_urls": ["https://a.jpg", "https://b.jpg", "https://c.jpg"],
                "video_url": None,
            }

            await _save_unchosen_to_library(draft, chosen_idx=0, platform_targets=None)

            assert mock_save.call_count == 2
            assert mock_save.call_args_list[0].kwargs["caption"] == "B"
            assert mock_save.call_args_list[1].kwargs["caption"] == "C"

    @pytest.mark.asyncio
    async def test_single_option_saves_nothing(self):
        """Only 1 option — nothing to save."""
        with patch(
            "bot.handlers.approval.save_to_content_library",
            new_callable=AsyncMock,
        ) as mock_save:
            from bot.handlers.approval import _save_unchosen_to_library

            draft = {
                "id": "draft-1",
                "tenant_id": "t-1",
                "caption_variants": [{"text": "Only one"}],
                "image_urls": ["https://only.jpg"],
                "video_url": None,
            }

            await _save_unchosen_to_library(draft, chosen_idx=0, platform_targets=None)

            mock_save.assert_not_called()

    @pytest.mark.asyncio
    async def test_video_draft_saves_with_video_url(self):
        """Video drafts save unchosen captions with the shared video_url."""
        with patch(
            "bot.handlers.approval.save_to_content_library",
            new_callable=AsyncMock,
        ) as mock_save:
            from bot.handlers.approval import _save_unchosen_to_library

            draft = {
                "id": "draft-1",
                "tenant_id": "t-1",
                "caption_variants": [
                    {"text": "Video cap A"},
                    {"text": "Video cap B"},
                    {"text": "Video cap C"},
                ],
                "image_urls": ["https://scene.jpg", "https://scene.jpg", "https://scene.jpg"],
                "video_url": "https://cdn.kie.ai/video.mp4",
            }

            await _save_unchosen_to_library(draft, chosen_idx=0, platform_targets=None)

            assert mock_save.call_count == 2
            for call in mock_save.call_args_list:
                assert call.kwargs["media_type"] == "video"
                assert call.kwargs["video_url"] == "https://cdn.kie.ai/video.mp4"

    @pytest.mark.asyncio
    async def test_image_urls_shorter_than_variants(self):
        """Handles gracefully when image_urls has fewer items than caption_variants."""
        with patch(
            "bot.handlers.approval.save_to_content_library",
            new_callable=AsyncMock,
        ) as mock_save:
            from bot.handlers.approval import _save_unchosen_to_library

            draft = {
                "id": "draft-1",
                "tenant_id": "t-1",
                "caption_variants": [{"text": "A"}, {"text": "B"}, {"text": "C"}],
                "image_urls": ["https://a.jpg"],  # Only 1 image for 3 captions
                "video_url": None,
            }

            await _save_unchosen_to_library(draft, chosen_idx=0, platform_targets=None)

            assert mock_save.call_count == 2
            # Option B (idx 1) has no image
            assert mock_save.call_args_list[0].kwargs["image_url"] is None
            # Option C (idx 2) has no image
            assert mock_save.call_args_list[1].kwargs["image_url"] is None

    @pytest.mark.asyncio
    async def test_empty_caption_variants_saves_nothing(self):
        """No caption_variants — nothing to save."""
        with patch(
            "bot.handlers.approval.save_to_content_library",
            new_callable=AsyncMock,
        ) as mock_save:
            from bot.handlers.approval import _save_unchosen_to_library

            draft = {
                "id": "draft-1",
                "tenant_id": "t-1",
                "caption_variants": [],
                "image_urls": [],
                "video_url": None,
            }

            await _save_unchosen_to_library(draft, chosen_idx=0, platform_targets=None)

            mock_save.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_failure_does_not_raise(self):
        """Library save failure must not break the approval flow."""
        with patch(
            "bot.handlers.approval.save_to_content_library",
            new_callable=AsyncMock,
            side_effect=Exception("DB down"),
        ):
            from bot.handlers.approval import _save_unchosen_to_library

            draft = {
                "id": "draft-1",
                "tenant_id": "t-1",
                "caption_variants": [{"text": "A"}, {"text": "B"}],
                "image_urls": ["https://a.jpg", "https://b.jpg"],
                "video_url": None,
            }

            # Should NOT raise
            await _save_unchosen_to_library(draft, chosen_idx=0, platform_targets=None)

    @pytest.mark.asyncio
    async def test_propagates_platform_targets(self):
        """Platform targets from original request are saved."""
        with patch(
            "bot.handlers.approval.save_to_content_library",
            new_callable=AsyncMock,
        ) as mock_save:
            from bot.handlers.approval import _save_unchosen_to_library

            draft = {
                "id": "draft-1",
                "tenant_id": "t-1",
                "caption_variants": [{"text": "A"}, {"text": "B"}],
                "image_urls": ["https://a.jpg", "https://b.jpg"],
                "video_url": None,
            }

            await _save_unchosen_to_library(
                draft, chosen_idx=0, platform_targets=["instagram", "facebook"]
            )

            assert mock_save.call_args_list[0].kwargs["platform_targets"] == [
                "instagram",
                "facebook",
            ]
