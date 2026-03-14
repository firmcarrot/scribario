"""Tests for ElevenLabs TTS voiceover generation."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from pipeline.long_video.tts import (
    ELEVENLABS_BASE_URL,
    TTS_COST_PER_SCENE,
    TTSResult,
    generate_voiceover,
    generate_voiceovers_sequential,
)


def _fake_mp3_bytes(duration_seconds: float) -> bytes:
    """Create fake MP3-sized bytes for a given duration.

    At 128kbps: size = duration * 128000 / 8 = duration * 16000
    """
    size = int(duration_seconds * 16000)
    return b"\x00" * size


def _fake_request(voice_id: str = "v1") -> httpx.Request:
    """Create a fake httpx.Request for mock responses."""
    return httpx.Request(
        "POST",
        f"{ELEVENLABS_BASE_URL}/v1/text-to-speech/{voice_id}",
    )


class TestTTSResult:
    def test_tts_result_fields(self) -> None:
        result = TTSResult(
            audio_url="/tmp/test.mp3",
            duration_seconds=5.0,
            cost_usd=0.01,
        )
        assert result.audio_url == "/tmp/test.mp3"
        assert result.duration_seconds == 5.0
        assert result.cost_usd == 0.01


class TestGenerateVoiceover:
    async def test_makes_correct_api_call(self) -> None:
        """Verify we POST to /v1/text-to-speech/{voice_id} with correct payload."""
        voice_id = "test-voice-123"
        text = "In a world of bland condiments..."
        fake_audio = _fake_mp3_bytes(5.0)

        mock_response = httpx.Response(
            status_code=200,
            content=fake_audio,
            headers={"content-type": "audio/mpeg"},
            request=_fake_request(voice_id),
        )

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("pipeline.long_video.tts.httpx.AsyncClient") as mock_client_cls,
            patch("pipeline.long_video.tts.get_settings") as mock_settings,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-api-key"
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await generate_voiceover(
                text=text,
                voice_id=voice_id,
                output_dir=tmpdir,
            )

            # Verify the API call
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            expected_url = f"{ELEVENLABS_BASE_URL}/v1/text-to-speech/{voice_id}"
            assert call_args[0][0] == expected_url

            # Verify payload includes model_id and text
            payload = call_args[1]["json"]
            assert payload["text"] == text
            assert payload["model_id"] == "eleven_turbo_v2_5"

            # Verify headers include API key
            headers = call_args[1]["headers"]
            assert headers["xi-api-key"] == "test-api-key"

    async def test_returns_tts_result_with_correct_fields(self) -> None:
        """Verify TTSResult has audio_url, duration_seconds, cost_usd."""
        fake_audio = _fake_mp3_bytes(7.5)

        mock_response = httpx.Response(
            status_code=200,
            content=fake_audio,
            headers={"content-type": "audio/mpeg"},
            request=_fake_request("voice-1"),
        )

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("pipeline.long_video.tts.httpx.AsyncClient") as mock_client_cls,
            patch("pipeline.long_video.tts.get_settings") as mock_settings,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key"
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await generate_voiceover(
                text="Test text",
                voice_id="voice-1",
                output_dir=tmpdir,
            )

            assert isinstance(result, TTSResult)
            assert result.audio_url.endswith(".mp3")
            assert os.path.dirname(result.audio_url) == tmpdir
            assert result.cost_usd == TTS_COST_PER_SCENE

    async def test_estimates_duration_from_file_size(self) -> None:
        """Duration should be estimated from MP3 size at 128kbps."""
        target_duration = 10.0
        fake_audio = _fake_mp3_bytes(target_duration)

        mock_response = httpx.Response(
            status_code=200,
            content=fake_audio,
            headers={"content-type": "audio/mpeg"},
            request=_fake_request("voice-1"),
        )

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("pipeline.long_video.tts.httpx.AsyncClient") as mock_client_cls,
            patch("pipeline.long_video.tts.get_settings") as mock_settings,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key"
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await generate_voiceover(
                text="Test text",
                voice_id="voice-1",
                output_dir=tmpdir,
            )

            # Duration = file_size / (128000 / 8) = file_size / 16000
            assert abs(result.duration_seconds - target_duration) < 0.1

    async def test_saves_audio_to_file(self) -> None:
        """Verify the audio bytes are written to disk."""
        fake_audio = _fake_mp3_bytes(3.0)

        mock_response = httpx.Response(
            status_code=200,
            content=fake_audio,
            headers={"content-type": "audio/mpeg"},
            request=_fake_request(),
        )

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("pipeline.long_video.tts.httpx.AsyncClient") as mock_client_cls,
            patch("pipeline.long_video.tts.get_settings") as mock_settings,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key"
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await generate_voiceover(
                text="Test",
                voice_id="v1",
                output_dir=tmpdir,
            )

            assert os.path.exists(result.audio_url)
            with open(result.audio_url, "rb") as f:
                saved_bytes = f.read()
            assert saved_bytes == fake_audio

    async def test_error_handling_on_api_failure(self) -> None:
        """Should raise on non-200 response from ElevenLabs."""
        mock_response = httpx.Response(
            status_code=500,
            content=b"Internal Server Error",
            headers={"content-type": "text/plain"},
            request=_fake_request(),
        )

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("pipeline.long_video.tts.httpx.AsyncClient") as mock_client_cls,
            patch("pipeline.long_video.tts.get_settings") as mock_settings,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key"
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)

            with pytest.raises(httpx.HTTPStatusError):
                await generate_voiceover(
                    text="Test",
                    voice_id="v1",
                    output_dir=tmpdir,
                )

    async def test_error_handling_on_network_error(self) -> None:
        """Should propagate httpx transport errors."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("pipeline.long_video.tts.httpx.AsyncClient") as mock_client_cls,
            patch("pipeline.long_video.tts.get_settings") as mock_settings,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key"
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(
                side_effect=httpx.ConnectError("Connection refused")
            )

            with pytest.raises(httpx.ConnectError):
                await generate_voiceover(
                    text="Test",
                    voice_id="v1",
                    output_dir=tmpdir,
                )

    async def test_uses_default_temp_dir_when_none(self) -> None:
        """When output_dir is None, should use tempfile default."""
        fake_audio = _fake_mp3_bytes(2.0)

        mock_response = httpx.Response(
            status_code=200,
            content=fake_audio,
            headers={"content-type": "audio/mpeg"},
            request=_fake_request(),
        )

        with (
            patch("pipeline.long_video.tts.httpx.AsyncClient") as mock_client_cls,
            patch("pipeline.long_video.tts.get_settings") as mock_settings,
        ):
            mock_settings.return_value.elevenlabs_api_key = "test-key"
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await generate_voiceover(
                text="Test",
                voice_id="v1",
                output_dir=None,
            )

            assert result.audio_url.endswith(".mp3")
            assert os.path.exists(result.audio_url)
            # Cleanup
            os.unlink(result.audio_url)


