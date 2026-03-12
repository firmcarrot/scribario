"""Tests for regen_image worker job."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestHandleRegenImage:
    """handle_regen_image_job updates draft image_urls and sends updated preview."""

    @pytest.mark.asyncio
    async def test_generates_new_image_and_updates_draft(self):
        """After regen, image_urls[option_idx] is replaced with the new URL."""
        draft = {
            "id": "draft-abc",
            "tenant_id": "tenant-xyz",
            "caption_variants": [
                {"text": "Cap 1", "visual_prompt": "shrimp dish"},
                {"text": "Cap 2", "visual_prompt": "sauce bottle"},
            ],
            "image_urls": ["https://old1.com", "https://old2.com"],
        }

        content_drafts_mock = MagicMock()
        content_drafts_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[draft]
        )
        update_chain = MagicMock()
        update_chain.eq.return_value.execute.return_value = MagicMock()
        content_drafts_mock.update.return_value = update_chain

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = content_drafts_mock

        mock_image_result = MagicMock()
        mock_image_result.url = "https://new1.com"
        mock_image_result.provider = "kie_ai"
        mock_image_result.cost_usd = 0.01

        with (
            patch("bot.db.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.regen_image.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.regen_image.ImageGenerationService") as mock_svc_class,
            patch("worker.jobs.regen_image.log_usage_event", new_callable=AsyncMock),
            patch("worker.jobs.regen_image.Bot") as mock_bot_class,
            patch("worker.jobs.regen_image.get_settings") as mock_settings,
        ):
            mock_settings.return_value.telegram_bot_token = "fake-token"
            mock_svc = AsyncMock()
            mock_svc_class.return_value = mock_svc
            mock_svc.generate = AsyncMock(return_value=mock_image_result)

            mock_bot = AsyncMock()
            mock_bot_class.return_value = mock_bot

            from worker.jobs.regen_image import handle_regen_image_job

            await handle_regen_image_job({
                "draft_id": "draft-abc",
                "tenant_id": "tenant-xyz",
                "option_idx": 0,
                "visual_prompt": "shrimp dish",
                "telegram_chat_id": 12345,
            })

        # Verify update was called with new URL at index 0
        content_drafts_mock.update.assert_called_once()
        updated_data = content_drafts_mock.update.call_args[0][0]
        assert updated_data["image_urls"][0] == "https://new1.com"
        assert updated_data["image_urls"][1] == "https://old2.com"  # unchanged

    @pytest.mark.asyncio
    async def test_sends_telegram_message_with_new_image(self):
        """After regeneration, a Telegram message is sent with the new image."""
        draft = {
            "id": "draft-abc",
            "tenant_id": "tenant-xyz",
            "caption_variants": [{"text": "Cap 1", "visual_prompt": "shrimp dish"}],
            "image_urls": ["https://old1.com"],
        }

        content_drafts_mock = MagicMock()
        content_drafts_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[draft]
        )
        content_drafts_mock.update.return_value.eq.return_value.execute.return_value = MagicMock()

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = content_drafts_mock

        mock_image_result = MagicMock()
        mock_image_result.url = "https://newimg.com"
        mock_image_result.provider = "kie_ai"
        mock_image_result.cost_usd = 0.01

        mock_bot = AsyncMock()

        with (
            patch("bot.db.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.regen_image.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.regen_image.ImageGenerationService") as mock_svc_class,
            patch("worker.jobs.regen_image.log_usage_event", new_callable=AsyncMock),
            patch("worker.jobs.regen_image.Bot", return_value=mock_bot),
            patch("worker.jobs.regen_image.get_settings") as mock_settings,
        ):
            mock_settings.return_value.telegram_bot_token = "fake-token"
            mock_svc = AsyncMock()
            mock_svc_class.return_value = mock_svc
            mock_svc.generate = AsyncMock(return_value=mock_image_result)

            from worker.jobs.regen_image import handle_regen_image_job

            await handle_regen_image_job({
                "draft_id": "draft-abc",
                "tenant_id": "tenant-xyz",
                "option_idx": 0,
                "visual_prompt": "shrimp dish",
                "telegram_chat_id": 12345,
            })

        mock_bot.send_photo.assert_called_once()
        call_kwargs = mock_bot.send_photo.call_args.kwargs
        assert call_kwargs["chat_id"] == 12345
        assert call_kwargs["photo"] == "https://newimg.com"

    @pytest.mark.asyncio
    async def test_no_telegram_message_when_no_chat_id(self):
        """When telegram_chat_id is absent, no bot message is sent."""
        draft = {
            "id": "draft-abc",
            "tenant_id": "tenant-xyz",
            "caption_variants": [{"text": "Cap 1", "visual_prompt": "shrimp dish"}],
            "image_urls": ["https://old1.com"],
        }

        content_drafts_mock = MagicMock()
        content_drafts_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[draft]
        )
        content_drafts_mock.update.return_value.eq.return_value.execute.return_value = MagicMock()

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = content_drafts_mock

        mock_image_result = MagicMock()
        mock_image_result.url = "https://newimg.com"
        mock_image_result.provider = "kie_ai"
        mock_image_result.cost_usd = 0.01

        mock_bot = AsyncMock()

        with (
            patch("bot.db.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.regen_image.get_supabase_client", return_value=supabase_mock),
            patch("worker.jobs.regen_image.ImageGenerationService") as mock_svc_class,
            patch("worker.jobs.regen_image.log_usage_event", new_callable=AsyncMock),
            patch("worker.jobs.regen_image.Bot", return_value=mock_bot),
            patch("worker.jobs.regen_image.get_settings") as mock_settings,
        ):
            mock_settings.return_value.telegram_bot_token = "fake-token"
            mock_svc = AsyncMock()
            mock_svc_class.return_value = mock_svc
            mock_svc.generate = AsyncMock(return_value=mock_image_result)

            from worker.jobs.regen_image import handle_regen_image_job

            await handle_regen_image_job({
                "draft_id": "draft-abc",
                "tenant_id": "tenant-xyz",
                "option_idx": 0,
                "visual_prompt": "shrimp dish",
            })

        mock_bot.send_photo.assert_not_called()
