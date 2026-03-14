"""Voice library — create/cache branded ElevenLabs voices per tenant."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from bot.config import get_settings
from bot.db import get_supabase_client

logger = logging.getLogger(__name__)

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io"
DEFAULT_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # ElevenLabs "Adam" as fallback


@dataclass
class VoiceInfo:
    voice_id: str
    name: str
    is_new: bool  # True if just created


async def get_or_create_voice(
    tenant_id: str,
    voice_style: str = "confident male narrator, warm baritone",
    tenant_name: str = "Brand",
) -> VoiceInfo:
    """Get existing or create new branded voice for a tenant.

    1. Check brand_profiles.voice_id for tenant
    2. If exists, return it
    3. If not, call ElevenLabs Voice Design API to create one
    4. Store voice_id in brand_profiles
    5. Return VoiceInfo

    Falls back to DEFAULT_VOICE_ID on any error.
    """
    try:
        return await _get_or_create_voice_inner(tenant_id, voice_style, tenant_name)
    except Exception:
        logger.warning(
            "Failed to get/create voice for tenant %s, using default",
            tenant_id,
            exc_info=True,
        )
        return VoiceInfo(voice_id=DEFAULT_VOICE_ID, name="default", is_new=False)


async def _get_or_create_voice_inner(
    tenant_id: str,
    voice_style: str,
    tenant_name: str,
) -> VoiceInfo:
    """Inner implementation — raises on error so caller can catch."""
    client = get_supabase_client()

    # 1. Check for existing voice_id in brand_profiles
    result = (
        client.table("brand_profiles")
        .select("voice_id")
        .eq("tenant_id", tenant_id)
        .limit(1)
        .execute()
    )

    if result.data:
        voice_id = result.data[0].get("voice_id")
        if voice_id:  # non-None, non-empty
            return VoiceInfo(voice_id=voice_id, name="cached", is_new=False)

    # 2. Create voice via ElevenLabs API
    settings = get_settings()
    voice_id = await _create_elevenlabs_voice(
        api_key=settings.elevenlabs_api_key,
        voice_style=voice_style,
        voice_name=f"{tenant_name} Voice",
    )

    # 3. Store voice_id back to brand_profiles (best-effort)
    try:
        client.table("brand_profiles").update({"voice_id": voice_id}).eq(
            "tenant_id", tenant_id
        ).execute()
    except Exception:
        logger.warning(
            "Failed to store voice_id in brand_profiles for tenant %s "
            "(column may not exist yet)",
            tenant_id,
            exc_info=True,
        )

    return VoiceInfo(voice_id=voice_id, name=f"{tenant_name} Voice", is_new=True)


async def _create_elevenlabs_voice(
    api_key: str,
    voice_style: str,
    voice_name: str,
) -> str:
    """Create a voice via ElevenLabs Voice Design API (two-step process).

    1. POST /v1/text-to-voice/create-previews — get a preview voice
    2. POST /v1/text-to-voice/create-voice-from-preview — finalize it

    Returns the final voice_id.
    """
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30.0) as http:
        # Step 1: Create preview
        preview_resp = await http.post(
            f"{ELEVENLABS_BASE_URL}/v1/text-to-voice/create-previews",
            headers=headers,
            json={
                "voice_description": voice_style,
                "text": "This is a preview of the branded voice for content creation.",
            },
        )
        preview_resp.raise_for_status()
        previews = preview_resp.json()["previews"]
        generated_voice_id = previews[0]["generated_voice_id"]

        # Step 2: Finalize voice from preview
        create_resp = await http.post(
            f"{ELEVENLABS_BASE_URL}/v1/text-to-voice/create-voice-from-preview",
            headers=headers,
            json={
                "voice_name": voice_name,
                "voice_description": voice_style,
                "generated_voice_id": generated_voice_id,
            },
        )
        create_resp.raise_for_status()
        return create_resp.json()["voice_id"]


async def get_voice_from_pool_or_create(
    tenant_id: str,
    voice_style: str,
    voice_pool: list[dict] | None = None,
    tenant_name: str = "Brand",
) -> VoiceInfo:
    """Select from pool if available, otherwise create and add to pool.

    1. If voice_pool has entries → select best match via select_voice_from_pool()
    2. If pool is empty/no match → create voice via ElevenLabs, append to pool JSONB
    3. Return VoiceInfo
    """
    from pipeline.prompt_engine.voice_pool import VoicePoolEntry, select_voice_from_pool

    if voice_pool:
        entries = [VoicePoolEntry.from_dict(d) for d in voice_pool]
        match = select_voice_from_pool(entries, voice_style)
        if match:
            return VoiceInfo(voice_id=match.voice_id, name=match.style_label, is_new=False)

    # Create new voice and add it to the pool
    voice_info = await get_or_create_voice(tenant_id, voice_style, tenant_name)

    if voice_info.is_new and voice_info.voice_id != DEFAULT_VOICE_ID:
        # Detect gender from the style string for pool entry
        from pipeline.prompt_engine.voice_pool import _detect_gender_from_style

        gender = _detect_gender_from_style(voice_style) or "neutral"
        new_entry = VoicePoolEntry(
            voice_id=voice_info.voice_id,
            gender=gender,
            style_label=voice_info.name,
        )

        # Append to voice_pool JSONB in DB (best-effort)
        try:
            client = get_supabase_client()
            existing_pool = list(voice_pool) if voice_pool else []
            existing_pool.append(new_entry.to_dict())
            client.table("brand_profiles").update(
                {"voice_pool": existing_pool}
            ).eq("tenant_id", tenant_id).execute()
            logger.info(
                "Added new voice to pool",
                extra={"tenant_id": tenant_id, "voice_id": voice_info.voice_id, "gender": gender},
            )
        except Exception:
            logger.warning(
                "Failed to append voice to pool for tenant %s",
                tenant_id,
                exc_info=True,
            )

    return voice_info