class TestGenerateVoiceoversSequential:
    async def test_processes_multiple_scenes_in_order(self) -> None:
        """Should call generate_voiceover for each scene sequentially."""
        scenes = [
            {"text": "Scene one narration.", "voice_id": "voice-a"},
            {"text": "Scene two narration.", "voice_id": "voice-b"},
            {"text": "Scene three narration.", "voice_id": "voice-c"},
        ]

        call_order: list[str] = []

        async def mock_generate(
            text: str, voice_id: str, output_dir: str | None = None
        ) -> TTSResult:
            call_order.append(text)
            return TTSResult(
                audio_url=f"/tmp/scene_{len(call_order)}.mp3",
                duration_seconds=5.0 * len(call_order),
                cost_usd=TTS_COST_PER_SCENE,
            )

        with patch("pipeline.long_video.tts.generate_voiceover", side_effect=mock_generate):
            results = await generate_voiceovers_sequential(scenes)

        assert len(results) == 3
        assert call_order == [
            "Scene one narration.",
            "Scene two narration.",
            "Scene three narration.",
        ]
        # Verify results are in order
        assert results[0].duration_seconds == 5.0
        assert results[1].duration_seconds == 10.0
        assert results[2].duration_seconds == 15.0

    async def test_empty_scenes_returns_empty_list(self) -> None:
        """No scenes = no results, no API calls."""
        results = await generate_voiceovers_sequential([])
        assert results == []

    async def test_propagates_error_from_single_scene(self) -> None:
        """If one scene fails, the whole batch should fail."""
        scenes = [
            {"text": "Scene one.", "voice_id": "v1"},
            {"text": "Scene two.", "voice_id": "v2"},
        ]

        call_count = 0

        async def mock_generate(
            text: str, voice_id: str, output_dir: str | None = None
        ) -> TTSResult:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise httpx.HTTPStatusError(
                    "Server Error",
                    request=_fake_request("v2"),
                    response=httpx.Response(500, request=_fake_request("v2")),
                )
            return TTSResult(
                audio_url="/tmp/scene.mp3",
                duration_seconds=5.0,
                cost_usd=TTS_COST_PER_SCENE,
            )

        with patch("pipeline.long_video.tts.generate_voiceover", side_effect=mock_generate):
            with pytest.raises(httpx.HTTPStatusError):
                await generate_voiceovers_sequential(scenes)
