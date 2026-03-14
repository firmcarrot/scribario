"""Tests for voice pool rotation and selection."""

from __future__ import annotations

import pytest

from pipeline.prompt_engine.voice_pool import (
    VoicePoolEntry,
    select_voice_from_pool,
)


class TestVoicePoolEntry:
    def test_create_entry(self) -> None:
        entry = VoicePoolEntry(
            voice_id="abc123",
            gender="female",
            style_label="confident female narrator",
        )
        assert entry.voice_id == "abc123"
        assert entry.gender == "female"

    def test_to_dict(self) -> None:
        entry = VoicePoolEntry(
            voice_id="abc123",
            gender="male",
            style_label="warm baritone",
        )
        d = entry.to_dict()
        assert d == {"voice_id": "abc123", "gender": "male", "style_label": "warm baritone"}

    def test_from_dict(self) -> None:
        entry = VoicePoolEntry.from_dict(
            {"voice_id": "abc123", "gender": "female", "style_label": "upbeat young woman"}
        )
        assert entry.voice_id == "abc123"
        assert entry.gender == "female"


class TestSelectVoiceFromPool:
    def test_empty_pool_returns_none(self) -> None:
        result = select_voice_from_pool([], "confident female narrator")
        assert result is None

    def test_exact_gender_match(self) -> None:
        pool = [
            VoicePoolEntry("male1", "male", "deep male narrator"),
            VoicePoolEntry("female1", "female", "warm female narrator"),
        ]
        result = select_voice_from_pool(pool, "energetic female voice")
        assert result is not None
        assert result.gender == "female"

    def test_gender_match_male(self) -> None:
        pool = [
            VoicePoolEntry("male1", "male", "deep male narrator"),
            VoicePoolEntry("female1", "female", "warm female narrator"),
        ]
        result = select_voice_from_pool(pool, "confident male narrator")
        assert result is not None
        assert result.gender == "male"

    def test_no_gender_match_picks_from_full_pool(self) -> None:
        """When voice_style has no gender cue, pick from full pool."""
        pool = [
            VoicePoolEntry("v1", "male", "narrator"),
            VoicePoolEntry("v2", "female", "narrator"),
        ]
        result = select_voice_from_pool(pool, "professional narrator")
        assert result is not None
        assert result.voice_id in ("v1", "v2")

    def test_random_selection_among_gender_matches(self) -> None:
        """When multiple entries match gender, pick randomly (not always first)."""
        import random
        pool = [
            VoicePoolEntry("m1", "male", "deep baritone"),
            VoicePoolEntry("m2", "male", "energetic young male"),
        ]
        # With seeded random, verify we get both voices across many calls
        random.seed(42)
        results = {select_voice_from_pool(pool, "male narrator").voice_id for _ in range(20)}
        assert len(results) == 2, f"Expected both voices, got {results}"


from unittest.mock import AsyncMock, MagicMock, patch
from pipeline.long_video.voice_library import get_voice_from_pool_or_create, VoiceInfo


class TestGetVoiceFromPoolOrCreate:
    @pytest.mark.asyncio
    async def test_pool_hit_returns_match(self) -> None:
        """When pool has a matching voice, use it without calling ElevenLabs."""
        pool = [{"voice_id": "f1", "gender": "female", "style_label": "warm"}]
        result = await get_voice_from_pool_or_create(
            tenant_id="t1", voice_style="female narrator", voice_pool=pool,
        )
        assert result.voice_id == "f1"

    @pytest.mark.asyncio
    async def test_empty_pool_falls_back_to_create(self) -> None:
        """Empty pool should fall back to get_or_create_voice."""
        with patch(
            "pipeline.long_video.voice_library.get_or_create_voice",
            new_callable=AsyncMock,
            return_value=VoiceInfo(voice_id="default", name="default", is_new=False),
        ) as mock_create:
            result = await get_voice_from_pool_or_create(
                tenant_id="t1", voice_style="narrator", voice_pool=[],
            )
            assert result.voice_id == "default"
            mock_create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_none_pool_falls_back_to_create(self) -> None:
        """None pool should fall back to get_or_create_voice."""
        with patch(
            "pipeline.long_video.voice_library.get_or_create_voice",
            new_callable=AsyncMock,
            return_value=VoiceInfo(voice_id="default", name="default", is_new=False),
        ) as mock_create:
            result = await get_voice_from_pool_or_create(
                tenant_id="t1", voice_style="narrator", voice_pool=None,
            )
            assert result.voice_id == "default"
            mock_create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_new_voice_appended_to_pool(self) -> None:
        """When a new voice is created, it should be appended to voice_pool JSONB."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.update.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = MagicMock()

        with patch(
            "pipeline.long_video.voice_library.get_or_create_voice",
            new_callable=AsyncMock,
            return_value=VoiceInfo(voice_id="new_voice_123", name="Brand Voice", is_new=True),
        ), patch(
            "pipeline.long_video.voice_library.get_supabase_client",
            return_value=mock_client,
        ):
            result = await get_voice_from_pool_or_create(
                tenant_id="t1",
                voice_style="confident female narrator",
                voice_pool=[],
            )
            assert result.voice_id == "new_voice_123"
            # Verify pool was updated in DB
            mock_table.update.assert_called_once()
            update_arg = mock_table.update.call_args[0][0]
            assert "voice_pool" in update_arg
            assert len(update_arg["voice_pool"]) == 1
            assert update_arg["voice_pool"][0]["voice_id"] == "new_voice_123"
            assert update_arg["voice_pool"][0]["gender"] == "female"

    @pytest.mark.asyncio
    async def test_existing_voice_not_appended_to_pool(self) -> None:
        """When an existing voice is returned (is_new=False), pool should not be updated."""
        with patch(
            "pipeline.long_video.voice_library.get_or_create_voice",
            new_callable=AsyncMock,
            return_value=VoiceInfo(voice_id="existing", name="cached", is_new=False),
        ) as mock_create, patch(
            "pipeline.long_video.voice_library.get_supabase_client",
        ) as mock_get_client:
            result = await get_voice_from_pool_or_create(
                tenant_id="t1", voice_style="narrator", voice_pool=[],
            )
            assert result.voice_id == "existing"
            # Should NOT have called update on the DB
            mock_get_client.return_value.table.return_value.update.assert_not_called()
