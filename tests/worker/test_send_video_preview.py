"""Tests for _send_video_preview — approval request + draft status tracking."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSendVideoPreviewApprovalTracking:
    """C1 fix: _send_video_preview must create approval_request + set status to previewing."""

    @pytest.mark.asyncio
    async def test_creates_approval_request_and_sets_previewing(self):
        """After sending video preview, should create approval_request and set draft to previewing."""
        mock_bot_instance = AsyncMock()
        mock_sent_message = MagicMock()
        mock_sent_message.message_id = 999
        mock_bot_instance.send_video = AsyncMock()
        mock_bot_instance.send_message = AsyncMock(return_value=mock_sent_message)
        mock_bot_instance.session = AsyncMock()

        with (
            patch("worker.jobs.generate_video.Bot", return_value=mock_bot_instance),
            patch("worker.jobs.generate_video.get_settings") as mock_settings,
            patch(
                "worker.jobs.generate_video.create_approval_request",
                new_callable=AsyncMock,
            ) as mock_create_approval,
            patch(
                "worker.jobs.generate_video.update_draft_status",
                new_callable=AsyncMock,
            ) as mock_update_status,
        ):
            mock_settings.return_value = MagicMock(telegram_bot_token="fake-token")

            from worker.jobs.generate_video import _send_video_preview

            await _send_video_preview(
                chat_id=12345,
                draft_id="draft-abc",
                video_url="https://cdn.kie.ai/vid.mp4",
                draft={
                    "id": "draft-abc",
                    "tenant_id": "tenant-xyz",
                    "caption_variants": [
                        {"text": "Caption 1"},
                        {"text": "Caption 2"},
                    ],
                },
                tenant_id="tenant-xyz",
            )

            mock_create_approval.assert_called_once_with(
                draft_id="draft-abc",
                tenant_id="tenant-xyz",
                telegram_message_id=999,
                telegram_chat_id=12345,
            )
            mock_update_status.assert_called_once_with("draft-abc", "previewing")

    @pytest.mark.asyncio
    async def test_no_approval_request_on_send_failure(self):
        """If sending fails, should NOT create approval request."""
        mock_bot_instance = AsyncMock()
        mock_bot_instance.send_video = AsyncMock(side_effect=Exception("Telegram down"))
        mock_bot_instance.send_message = AsyncMock()
        mock_bot_instance.session = AsyncMock()

        with (
            patch("worker.jobs.generate_video.Bot", return_value=mock_bot_instance),
            patch("worker.jobs.generate_video.get_settings") as mock_settings,
            patch(
                "worker.jobs.generate_video.create_approval_request",
                new_callable=AsyncMock,
            ) as mock_create_approval,
            patch(
                "worker.jobs.generate_video.update_draft_status",
                new_callable=AsyncMock,
            ) as mock_update_status,
        ):
            mock_settings.return_value = MagicMock(telegram_bot_token="fake-token")

            from worker.jobs.generate_video import _send_video_preview

            await _send_video_preview(
                chat_id=12345,
                draft_id="draft-abc",
                video_url="https://cdn.kie.ai/vid.mp4",
                draft={"id": "draft-abc", "tenant_id": "tenant-xyz", "caption_variants": []},
                tenant_id="tenant-xyz",
            )

            mock_create_approval.assert_not_called()
            mock_update_status.assert_not_called()
