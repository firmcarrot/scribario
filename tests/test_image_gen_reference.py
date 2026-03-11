"""Tests for image_gen.py reference image support via image_input."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.image_gen import KieAiProvider, ImageGenerationService


FAKE_TASK_ID = "task_nano-banana-2_test123"
FAKE_IMAGE_URL = "https://tempfile.aiquickdraw.com/test-result.jpg"


def _make_success_response(task_id: str = FAKE_TASK_ID) -> dict:
    return {"code": 200, "msg": "success", "data": {"taskId": task_id, "recordId": task_id}}


def _make_poll_success(image_url: str = FAKE_IMAGE_URL) -> dict:
    return {
        "code": 200,
        "data": {
            "state": "success",
            "costTime": 42000,
            "resultJson": json.dumps({"resultUrls": [image_url]}),
        },
    }


class TestKieAiProviderReferenceImages:
    @pytest.mark.asyncio
    async def test_generate_without_reference_images(self):
        """Baseline: generate with text-only prompt still works."""
        provider = KieAiProvider(api_key="test-key")

        mock_client = MagicMock()
        create_resp = MagicMock()
        create_resp.json.return_value = _make_success_response()
        create_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.json.return_value = _make_poll_success()
        poll_resp.raise_for_status = MagicMock()

        mock_client.post = AsyncMock(return_value=create_resp)
        mock_client.get = AsyncMock(return_value=poll_resp)
        mock_client.is_closed = False

        with patch.object(provider, "_get_client", return_value=mock_client):
            result = await provider.generate(prompt="A shrimp dish", aspect_ratio="1:1")

        assert result.url == FAKE_IMAGE_URL
        # Verify image_input was NOT included in payload
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs.args[1] if len(call_kwargs.args) > 1 else call_kwargs.kwargs["json"]
        assert "image_input" not in payload.get("input", {})

    @pytest.mark.asyncio
    async def test_generate_with_reference_images_includes_image_input(self):
        """When reference_image_urls provided, they appear in the API payload."""
        provider = KieAiProvider(api_key="test-key")

        ref_urls = [
            "https://supabase.co/storage/signed/ref1.jpg",
            "https://supabase.co/storage/signed/ref2.jpg",
        ]

        mock_client = MagicMock()
        create_resp = MagicMock()
        create_resp.json.return_value = _make_success_response()
        create_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.json.return_value = _make_poll_success()
        poll_resp.raise_for_status = MagicMock()

        mock_client.post = AsyncMock(return_value=create_resp)
        mock_client.get = AsyncMock(return_value=poll_resp)
        mock_client.is_closed = False

        with patch.object(provider, "_get_client", return_value=mock_client):
            result = await provider.generate(
                prompt="Owner eating Mondo Shrimp over a volcano, dangerously good",
                aspect_ratio="16:9",
                reference_image_urls=ref_urls,
            )

        assert result.url == FAKE_IMAGE_URL

        # Verify image_input was included in payload
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs[1].get("json") or call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1]["json"]
        assert payload["input"]["image_input"] == ref_urls

    @pytest.mark.asyncio
    async def test_generate_with_empty_reference_list_excludes_image_input(self):
        """Empty reference list should not include image_input in payload."""
        provider = KieAiProvider(api_key="test-key")

        mock_client = MagicMock()
        create_resp = MagicMock()
        create_resp.json.return_value = _make_success_response()
        create_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.json.return_value = _make_poll_success()
        poll_resp.raise_for_status = MagicMock()

        mock_client.post = AsyncMock(return_value=create_resp)
        mock_client.get = AsyncMock(return_value=poll_resp)
        mock_client.is_closed = False

        with patch.object(provider, "_get_client", return_value=mock_client):
            result = await provider.generate(
                prompt="A shrimp dish",
                reference_image_urls=[],
            )

        assert result.url == FAKE_IMAGE_URL
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs[1].get("json") or call_kwargs[1]["json"]
        assert "image_input" not in payload.get("input", {})


class TestBuildImageInputArray:
    def test_new_photos_take_priority_over_defaults(self):
        from pipeline.image_gen import build_image_input_array

        new_photos = [f"new_{i}.jpg" for i in range(10)]
        defaults = [f"default_{i}.jpg" for i in range(10)]

        result = build_image_input_array(new_photo_urls=new_photos, default_ref_urls=defaults)

        # Should have new photos first
        assert result[:10] == new_photos
        # Total <= 14
        assert len(result) <= 14

    def test_truncates_to_14_total(self):
        from pipeline.image_gen import build_image_input_array

        new_photos = [f"new_{i}.jpg" for i in range(8)]
        defaults = [f"default_{i}.jpg" for i in range(10)]

        result = build_image_input_array(new_photo_urls=new_photos, default_ref_urls=defaults)

        assert len(result) == 14

    def test_no_new_photos_uses_all_defaults_up_to_limit(self):
        from pipeline.image_gen import build_image_input_array

        defaults = [f"default_{i}.jpg" for i in range(6)]
        result = build_image_input_array(new_photo_urls=[], default_ref_urls=defaults)

        assert result == defaults

    def test_returns_empty_when_no_inputs(self):
        from pipeline.image_gen import build_image_input_array

        result = build_image_input_array(new_photo_urls=[], default_ref_urls=[])
        assert result == []

    def test_more_than_14_new_photos_truncates_to_14(self):
        from pipeline.image_gen import build_image_input_array

        new_photos = [f"new_{i}.jpg" for i in range(20)]
        result = build_image_input_array(new_photo_urls=new_photos, default_ref_urls=[])

        assert len(result) == 14
        assert result == new_photos[:14]

    def test_returns_warning_flag_when_defaults_truncated(self):
        from pipeline.image_gen import build_image_input_array

        new_photos = [f"new_{i}.jpg" for i in range(5)]
        defaults = [f"default_{i}.jpg" for i in range(12)]

        result, truncated = build_image_input_array(
            new_photo_urls=new_photos, default_ref_urls=defaults, return_truncated=True
        )

        assert truncated is True
        assert len(result) == 14

    def test_no_truncation_returns_false_flag(self):
        from pipeline.image_gen import build_image_input_array

        result, truncated = build_image_input_array(
            new_photo_urls=["a.jpg"],
            default_ref_urls=["b.jpg"],
            return_truncated=True,
        )

        assert truncated is False
