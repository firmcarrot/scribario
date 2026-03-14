"""Tests for ElevenLabs sound effects generation."""

from __future__ import annotations

import asyncio
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from pipeline.long_video.sfx import (
    ELEVENLABS_BASE_URL,
    SFX_COST_PER_CLIP,
    SFXResult,
    generate_sfx,
    generate_sfx_batch,
)


class TestSFXResult:
    def test_sfx_result_fields(self) -> None:
        result = SFXResult(audio_path="/tmp/sfx.mp3", cost_usd=0.01)
        assert result.audio_path == "/tmp/sfx.mp3"
        assert result.cost_usd == 0.01


class TestGenerateSFX:
    async def test_posts_to_correct_endpoint(self) -> None:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b"fake-audio-bytes"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with (
            patch("pipeline.long_video.sfx.httpx.AsyncClient", return_value=mock_client),
            patch("pipeline.long_video.sfx.get_settings") as mock_settings,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key-123"

            result = await generate_sfx(
                description="dramatic whoosh",
                duration_seconds=3.0,
                output_dir=tmpdir,
            )

            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == f"{ELEVENLABS_BASE_URL}/v1/sound-generation"
            assert call_args[1]["json"]["text"] == "dramatic whoosh"
            assert call_args[1]["json"]["duration_seconds"] == 3.0
            assert call_args[1]["headers"]["xi-api-key"] == "test-key-123"

    async def test_returns_sfx_result_with_audio_path_and_cost(self) -> None:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b"fake-audio-bytes"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with (
            patch("pipeline.long_video.sfx.httpx.AsyncClient", return_value=mock_client),
            patch("pipeline.long_video.sfx.get_settings") as mock_settings,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key-123"

            result = await generate_sfx(
                description="ocean waves",
                duration_seconds=5.0,
                output_dir=tmpdir,
            )

            assert isinstance(result, SFXResult)
            assert result.cost_usd == SFX_COST_PER_CLIP
            assert os.path.exists(result.audio_path)
            with open(result.audio_path, "rb") as f:
                assert f.read() == b"fake-audio-bytes"

    async def test_raises_on_http_error(self) -> None:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Server Error",
                request=MagicMock(),
                response=mock_response,
            )
        )

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with (
            patch("pipeline.long_video.sfx.httpx.AsyncClient", return_value=mock_client),
            patch("pipeline.long_video.sfx.get_settings") as mock_settings,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key-123"

            with pytest.raises(httpx.HTTPStatusError):
                await generate_sfx(description="fail sfx")

    async def test_uses_temp_dir_when_no_output_dir(self) -> None:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b"audio-data"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with (
            patch("pipeline.long_video.sfx.httpx.AsyncClient", return_value=mock_client),
            patch("pipeline.long_video.sfx.get_settings") as mock_settings,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key-123"

            result = await generate_sfx(description="whoosh")
            assert os.path.exists(result.audio_path)
            assert result.audio_path.endswith(".mp3")


class TestGenerateSFXBatch:
    async def test_runs_multiple_sfx_in_parallel(self) -> None:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b"audio-bytes"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with (
            patch("pipeline.long_video.sfx.httpx.AsyncClient", return_value=mock_client),
            patch("pipeline.long_video.sfx.get_settings") as mock_settings,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key-123"

            descriptions = [
                {"description": "whoosh", "duration_seconds": 2.0},
                {"description": "splash", "duration_seconds": 3.0},
                {"description": "boom", "duration_seconds": 1.5},
            ]

            results = await generate_sfx_batch(descriptions, output_dir=tmpdir)

            assert len(results) == 3
            assert all(isinstance(r, SFXResult) for r in results)
            assert mock_client.post.call_count == 3

    async def test_returns_none_for_failed_items(self) -> None:
        success_response = MagicMock(spec=httpx.Response)
        success_response.status_code = 200
        success_response.content = b"audio-bytes"
        success_response.raise_for_status = MagicMock()

        fail_response = MagicMock(spec=httpx.Response)
        fail_response.status_code = 500
        fail_response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Server Error",
                request=MagicMock(),
                response=fail_response,
            )
        )

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=[success_response, fail_response])

        with (
            patch("pipeline.long_video.sfx.httpx.AsyncClient", return_value=mock_client),
            patch("pipeline.long_video.sfx.get_settings") as mock_settings,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key-123"

            descriptions = [
                {"description": "whoosh", "duration_seconds": 2.0},
                {"description": "fail", "duration_seconds": 3.0},
            ]

            results = await generate_sfx_batch(descriptions, output_dir=tmpdir)

            assert len(results) == 2
            assert isinstance(results[0], SFXResult)
            assert results[1] is None
