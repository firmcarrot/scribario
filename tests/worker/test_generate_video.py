"""Tests for worker.jobs.generate_video module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.brand_voice import BrandProfile
from pipeline.video_gen import VideoResult
from pipeline.video_prompt_gen import VideoPromptResult


def _default_patches():
    """Return common patches for generate_video handler tests."""
    return {
        "service_cls": patch("worker.jobs.generate_video.VideoGenerationService"),
        "log_usage": patch("worker.jobs.generate_video.log_usage_event", new_callable=AsyncMock),
        "get_draft": patch("worker.jobs.generate_video.get_draft", new_callable=AsyncMock),
        "update_url": patch("worker.jobs.generate_video.update_draft_video_url", new_callable=AsyncMock),
        "preview": patch("worker.jobs.generate_video._send_video_preview", new_callable=AsyncMock),
        "load_profile": patch("worker.jobs.generate_video.load_brand_profile", new_callable=AsyncMock),
        "gen_prompt": patch("worker.jobs.generate_video.generate_video_prompt", new_callable=AsyncMock),
        "decrement_credit": patch("bot.services.budget.decrement_video_credit", new_callable=AsyncMock),
    }


class TestHandleGenerateVideo:
    """Tests for the generate_video job handler."""

    @pytest.mark.asyncio
    async def test_text_to_video_basic_flow(self):
        """Happy path: text-to-video generates, stores, sends preview."""
        mock_video_result = VideoResult(
            url="https://cdn.kie.ai/video-123.mp4",
            provider="kie_ai_veo",
            cost_usd=0.40,
            metadata={"task_id": "task-123"},
        )

        patches = _default_patches()
        with (
            patches["service_cls"] as mock_service_cls,
            patches["log_usage"] as mock_log,
            patches["get_draft"] as mock_get_draft,
            patches["update_url"] as mock_update,
            patches["preview"] as mock_preview,
            patches["load_profile"] as mock_load_profile,
            patches["gen_prompt"] as mock_gen_prompt,
            patches["decrement_credit"],
        ):
            mock_service = AsyncMock()
            mock_service.generate = AsyncMock(return_value=mock_video_result)
            mock_service_cls.return_value = mock_service

            mock_load_profile.return_value = BrandProfile(
                tenant_id="tenant-1",
                name="Test Brand",
                tone_words=["bold"],
                audience_description="testers",
                do_list=[],
                dont_list=[],
            )
            mock_gen_prompt.return_value = VideoPromptResult(text="Cinematic close-up of hot sauce. Audio: sizzle.", input_tokens=500, output_tokens=100)

            mock_get_draft.return_value = {
                "id": "draft-1",
                "tenant_id": "tenant-1",
                "caption_variants": [{"text": "Great sauce!", "visual_prompt": "sauce vid"}],
                "image_urls": ["https://img.com/1.jpg"],
                "status": "previewing",
            }

            from worker.jobs.generate_video import handle_generate_video

            await handle_generate_video({
                "draft_id": "draft-1",
                "tenant_id": "tenant-1",
                "prompt": "showcase our hot sauce",
                "aspect_ratio": "16:9",
                "generation_type": "TEXT_2_VIDEO",
                "telegram_chat_id": 12345,
            })

            # Should use optimized prompt, not raw
            mock_service.generate.assert_called_once_with(
                "Cinematic close-up of hot sauce. Audio: sizzle.",
                aspect_ratio="16:9",
                generation_type="TEXT_2_VIDEO",
                image_urls=None,
            )
            mock_gen_prompt.assert_called_once()
            assert mock_log.call_count == 1  # prompt gen only (video gen logs via service)
            mock_update.assert_called_once_with("draft-1", "https://cdn.kie.ai/video-123.mp4")
            mock_preview.assert_called_once()

    @pytest.mark.asyncio
    async def test_reference_to_video_passes_image_urls(self):
        """REFERENCE_2_VIDEO passes image_urls to the provider."""
        mock_video_result = VideoResult(
            url="https://cdn.kie.ai/ref-video.mp4",
            provider="kie_ai_veo",
            cost_usd=0.40,
            metadata={"task_id": "task-ref"},
        )

        patches = _default_patches()
        with (
            patches["service_cls"] as mock_service_cls,
            patches["log_usage"],
            patches["get_draft"] as mock_get_draft,
            patches["update_url"],
            patches["preview"],
            patches["load_profile"] as mock_load_profile,
            patches["gen_prompt"] as mock_gen_prompt,
            patches["decrement_credit"],
        ):
            mock_service = AsyncMock()
            mock_service.generate = AsyncMock(return_value=mock_video_result)
            mock_service_cls.return_value = mock_service

            mock_load_profile.return_value = None  # triggers default profile
            mock_gen_prompt.return_value = VideoPromptResult(text="Optimized product showcase prompt.", input_tokens=500, output_tokens=100)

            mock_get_draft.return_value = {
                "id": "draft-1",
                "tenant_id": "tenant-1",
                "caption_variants": [{"text": "caption"}],
                "image_urls": ["https://img.com/1.jpg"],
                "status": "previewing",
            }

            from worker.jobs.generate_video import handle_generate_video

            await handle_generate_video({
                "draft_id": "draft-1",
                "tenant_id": "tenant-1",
                "prompt": "product showcase",
                "aspect_ratio": "16:9",
                "generation_type": "REFERENCE_2_VIDEO",
                "image_urls": ["https://img.com/product.jpg"],
                "telegram_chat_id": 12345,
            })

            mock_service.generate.assert_called_once_with(
                "Optimized product showcase prompt.",
                aspect_ratio="16:9",
                generation_type="REFERENCE_2_VIDEO",
                image_urls=["https://img.com/product.jpg"],
            )

    @pytest.mark.asyncio
    async def test_skips_preview_without_chat_id(self):
        """No telegram_chat_id → skip preview send."""
        mock_video_result = VideoResult(
            url="https://cdn.kie.ai/vid.mp4",
            provider="kie_ai_veo",
            cost_usd=0.40,
            metadata={},
        )

        patches = _default_patches()
        with (
            patches["service_cls"] as mock_service_cls,
            patches["log_usage"],
            patches["get_draft"] as mock_get_draft,
            patches["update_url"],
            patches["preview"] as mock_preview,
            patches["load_profile"] as mock_load_profile,
            patches["gen_prompt"] as mock_gen_prompt,
            patches["decrement_credit"],
        ):
            mock_service = AsyncMock()
            mock_service.generate = AsyncMock(return_value=mock_video_result)
            mock_service_cls.return_value = mock_service

            mock_load_profile.return_value = None
            mock_gen_prompt.return_value = VideoPromptResult(text="Optimized prompt.", input_tokens=500, output_tokens=100)

            mock_get_draft.return_value = {
                "id": "draft-1",
                "tenant_id": "tenant-1",
                "caption_variants": [],
                "image_urls": [],
                "status": "generated",
            }

            from worker.jobs.generate_video import handle_generate_video

            await handle_generate_video({
                "draft_id": "draft-1",
                "tenant_id": "tenant-1",
                "prompt": "sauce video",
                "aspect_ratio": "16:9",
                "generation_type": "TEXT_2_VIDEO",
            })

            mock_preview.assert_not_called()

    @pytest.mark.asyncio
    async def test_generation_failure_propagates(self):
        """Provider failure should propagate, not be silently swallowed."""
        patches = _default_patches()
        with (
            patches["service_cls"] as mock_service_cls,
            patches["log_usage"],
            patches["get_draft"] as mock_get_draft,
            patches["update_url"],
            patches["preview"],
            patches["load_profile"] as mock_load_profile,
            patches["gen_prompt"] as mock_gen_prompt,
            patches["decrement_credit"],
        ):
            mock_service = AsyncMock()
            mock_service.generate = AsyncMock(
                side_effect=RuntimeError("All video providers failed")
            )
            mock_service_cls.return_value = mock_service

            mock_load_profile.return_value = None
            mock_gen_prompt.return_value = VideoPromptResult(text="Optimized prompt.", input_tokens=500, output_tokens=100)

            mock_get_draft.return_value = {
                "id": "draft-1",
                "tenant_id": "tenant-1",
                "status": "previewing",
            }

            from worker.jobs.generate_video import handle_generate_video

            with pytest.raises(RuntimeError, match="All video providers failed"):
                await handle_generate_video({
                    "draft_id": "draft-1",
                    "tenant_id": "tenant-1",
                    "prompt": "failing video",
                    "aspect_ratio": "16:9",
                    "generation_type": "TEXT_2_VIDEO",
                })

    @pytest.mark.asyncio
    async def test_prompt_gen_failure_falls_back_to_raw_prompt(self):
        """If Claude prompt gen fails, falls back to raw prompt and video still generates."""
        mock_video_result = VideoResult(
            url="https://cdn.kie.ai/fallback.mp4",
            provider="kie_ai_veo",
            cost_usd=0.40,
            metadata={},
        )

        patches = _default_patches()
        with (
            patches["service_cls"] as mock_service_cls,
            patches["log_usage"] as mock_log,
            patches["get_draft"] as mock_get_draft,
            patches["update_url"],
            patches["preview"],
            patches["load_profile"] as mock_load_profile,
            patches["gen_prompt"] as mock_gen_prompt,
            patches["decrement_credit"],
        ):
            mock_service = AsyncMock()
            mock_service.generate = AsyncMock(return_value=mock_video_result)
            mock_service_cls.return_value = mock_service

            mock_load_profile.return_value = None
            mock_gen_prompt.side_effect = Exception("Claude API down")

            mock_get_draft.return_value = {
                "id": "draft-1",
                "tenant_id": "tenant-1",
                "caption_variants": [],
                "image_urls": [],
                "status": "generated",
            }

            from worker.jobs.generate_video import handle_generate_video

            await handle_generate_video({
                "draft_id": "draft-1",
                "tenant_id": "tenant-1",
                "prompt": "raw fallback prompt",
                "aspect_ratio": "16:9",
                "generation_type": "TEXT_2_VIDEO",
            })

            # Should fall back to raw prompt
            mock_service.generate.assert_called_once_with(
                "raw fallback prompt",
                aspect_ratio="16:9",
                generation_type="TEXT_2_VIDEO",
                image_urls=None,
            )
            # No log_usage_event calls — prompt gen failed, video gen logs via service
            assert mock_log.call_count == 0

    @pytest.mark.asyncio
    async def test_brand_profile_loaded_before_prompt_gen(self):
        """Brand profile should be loaded and passed to generate_video_prompt."""
        mock_video_result = VideoResult(
            url="https://cdn.kie.ai/branded.mp4",
            provider="kie_ai_veo",
            cost_usd=0.40,
            metadata={},
        )
        mock_profile = BrandProfile(
            tenant_id="tenant-1",
            name="Mondo Shrimp",
            tone_words=["bold", "playful"],
            audience_description="Foodies",
            do_list=[],
            dont_list=[],
        )

        patches = _default_patches()
        with (
            patches["service_cls"] as mock_service_cls,
            patches["log_usage"],
            patches["get_draft"] as mock_get_draft,
            patches["update_url"],
            patches["preview"],
            patches["load_profile"] as mock_load_profile,
            patches["gen_prompt"] as mock_gen_prompt,
            patches["decrement_credit"],
        ):
            mock_service = AsyncMock()
            mock_service.generate = AsyncMock(return_value=mock_video_result)
            mock_service_cls.return_value = mock_service

            mock_load_profile.return_value = mock_profile
            mock_gen_prompt.return_value = VideoPromptResult(text="Branded prompt.", input_tokens=500, output_tokens=100)

            mock_get_draft.return_value = {
                "id": "draft-1",
                "tenant_id": "tenant-1",
                "caption_variants": [],
                "image_urls": [],
                "status": "generated",
            }

            from worker.jobs.generate_video import handle_generate_video

            await handle_generate_video({
                "draft_id": "draft-1",
                "tenant_id": "tenant-1",
                "prompt": "shrimp video",
                "aspect_ratio": "16:9",
                "generation_type": "TEXT_2_VIDEO",
            })

            mock_load_profile.assert_called_once_with("tenant-1")
            # Verify brand profile was passed to prompt gen
            gen_call = mock_gen_prompt.call_args
            assert gen_call.kwargs.get("brand_profile") == mock_profile
