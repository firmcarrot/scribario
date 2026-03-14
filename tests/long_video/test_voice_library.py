"""Tests for ElevenLabs voice library — create/cache branded voices per tenant."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from pipeline.long_video.voice_library import (
    DEFAULT_VOICE_ID,
    ELEVENLABS_BASE_URL,
    VoiceInfo,
    get_or_create_voice,
)

TENANT_ID = "52590da5-bc80-4161-ac13-62e9bcd75424"


class TestGetOrCreateVoiceReturnsExisting:
    """When brand_profiles already has a voice_id, return it without calling ElevenLabs."""

    async def test_returns_cached_voice_id(self) -> None:
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"voice_id": "existing-voice-123"}]
        )

        with patch("pipeline.long_video.voice_library.get_supabase_client", return_value=mock_client):
            result = await get_or_create_voice(TENANT_ID)

        assert result.voice_id == "existing-voice-123"
        assert result.name == "cached"
        assert result.is_new is False

    async def test_does_not_call_elevenlabs_when_cached(self) -> None:
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"voice_id": "existing-voice-123"}]
        )

        with (
            patch("pipeline.long_video.voice_library.get_supabase_client", return_value=mock_client),
            patch("pipeline.long_video.voice_library.httpx.AsyncClient") as mock_httpx,
        ):
            await get_or_create_voice(TENANT_ID)
            mock_httpx.assert_not_called()


class TestGetOrCreateVoiceCreatesNew:
    """When no voice_id in DB, create one via ElevenLabs API and store it."""

    async def test_creates_voice_via_elevenlabs(self) -> None:
        # DB returns no voice_id
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"voice_id": None}]
        )
        # Update call
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{}]
        )

        # Mock ElevenLabs API responses
        preview_response = MagicMock()
        preview_response.status_code = 200
        preview_response.json.return_value = {
            "previews": [{"generated_voice_id": "preview-voice-abc", "audio_base_64": "base64data"}]
        }
        preview_response.raise_for_status = MagicMock()

        create_response = MagicMock()
        create_response.status_code = 200
        create_response.json.return_value = {"voice_id": "final-voice-xyz"}
        create_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(side_effect=[preview_response, create_response])
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("pipeline.long_video.voice_library.get_supabase_client", return_value=mock_client),
            patch("pipeline.long_video.voice_library.httpx.AsyncClient", return_value=mock_http_client),
        ):
            result = await get_or_create_voice(TENANT_ID, tenant_name="Mondo Shrimp")

        assert result.voice_id == "final-voice-xyz"
        assert result.is_new is True

    async def test_handles_empty_db_row(self) -> None:
        """When brand_profiles has no row at all for this tenant."""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{}]
        )

        preview_response = MagicMock()
        preview_response.status_code = 200
        preview_response.json.return_value = {
            "previews": [{"generated_voice_id": "preview-abc", "audio_base_64": "data"}]
        }
        preview_response.raise_for_status = MagicMock()

        create_response = MagicMock()
        create_response.status_code = 200
        create_response.json.return_value = {"voice_id": "new-voice-456"}
        create_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(side_effect=[preview_response, create_response])
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("pipeline.long_video.voice_library.get_supabase_client", return_value=mock_client),
            patch("pipeline.long_video.voice_library.httpx.AsyncClient", return_value=mock_http_client),
        ):
            result = await get_or_create_voice(TENANT_ID)

        assert result.voice_id == "new-voice-456"
        assert result.is_new is True


class TestGetOrCreateVoiceStoresNew:
    """After creating a voice, store voice_id back in brand_profiles."""

    async def test_updates_brand_profiles_with_voice_id(self) -> None:
        mock_client = MagicMock()
        # Select returns no voice_id
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"voice_id": None}]
        )
        mock_update_chain = MagicMock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute = mock_update_chain

        preview_response = MagicMock()
        preview_response.status_code = 200
        preview_response.json.return_value = {
            "previews": [{"generated_voice_id": "preview-abc", "audio_base_64": "data"}]
        }
        preview_response.raise_for_status = MagicMock()

        create_response = MagicMock()
        create_response.status_code = 200
        create_response.json.return_value = {"voice_id": "stored-voice-789"}
        create_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(side_effect=[preview_response, create_response])
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("pipeline.long_video.voice_library.get_supabase_client", return_value=mock_client),
            patch("pipeline.long_video.voice_library.httpx.AsyncClient", return_value=mock_http_client),
        ):
            await get_or_create_voice(TENANT_ID)

        # Verify update was called on brand_profiles
        mock_client.table.assert_any_call("brand_profiles")
        mock_update_chain.assert_called()


class TestGetOrCreateVoiceErrorHandling:
    """On any error, fall back to DEFAULT_VOICE_ID gracefully."""

    async def test_returns_default_on_api_error(self) -> None:
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"voice_id": None}]
        )

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(side_effect=httpx.HTTPStatusError(
            "500 Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500),
        ))
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("pipeline.long_video.voice_library.get_supabase_client", return_value=mock_client),
            patch("pipeline.long_video.voice_library.httpx.AsyncClient", return_value=mock_http_client),
        ):
            result = await get_or_create_voice(TENANT_ID)

        assert result.voice_id == DEFAULT_VOICE_ID
        assert result.is_new is False

    async def test_returns_default_on_db_error(self) -> None:
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.side_effect = Exception(
            "DB connection failed"
        )

        with patch("pipeline.long_video.voice_library.get_supabase_client", return_value=mock_client):
            result = await get_or_create_voice(TENANT_ID)

        assert result.voice_id == DEFAULT_VOICE_ID
        assert result.is_new is False

    async def test_returns_default_when_column_missing(self) -> None:
        """If voice_id column doesn't exist, KeyError should be caught."""
        mock_client = MagicMock()
        # Row exists but no voice_id key at all
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"tenant_id": TENANT_ID, "tone_words": ["bold"]}]
        )

        # This should still try to create a voice, so mock the API
        preview_response = MagicMock()
        preview_response.status_code = 200
        preview_response.json.return_value = {
            "previews": [{"generated_voice_id": "preview-abc", "audio_base_64": "data"}]
        }
        preview_response.raise_for_status = MagicMock()

        create_response = MagicMock()
        create_response.status_code = 200
        create_response.json.return_value = {"voice_id": "new-voice-for-missing-col"}
        create_response.raise_for_status = MagicMock()

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(side_effect=[preview_response, create_response])
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        # Update might fail if column doesn't exist — that should be caught
        mock_client.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception(
            "column voice_id does not exist"
        )

        with (
            patch("pipeline.long_video.voice_library.get_supabase_client", return_value=mock_client),
            patch("pipeline.long_video.voice_library.httpx.AsyncClient", return_value=mock_http_client),
        ):
            result = await get_or_create_voice(TENANT_ID)

        # Should still return the voice even if DB update fails
        assert result.voice_id == "new-voice-for-missing-col"
        assert result.is_new is True

    async def test_returns_default_on_network_timeout(self) -> None:
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"voice_id": ""}]
        )

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(side_effect=httpx.ConnectTimeout("Connection timed out"))
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("pipeline.long_video.voice_library.get_supabase_client", return_value=mock_client),
            patch("pipeline.long_video.voice_library.httpx.AsyncClient", return_value=mock_http_client),
        ):
            result = await get_or_create_voice(TENANT_ID)

        assert result.voice_id == DEFAULT_VOICE_ID
        assert result.is_new is False
