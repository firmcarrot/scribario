"""Tests for inline video generation in generate_content job handler."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.prompt_engine.models import (
    ContentFormat,
    FramePrompt,
    GenerationPlan,
    RefImageAssignment,
    RefSlotType,
    ScenePlan,
)
from pipeline.video_gen import VideoResult


def _make_plan(num_scenes: int = 3) -> GenerationPlan:
    scenes = [
        ScenePlan(
            index=i,
            scene_type="product_hero",
            duration_seconds=0,
            start_frame=FramePrompt(
                prompt=f"Scene {i} prompt",
                aspect_ratio="1:1",
                reference_images=[
                    RefImageAssignment("https://a.com/sauce.jpg", RefSlotType.OBJECT_FIDELITY),
                ] if i == 0 else [],
            ),
        )
        for i in range(num_scenes)
    ]
    return GenerationPlan(
        content_format=ContentFormat.IMAGE_POST,
        title="Mondo Monday",
        concept_summary="Hero shot",
        scenes=scenes,
        captions=[
            {"text": f"Caption {i} #MondoShrimp", "platform_variant": "instagram"}
            for i in range(num_scenes)
        ],
    )


def _base_message(generate_video: bool = True) -> dict:
    msg = {
        "request_id": "req-123",
        "tenant_id": "tenant-456",
        "intent": "hero shot of our sauce",
        "platform_targets": ["instagram"],
        "telegram_chat_id": 999,
    }
    if generate_video:
        msg["generate_video"] = True
        msg["video_aspect_ratio"] = "16:9"
    return msg


def _mock_image_service():
    image_result = MagicMock()
    image_result.url = "https://img.com/result.jpg"
    image_result.provider = "kie_ai"
    image_result.cost_usd = 0.04
    mock_service = MagicMock()
    mock_service.generate = AsyncMock(return_value=image_result)
    return mock_service


def _common_patches(mock_img_service=None, plan=None):
    """Return context managers for common patches."""
    if mock_img_service is None:
        mock_img_service = _mock_image_service()
    if plan is None:
        plan = _make_plan()
    return {
        "status": patch(
            "worker.jobs.generate_content.update_content_request_status",
            new_callable=AsyncMock,
        ),
        "profile": patch(
            "worker.jobs.generate_content.load_brand_profile",
            new_callable=AsyncMock,
            return_value=MagicMock(),
        ),
        "examples": patch(
            "worker.jobs.generate_content.load_few_shot_examples",
            new_callable=AsyncMock,
            return_value=[],
        ),
        "assets": patch(
            "worker.jobs.generate_content.resolve_assets",
            new_callable=AsyncMock,
            return_value=MagicMock(
                product_photos=[], people_photos=[], other_photos=[], logo_url=None,
            ),
        ),
        "gen_plan": patch(
            "worker.jobs.generate_content.generate_plan",
            new_callable=AsyncMock,
            return_value=plan,
        ),
        "img_service": patch(
            "worker.jobs.generate_content.ImageGenerationService",
            return_value=mock_img_service,
        ),
        "log_usage": patch(
            "worker.jobs.generate_content.log_usage_event",
            new_callable=AsyncMock,
        ),
        "create_draft": patch(
            "worker.jobs.generate_content.create_content_draft",
            new_callable=AsyncMock,
            return_value={"id": "draft-1"},
        ),
        "send_preview": patch(
            "worker.jobs.generate_content._send_preview",
            new_callable=AsyncMock,
        ),
    }


class TestInlineVideoGeneration:
    """Tests for inline video generation within generate_content."""

    @pytest.mark.asyncio
    async def test_video_generated_inline_when_flag_set(self):
        """When generate_video=True, video is generated inline (no separate job)."""
        video_result = VideoResult(
            url="https://cdn.kie.ai/video-123.mp4",
            provider="kie_ai_veo",
            cost_usd=0.40,
            metadata={},
        )
        mock_video_service = MagicMock()
        mock_video_service.generate = AsyncMock(return_value=video_result)

        patches = _common_patches()
        with (
            patches["status"],
            patches["profile"],
            patches["examples"],
            patches["assets"],
            patches["gen_plan"],
            patches["img_service"],
            patches["log_usage"],
            patches["create_draft"],
            patches["send_preview"] as mock_preview,
            patch(
                "pipeline.video_gen.VideoGenerationService",
                return_value=mock_video_service,
            ),
            patch(
                "pipeline.video_prompt_gen.generate_video_prompt",
                new_callable=AsyncMock,
                return_value="Optimized video prompt",
            ),
            patch(
                "worker.jobs.generate_video.update_draft_video_url",
                new_callable=AsyncMock,
            ) as mock_update_url,
        ):
            from worker.jobs.generate_content import handle_generate_content

            await handle_generate_content(_base_message(generate_video=True))

            # Video should be generated
            mock_video_service.generate.assert_called_once()
            # Video URL stored on draft
            mock_update_url.assert_called_once_with("draft-1", "https://cdn.kie.ai/video-123.mp4")
            # Preview called with video_url
            mock_preview.assert_called_once()
            call_kwargs = mock_preview.call_args.kwargs
            assert call_kwargs["video_url"] == "https://cdn.kie.ai/video-123.mp4"

    @pytest.mark.asyncio
    async def test_no_separate_video_job_enqueued(self):
        """When generate_video=True, NO separate generate_video job is enqueued."""
        video_result = VideoResult(
            url="https://cdn.kie.ai/video-123.mp4",
            provider="kie_ai_veo",
            cost_usd=0.40,
            metadata={},
        )
        mock_video_service = MagicMock()
        mock_video_service.generate = AsyncMock(return_value=video_result)

        patches = _common_patches()
        with (
            patches["status"],
            patches["profile"],
            patches["examples"],
            patches["assets"],
            patches["gen_plan"],
            patches["img_service"],
            patches["log_usage"],
            patches["create_draft"],
            patches["send_preview"],
            patch(
                "pipeline.video_gen.VideoGenerationService",
                return_value=mock_video_service,
            ),
            patch(
                "pipeline.video_prompt_gen.generate_video_prompt",
                new_callable=AsyncMock,
                return_value="prompt",
            ),
            patch(
                "worker.jobs.generate_video.update_draft_video_url",
                new_callable=AsyncMock,
            ),
            patch("bot.db.enqueue_job", new_callable=AsyncMock) as mock_enqueue,
        ):
            from worker.jobs.generate_content import handle_generate_content

            await handle_generate_content(_base_message(generate_video=True))

            # No enqueue_job call for generate_video
            mock_enqueue.assert_not_called()

    @pytest.mark.asyncio
    async def test_video_failure_falls_back_to_image_preview(self):
        """If video generation fails, send image-only preview (no crash)."""
        mock_video_service = MagicMock()
        mock_video_service.generate = AsyncMock(
            side_effect=RuntimeError("Veo API down"),
        )

        patches = _common_patches()
        with (
            patches["status"],
            patches["profile"],
            patches["examples"],
            patches["assets"],
            patches["gen_plan"],
            patches["img_service"],
            patches["log_usage"],
            patches["create_draft"],
            patches["send_preview"] as mock_preview,
            patch(
                "pipeline.video_gen.VideoGenerationService",
                return_value=mock_video_service,
            ),
            patch(
                "pipeline.video_prompt_gen.generate_video_prompt",
                new_callable=AsyncMock,
                return_value="prompt",
            ),
            patch(
                "worker.jobs.generate_video.update_draft_video_url",
                new_callable=AsyncMock,
            ),
        ):
            from worker.jobs.generate_content import handle_generate_content

            # Should not raise
            await handle_generate_content(_base_message(generate_video=True))

            # Preview still sent, but without video_url
            mock_preview.assert_called_once()
            call_kwargs = mock_preview.call_args.kwargs
            assert call_kwargs["video_url"] is None

    @pytest.mark.asyncio
    async def test_image_only_request_unchanged(self):
        """Without generate_video flag, no video gen happens."""
        patches = _common_patches()
        with (
            patches["status"],
            patches["profile"],
            patches["examples"],
            patches["assets"],
            patches["gen_plan"],
            patches["img_service"],
            patches["log_usage"],
            patches["create_draft"],
            patches["send_preview"] as mock_preview,
        ):
            from worker.jobs.generate_content import handle_generate_content

            await handle_generate_content(_base_message(generate_video=False))

            mock_preview.assert_called_once()
            call_kwargs = mock_preview.call_args.kwargs
            assert call_kwargs.get("video_url") is None
