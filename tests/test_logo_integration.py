"""Tests for automatic logo integration into the content pipeline."""

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


class TestRefSlotTypeLogo:
    def test_logo_reference_enum_exists(self) -> None:
        assert RefSlotType.LOGO_REFERENCE == "logo_reference"

    def test_logo_reference_excluded_from_cap(self) -> None:
        """Logo references should NOT count toward the 14-image cap."""
        refs = [
            RefImageAssignment(asset_url="http://img.test/1.jpg", slot_type=RefSlotType.OBJECT_FIDELITY),
            RefImageAssignment(asset_url="http://img.test/logo.png", slot_type=RefSlotType.LOGO_REFERENCE),
        ]
        # Count non-logo refs (same logic as validate())
        non_logo = sum(1 for r in refs if r.slot_type != RefSlotType.LOGO_REFERENCE)
        assert non_logo == 1


class TestValidationExcludesLogo:
    def test_logo_refs_not_counted_in_cap(self) -> None:
        """Plan with 14 product refs + 1 logo should pass validation."""
        refs_14_products = [
            RefImageAssignment(asset_url=f"http://img.test/{i}.jpg", slot_type=RefSlotType.OBJECT_FIDELITY)
            for i in range(14)
        ]
        logo_ref = RefImageAssignment(
            asset_url="http://img.test/logo.png", slot_type=RefSlotType.LOGO_REFERENCE,
        )
        all_refs = refs_14_products + [logo_ref]

        scene = ScenePlan(
            index=0,
            scene_type="hero",
            duration_seconds=5.0,
            start_frame=FramePrompt(
                prompt="test",
                aspect_ratio="16:9",
                reference_images=all_refs,
            ),
        )
        plan = GenerationPlan(
            content_format=ContentFormat.IMAGE_POST,
            title="test",
            concept_summary="test",
            scenes=[scene],
            captions=[{"text": "a", "formula": "punchy_one_liner", "platform_variant": "ig"},
                      {"text": "b", "formula": "hook_story_offer", "platform_variant": "fb"},
                      {"text": "c", "formula": "story_lesson", "platform_variant": "tw"}],
        )
        errors = plan.validate()
        ref_errors = [e for e in errors if "reference images" in e]
        assert ref_errors == [], f"Logo should not trigger cap: {ref_errors}"


class TestLogoPresenceValidation:
    def _make_plan(self, has_logo_ref: bool) -> GenerationPlan:
        refs = []
        if has_logo_ref:
            refs.append(RefImageAssignment(
                asset_url="http://img.test/logo.png", slot_type=RefSlotType.LOGO_REFERENCE,
            ))
        scene = ScenePlan(
            index=0, scene_type="hero", duration_seconds=5.0,
            start_frame=FramePrompt(prompt="test", aspect_ratio="16:9", reference_images=refs),
        )
        return GenerationPlan(
            content_format=ContentFormat.IMAGE_POST, title="test", concept_summary="test",
            scenes=[scene],
            captions=[{"text": "a", "formula": "punchy_one_liner", "platform_variant": "ig"},
                      {"text": "b", "formula": "hook_story_offer", "platform_variant": "fb"},
                      {"text": "c", "formula": "story_lesson", "platform_variant": "tw"}],
        )

    def test_no_error_when_logo_not_available(self) -> None:
        plan = self._make_plan(has_logo_ref=False)
        errors = plan.validate(logo_available=False)
        logo_errors = [e for e in errors if "Logo" in e]
        assert logo_errors == []

    def test_no_error_when_logo_present_in_scene(self) -> None:
        plan = self._make_plan(has_logo_ref=True)
        errors = plan.validate(logo_available=True)
        logo_errors = [e for e in errors if "Logo" in e]
        assert logo_errors == []

    def test_error_when_logo_available_but_missing_from_scenes(self) -> None:
        plan = self._make_plan(has_logo_ref=False)
        errors = plan.validate(logo_available=True)
        logo_errors = [e for e in errors if "Logo" in e or "logo" in e]
        assert len(logo_errors) == 1


