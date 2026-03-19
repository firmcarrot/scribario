"""Tests for the generate_content job handler with Prompt Engine integration."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.prompt_engine.engine import PlanResult
from pipeline.prompt_engine.models import (
    ContentFormat,
    FramePrompt,
    GenerationPlan,
    RefImageAssignment,
    RefSlotType,
    ScenePlan,
)
from worker.jobs.generate_content import handle_generate_content


def _make_plan(
    content_format: ContentFormat = ContentFormat.IMAGE_POST,
    num_scenes: int = 3,
) -> GenerationPlan:
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
        content_format=content_format,
        title="Mondo Monday",
        concept_summary="Hero shot",
        scenes=scenes,
        captions=[
            {"text": f"Caption {i} #MondoShrimp", "platform_variant": "instagram"}
            for i in range(num_scenes)
        ],
    )


def _base_message() -> dict:
    return {
        "request_id": "req-123",
        "tenant_id": "tenant-456",
        "intent": "hero shot of our sauce",
        "platform_targets": ["instagram"],
        "telegram_chat_id": 999,
    }


class TestHandleGenerateContentWithPromptEngine:
    @pytest.mark.asyncio
    async def test_uses_prompt_engine(self) -> None:
        """Verify generate_content calls generate_plan instead of generate_captions."""
        plan = _make_plan()

        image_result = MagicMock()
        image_result.url = "https://img.com/result.jpg"
        image_result.provider = "kie_ai"
        image_result.cost_usd = 0.04

        mock_image_service = MagicMock()
        mock_image_service.generate = AsyncMock(return_value=image_result)

        with (
            patch("worker.jobs.generate_content.update_content_request_status",
                  new_callable=AsyncMock),
            patch("worker.jobs.generate_content.load_brand_profile",
                  new_callable=AsyncMock, return_value=MagicMock()),
            patch("worker.jobs.generate_content.load_few_shot_examples",
                  new_callable=AsyncMock, return_value=[]),
            patch("worker.jobs.generate_content.resolve_assets",
                  new_callable=AsyncMock, return_value=MagicMock(
                      product_photos=["https://a.com/sauce.jpg"],
                      people_photos=[],
                      other_photos=[],
                      logo_url=None,
                  )),
            patch("worker.jobs.generate_content.generate_plan",
                  new_callable=AsyncMock, return_value=PlanResult(plan=plan, input_tokens=1000, output_tokens=500, model="claude-sonnet-4-20250514")) as mock_gen_plan,
            patch("worker.jobs.generate_content.ImageGenerationService",
                  return_value=mock_image_service),
            patch("worker.jobs.generate_content.log_usage_event",
                  new_callable=AsyncMock),
            patch("worker.jobs.generate_content.create_content_draft",
                  new_callable=AsyncMock, return_value={"id": "draft-1"}),
            patch("worker.jobs.generate_content.update_content_request_status",
                  new_callable=AsyncMock),
            patch("worker.jobs.generate_content._send_preview",
                  new_callable=AsyncMock),
            patch("bot.services.budget.increment_post_count",
                  new_callable=AsyncMock),
            patch("bot.services.budget.decrement_video_credit",
                  new_callable=AsyncMock),
        ):
            await handle_generate_content(_base_message())

        mock_gen_plan.assert_called_once()
        call_kwargs = mock_gen_plan.call_args.kwargs
        assert call_kwargs["intent"] == "hero shot of our sauce"

    @pytest.mark.asyncio
    async def test_uses_plan_frame_prompts_for_image_gen(self) -> None:
        """Image gen should receive start_frame.prompt from the plan, not visual_prompt."""
        plan = _make_plan(num_scenes=2)

        image_result = MagicMock()
        image_result.url = "https://img.com/result.jpg"
        image_result.provider = "kie_ai"
        image_result.cost_usd = 0.04

        mock_image_service = MagicMock()
        mock_image_service.generate = AsyncMock(return_value=image_result)

        with (
            patch("worker.jobs.generate_content.update_content_request_status",
                  new_callable=AsyncMock),
            patch("worker.jobs.generate_content.load_brand_profile",
                  new_callable=AsyncMock, return_value=MagicMock()),
            patch("worker.jobs.generate_content.load_few_shot_examples",
                  new_callable=AsyncMock, return_value=[]),
            patch("worker.jobs.generate_content.resolve_assets",
                  new_callable=AsyncMock, return_value=MagicMock(
                      product_photos=[], people_photos=[], other_photos=[], logo_url=None,
                  )),
            patch("worker.jobs.generate_content.generate_plan",
                  new_callable=AsyncMock, return_value=PlanResult(plan=plan, input_tokens=1000, output_tokens=500, model="claude-sonnet-4-20250514")),
            patch("worker.jobs.generate_content.ImageGenerationService",
                  return_value=mock_image_service),
            patch("worker.jobs.generate_content.log_usage_event",
                  new_callable=AsyncMock),
            patch("worker.jobs.generate_content.create_content_draft",
                  new_callable=AsyncMock, return_value={"id": "draft-1"}),
            patch("worker.jobs.generate_content._send_preview",
                  new_callable=AsyncMock),
            patch("bot.services.budget.increment_post_count",
                  new_callable=AsyncMock),
            patch("bot.services.budget.decrement_video_credit",
                  new_callable=AsyncMock),
        ):
            await handle_generate_content(_base_message())

        # Image service called once per scene
        assert mock_image_service.generate.call_count == 2

        # First call should use scene 0's start_frame prompt
        first_call = mock_image_service.generate.call_args_list[0]
        assert first_call.args[0] == "Scene 0 prompt"

    @pytest.mark.asyncio
    async def test_reference_images_passed_to_image_gen(self) -> None:
        """Reference images from plan scenes should be passed to image gen."""
        plan = _make_plan(num_scenes=1)

        image_result = MagicMock()
        image_result.url = "https://img.com/result.jpg"
        image_result.provider = "kie_ai"
        image_result.cost_usd = 0.04

        mock_image_service = MagicMock()
        mock_image_service.generate = AsyncMock(return_value=image_result)

        with (
            patch("worker.jobs.generate_content.update_content_request_status",
                  new_callable=AsyncMock),
            patch("worker.jobs.generate_content.load_brand_profile",
                  new_callable=AsyncMock, return_value=MagicMock()),
            patch("worker.jobs.generate_content.load_few_shot_examples",
                  new_callable=AsyncMock, return_value=[]),
            patch("worker.jobs.generate_content.resolve_assets",
                  new_callable=AsyncMock, return_value=MagicMock(
                      product_photos=["https://a.com/sauce.jpg"],
                      people_photos=[], other_photos=[], logo_url=None,
                  )),
            patch("worker.jobs.generate_content.generate_plan",
                  new_callable=AsyncMock, return_value=PlanResult(plan=plan, input_tokens=1000, output_tokens=500, model="claude-sonnet-4-20250514")),
            patch("worker.jobs.generate_content.ImageGenerationService",
                  return_value=mock_image_service),
            patch("worker.jobs.generate_content.log_usage_event",
                  new_callable=AsyncMock),
            patch("worker.jobs.generate_content.create_content_draft",
                  new_callable=AsyncMock, return_value={"id": "draft-1"}),
            patch("worker.jobs.generate_content._send_preview",
                  new_callable=AsyncMock),
            patch("bot.services.budget.increment_post_count",
                  new_callable=AsyncMock),
            patch("bot.services.budget.decrement_video_credit",
                  new_callable=AsyncMock),
        ):
            await handle_generate_content(_base_message())

        first_call = mock_image_service.generate.call_args_list[0]
        ref_urls = first_call.kwargs.get("reference_image_urls")
        assert ref_urls == ["https://a.com/sauce.jpg"]

    @pytest.mark.asyncio
    async def test_plan_captions_used_for_draft(self) -> None:
        """Caption variants in the draft should come from the plan, not caption_gen."""
        plan = _make_plan(num_scenes=1)

        image_result = MagicMock()
        image_result.url = "https://img.com/result.jpg"
        image_result.provider = "kie_ai"
        image_result.cost_usd = 0.04

        mock_image_service = MagicMock()
        mock_image_service.generate = AsyncMock(return_value=image_result)

        with (
            patch("worker.jobs.generate_content.update_content_request_status",
                  new_callable=AsyncMock),
            patch("worker.jobs.generate_content.load_brand_profile",
                  new_callable=AsyncMock, return_value=MagicMock()),
            patch("worker.jobs.generate_content.load_few_shot_examples",
                  new_callable=AsyncMock, return_value=[]),
            patch("worker.jobs.generate_content.resolve_assets",
                  new_callable=AsyncMock, return_value=MagicMock(
                      product_photos=[], people_photos=[], other_photos=[], logo_url=None,
                  )),
            patch("worker.jobs.generate_content.generate_plan",
                  new_callable=AsyncMock, return_value=PlanResult(plan=plan, input_tokens=1000, output_tokens=500, model="claude-sonnet-4-20250514")),
            patch("worker.jobs.generate_content.ImageGenerationService",
                  return_value=mock_image_service),
            patch("worker.jobs.generate_content.log_usage_event",
                  new_callable=AsyncMock),
            patch("worker.jobs.generate_content.create_content_draft",
                  new_callable=AsyncMock, return_value={"id": "draft-1"}) as mock_draft,
            patch("worker.jobs.generate_content._send_preview",
                  new_callable=AsyncMock),
            patch("bot.services.budget.increment_post_count",
                  new_callable=AsyncMock),
            patch("bot.services.budget.decrement_video_credit",
                  new_callable=AsyncMock),
        ):
            await handle_generate_content(_base_message())

        call_kwargs = mock_draft.call_args.kwargs
        assert call_kwargs["caption_variants"] == plan.captions