class TestSystemPromptLogoLayer:
    def test_logo_layer_included_when_logo_present(self) -> None:
        from pipeline.prompt_engine.asset_resolver import AssetManifest
        from pipeline.prompt_engine.system_prompt import build_system_prompt

        manifest = AssetManifest(
            product_photos=[], people_photos=[], other_photos=[],
            logo_url="http://logo.test/logo.png",
        )
        profile = MagicMock()
        profile.tenant_id = "t1"

        with patch("pipeline.prompt_engine.system_prompt.format_brand_context", return_value="brand"):
            prompt = build_system_prompt(profile, [], manifest)

        assert "Logo Integration" in prompt
        assert "logo_reference" in prompt
        assert "laptop" in prompt.lower() or "sticker" in prompt.lower()
        # Fix #8: negative examples should be present
        assert "DO NOT" in prompt
        assert "floating logo" in prompt.lower()

    def test_logo_layer_excluded_when_no_logo(self) -> None:
        from pipeline.prompt_engine.asset_resolver import AssetManifest
        from pipeline.prompt_engine.system_prompt import build_system_prompt

        manifest = AssetManifest(
            product_photos=[], people_photos=[], other_photos=[],
            logo_url=None,
        )
        profile = MagicMock()
        profile.tenant_id = "t1"

        with patch("pipeline.prompt_engine.system_prompt.format_brand_context", return_value="brand"):
            prompt = build_system_prompt(profile, [], manifest)

        assert "Logo Integration" not in prompt

    def test_asset_context_describes_logo_reference(self) -> None:
        from pipeline.prompt_engine.asset_resolver import AssetManifest
        from pipeline.prompt_engine.system_prompt import _build_asset_context

        manifest = AssetManifest(
            product_photos=[], people_photos=[], other_photos=[],
            logo_url="http://logo.test/logo.png",
        )
        context = _build_asset_context(manifest)
        assert "logo_reference" in context
        assert "http://logo.test/logo.png" in context

    def test_asset_context_includes_shape_hint(self) -> None:
        from pipeline.prompt_engine.asset_resolver import AssetManifest
        from pipeline.prompt_engine.system_prompt import _build_asset_context

        manifest = AssetManifest(
            product_photos=[], people_photos=[], other_photos=[],
            logo_url="http://logo.test/logo.png",
            logo_shape="horizontal",
        )
        context = _build_asset_context(manifest)
        assert "wide/horizontal wordmark" in context

    def test_asset_context_no_logo(self) -> None:
        from pipeline.prompt_engine.asset_resolver import AssetManifest
        from pipeline.prompt_engine.system_prompt import _build_asset_context

        manifest = AssetManifest(
            product_photos=[], people_photos=[], other_photos=[],
            logo_url=None,
        )
        context = _build_asset_context(manifest)
        assert "No logo available" in context


class TestToolSchemaLogoReference:
    def test_slot_type_enum_includes_logo_reference(self) -> None:
        from pipeline.prompt_engine.engine import _TOOL_SCHEMA

        slot_enum = (
            _TOOL_SCHEMA["input_schema"]["$defs"]["frame_prompt"]
            ["properties"]["reference_images"]["items"]
            ["properties"]["slot_type"]["enum"]
        )
        assert "logo_reference" in slot_enum

    def test_composite_instruction_no_logo_overlay(self) -> None:
        """Composite schema should not have logo_overlay (deprecated)."""
        from pipeline.prompt_engine.engine import _TOOL_SCHEMA

        composite_props = (
            _TOOL_SCHEMA["input_schema"]["$defs"]["composite_instruction"]["properties"]
        )
        assert "logo_overlay" not in composite_props
        assert "logo_position" not in composite_props
        assert "logo_opacity" not in composite_props


class TestSaveLogoFromTelegram:
    @pytest.mark.asyncio
    async def test_saves_and_updates_path(self) -> None:
        from bot.handlers.logo import save_logo_from_telegram

        mock_bot = MagicMock()
        mock_bot.token = "123:ABC"
        mock_file = MagicMock()
        mock_file.file_path = "photos/logo_123.jpg"
        mock_bot.get_file = AsyncMock(return_value=mock_file)

        with (
            patch("bot.handlers.logo.download_and_store",
                  new_callable=AsyncMock,
                  return_value="reference-photos/t1/logo_abc.jpg") as mock_store,
            patch("bot.handlers.logo._update_logo_path",
                  new_callable=AsyncMock) as mock_update,
            patch("bot.services.storage.get_signed_url", return_value="https://signed.url/logo.jpg"),
            patch("httpx.AsyncClient") as mock_httpx_cls,
        ):
            # Mock the dimension extraction (it fetches the stored image)
            mock_resp = MagicMock()
            mock_resp.status_code = 404  # Skip dimension extraction
            mock_http_client = MagicMock()
            mock_http_client.get = AsyncMock(return_value=mock_resp)
            mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
            mock_http_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx_cls.return_value = mock_http_client

            result = await save_logo_from_telegram(
                bot=mock_bot,
                file_id="file_123",
                file_unique_id="unique_123",
                tenant_id="t1",
            )

        assert result == "reference-photos/t1/logo_abc.jpg"
        mock_store.assert_called_once()
        # preserve_alpha=True should be passed for logos
        call_kwargs = mock_store.call_args[1]
        assert call_kwargs["preserve_alpha"] is True
        mock_update.assert_called_once()
