# Content Quality & Voice Rotation Upgrade

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform Scribario's content from generic corporate filler into scroll-stopping social media content using proven copywriting formulas (Brunson, Dan Henry), add voice gender/style rotation for videos, and close the gap where videos don't get captions like images do.

**Architecture:** Three changes: (1) New caption quality layer in the Prompt Engine system prompt with rotating copywriting formulas and anti-corporate rules, (2) Voice pool system on brand_profiles so each brand has 2-3 voices that rotate across videos with scene-aware gender matching, (3) Wire long video preview to use plan captions instead of raw intent text.

**Tech Stack:** Python 3.11+, Claude Sonnet (tool_use structured output), ElevenLabs Voice Design API, Supabase Postgres.

---

## Context

### The Problems (Ron's words)

1. **Caption quality sucks.** "Short, no strong storytelling, or CTA hooks or anything." The system prompt has zero guidance for writing captions — it only covers image/animation prompts.
2. **Videos don't get captions.** Long video previews show raw intent text instead of the Prompt Engine's captions.
3. **Same voice every time.** No male/female rotation, no voice pool per brand. Every video sounds identical.
4. **No content rotation.** Every post uses the same structure — just swapping a few words.

### Research Findings

**Russell Brunson — Hook-Story-Offer:**
- Hook (first line, <3 seconds to stop the scroll)
- Story (epiphany bridge — share a real moment, build emotional connection)
- Offer/CTA (specific action, not generic "check us out")

**Dan Henry — Raw Directness:**
- Write like you talk, not like a press release
- If the hook doesn't grab in one line, nothing else matters
- "It's still a human world. People are walking down the grocery aisle looking at your ad."

**2026 Trending Patterns:**
- Posts with specific CTAs get 3x more engagement
- 85% watch video without sound — caption IS the content
- Odd-numbered lists feel more authentic than even
- Failure/struggle stories outperform success stories
- Saves and comment replies signal higher value to algorithms

**ElevenLabs Voice API:**
- Voices have gender, age, accent, tone labels
- Voice Design API creates voices from text descriptions (already implemented in `voice_library.py`)
- `brand_profiles` table needs `voice_pool` JSONB column (currently only has `voice_id` on `video_projects`)

### Key Files

- `pipeline/prompt_engine/system_prompt.py` — where caption quality rules go
- `pipeline/prompt_engine/engine.py` — tool schema for captions (may need `caption_formula` field)
- `pipeline/prompt_engine/models.py` — GenerationPlan dataclasses
- `pipeline/long_video/voice_library.py` — existing voice create/cache logic (ONE voice per brand)
- `pipeline/long_video/orchestrator.py` — where voice is selected for TTS
- `pipeline/brand_voice.py` — BrandProfile dataclass (needs voice_pool field)
- `worker/jobs/generate_long_video.py` — long video preview uses raw intent, not captions
- `worker/jobs/generate_content.py` — short-form pipeline (already uses plan captions)

### Design Decisions

**Q: Should Claude detect gender from scene content to match voice?**
A: Yes, but NOT via external gender detection API (over-engineered, adds cost, privacy concern). Instead: Claude already knows what's in each scene because it wrote the prompts. The system prompt tells Claude to set `voice_style` to include gender cue (e.g., "confident female narrator" or "energetic male voice"). The orchestrator then picks from the brand's voice pool based on the gender/style descriptor.

**Q: How does voice rotation work?**
A: Brand profile stores a `voice_pool`: array of `{voice_id, gender, style_label}`. When the Prompt Engine picks a `voice_style`, the orchestrator maps it to the best matching voice from the pool. If no pool exists yet, voices are created on first use via ElevenLabs Voice Design API and cached in the pool.

**Q: How does caption formula rotation work?**
A: The system prompt lists 5 formulas (Hook-Story-Offer, PAS, Punchy One-Liner, Story-Lesson, List/Value Drop). It instructs Claude: "Each of the 3 caption options MUST use a DIFFERENT formula. Vary which formula appears first across different generation calls."

**Q: What about user override?**
A: The system prompt has explicit rules: if the user's intent contains quoted text or very specific instructions, use it as-is or light polish only. If intent is vague/directional, go full creative.

---

## Task 1: Caption Quality Rules — Tests

**Files:**
- Modify: `tests/prompt_engine/test_system_prompt.py`

Tests were already written in the previous session. Verify they exist and fail.

**Step 1: Run existing tests to confirm the new ones fail**

Run: `python3 -m pytest tests/prompt_engine/test_system_prompt.py -v`
Expected: 4 new tests FAIL (test_contains_caption_quality_rules, test_caption_rules_have_hook_types, test_caption_rules_apply_to_all_formats, test_caption_rules_require_three_options), 12 old tests PASS.

---

## Task 2: Caption Quality Rules — Implementation

**Files:**
- Modify: `pipeline/prompt_engine/system_prompt.py`

**Step 1: Add the `_CAPTION_QUALITY_RULES` layer**

Add this new constant after `_QUALITY_RULES`:

```python
_CAPTION_QUALITY_RULES = """\
## Caption & Content Quality Rules (CRITICAL — THIS IS THE MOST IMPORTANT SECTION)

Captions are the #1 driver of engagement. They apply to ALL content formats — images AND videos.
Always generate exactly 3 caption options. Each option MUST use a DIFFERENT formula from the list below.

### The 5 Caption Formulas (rotate these — never use the same one twice in one generation)

1. **Hook-Story-Offer (Russell Brunson):**
   - Hook: One bold, scroll-stopping first line (5-10 words max)
   - Story: 2-4 sentences telling a real moment, a realization, or a "you know that feeling when..." bridge
   - Offer/CTA: Specific action ("Comment SAUCE if you've been there" / "Tag someone who needs this")

2. **PAS (Problem-Agitate-Solution):**
   - Problem: Name the pain your audience knows ("Tired of bland hot sauce that promises heat and delivers nothing?")
   - Agitate: Twist the knife ("You've tried them all. The ones with scary labels that taste like ketchup with attitude.")
   - Solution: Your product/brand as the answer, with CTA

3. **Punchy One-Liner + CTA:**
   - One devastatingly good line. No story. Just a mic drop followed by a specific CTA.
   - Example energy: "Life's too short for mild sauce." + "Double-tap if you agree."

4. **Story-Lesson (Epiphany Bridge):**
   - Open with a scene: "Last Tuesday, a customer walked in and..."
   - Build to a realization or lesson
   - End with how it connects to the brand/product + CTA

5. **List/Value Drop:**
   - "3 reasons your hot sauce shelf is lying to you"
   - Deliver real value in a scannable format (odd numbers perform better — 3, 5, 7)
   - End with CTA tied to the list content

### Hook Types (use a DIFFERENT hook type for each caption option)

- **Question hook:** "Want to know what happens when you put ghost pepper on everything?"
- **Bold/contrarian statement:** "Hot sauce companies have been lying to you."
- **Curiosity gap:** "This one ingredient changed everything..."
- **Story opener:** "Last Tuesday a customer said something I'll never forget."
- **Number/list hook:** "3 reasons your hot sauce shelf is wrong"
- **Urgency/scarcity:** "We almost didn't make this batch."

### Mandatory Rules for ALL Captions

- Write like you TALK. If you wouldn't say it to a friend, don't post it.
- NEVER use corporate language: "We're thrilled to announce", "Check out our latest", "Don't miss out",
  "Excited to share", "We're proud to present", "Stay tuned", "Click the link in bio"
- NEVER start with the brand name. Lead with the hook, not "Mondo Shrimp is..."
- Every caption MUST have a specific CTA. "Comment X below" beats "let me know" by 3x.
- Keep it conversational and authentic — channel the brand's tone words, not a marketing textbook.
- Hashtags: 3-5 relevant ones at the END, never mid-sentence. Mix branded + discovery tags.
- For VIDEO content: the caption is critical because 85% of people watch without sound.
  The caption must tell the story independently of the video.

### User Intent Override Rules

- If the user provides EXACT text in quotes → use it as-is, just add hashtags
- If the user gives a specific direction ("funny post about...") → be creative but follow the direction
- If the user is vague ("post about our sauce") → go full creative, pick the best formulas
- When in doubt: be MORE creative, not less. The user hired an AI to be better than they could do themselves."""
```

**Step 2: Add the caption rules layer to `build_system_prompt()`**

In the `layers` list inside `build_system_prompt()`, add `_CAPTION_QUALITY_RULES` after `_QUALITY_RULES`:

```python
    layers = [
        _ROLE_LAYER,
        _FORMAT_RULES,
        _SCENE_RULES,
        _REF_IMAGE_STRATEGY,
        _VEO_RULES,
        _QUALITY_RULES,
        _CAPTION_QUALITY_RULES,  # <-- ADD THIS
        f"## Brand Context\n\n{brand_context}",
        asset_context,
    ]
```

**Step 3: Run tests**

Run: `python3 -m pytest tests/prompt_engine/test_system_prompt.py -v`
Expected: All 16 tests PASS.

**Step 4: Commit**

```bash
git add pipeline/prompt_engine/system_prompt.py tests/prompt_engine/test_system_prompt.py
git commit -m "feat: add caption quality rules with Brunson/Henry copywriting formulas"
```

---

## Task 3: Voice Pool — DB Migration

**Files:**
- Create: `supabase/migrations/TIMESTAMP_add_voice_pool.sql` (timestamp from MCP)

**Step 1: Apply migration via Supabase MCP**

SQL:
```sql
ALTER TABLE brand_profiles
  ADD COLUMN IF NOT EXISTS voice_pool JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN brand_profiles.voice_pool IS
  'Array of {voice_id, gender, style_label} for voice rotation across videos';
```

Use `apply_migration` via Supabase MCP. Capture the EXACT timestamp from the response.

**Step 2: Save local migration file with MCP timestamp**

Create `supabase/migrations/<MCP_TIMESTAMP>_add_voice_pool.sql` with the exact same SQL.

---

## Task 4: Voice Pool — Model & Library Tests

**Files:**
- Create: `tests/prompt_engine/test_voice_pool.py`

**Step 1: Write failing tests**

```python
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

    def test_no_gender_match_returns_first(self) -> None:
        """When voice_style has no gender cue, return first entry."""
        pool = [
            VoicePoolEntry("v1", "male", "narrator"),
            VoicePoolEntry("v2", "female", "narrator"),
        ]
        result = select_voice_from_pool(pool, "professional narrator")
        assert result is not None
        assert result.voice_id == "v1"

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
```

**Step 2: Run to verify failure**

Run: `python3 -m pytest tests/prompt_engine/test_voice_pool.py -v`
Expected: FAIL — module not found.

---

## Task 5: Voice Pool — Implementation

**Files:**
- Create: `pipeline/prompt_engine/voice_pool.py`

**Step 1: Implement voice pool module**

```python
"""Voice pool — select and rotate voices for video content."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass


@dataclass
class VoicePoolEntry:
    voice_id: str
    gender: str  # "male", "female", "neutral"
    style_label: str

    def to_dict(self) -> dict:
        return {
            "voice_id": self.voice_id,
            "gender": self.gender,
            "style_label": self.style_label,
        }

    @staticmethod
    def from_dict(d: dict) -> VoicePoolEntry:
        return VoicePoolEntry(
            voice_id=d["voice_id"],
            gender=d.get("gender", "neutral"),
            style_label=d.get("style_label", ""),
        )


_FEMALE_KEYWORDS = re.compile(r"\b(female|woman|girl|feminine)\b", re.IGNORECASE)
_MALE_KEYWORDS = re.compile(r"\b(male|man|boy|masculine)\b", re.IGNORECASE)


def _detect_gender_from_style(voice_style: str) -> str | None:
    """Extract gender cue from a voice_style descriptor string."""
    has_female = bool(_FEMALE_KEYWORDS.search(voice_style))
    has_male = bool(_MALE_KEYWORDS.search(voice_style))
    if has_female and not has_male:
        return "female"
    if has_male and not has_female:
        return "male"
    return None  # ambiguous or no cue


def select_voice_from_pool(
    pool: list[VoicePoolEntry],
    voice_style: str,
) -> VoicePoolEntry | None:
    """Pick the best voice from the pool based on style + random rotation.

    1. Parse gender from voice_style
    2. Filter pool by matching gender (or use full pool if no match)
    3. Random selection among candidates (gives natural variety without tracking state)
    """
    if not pool:
        return None

    # Step 1: detect desired gender
    desired_gender = _detect_gender_from_style(voice_style)

    # Step 2: filter by gender
    if desired_gender:
        candidates = [e for e in pool if e.gender == desired_gender]
    else:
        candidates = list(pool)

    # Fallback: if no candidates match gender, use full pool
    if not candidates:
        candidates = list(pool)

    # Step 3: random selection for natural variety
    return random.choice(candidates)
```

**Step 2: Run tests**

Run: `python3 -m pytest tests/prompt_engine/test_voice_pool.py -v`
Expected: All 9 tests PASS.

**Step 3: Commit**

```bash
git add pipeline/prompt_engine/voice_pool.py tests/prompt_engine/test_voice_pool.py
git commit -m "feat: add voice pool selection with gender matching and rotation"
```

---

## Task 6: Voice Style Guidance in System Prompt

**Files:**
- Modify: `pipeline/prompt_engine/system_prompt.py`
- Modify: `tests/prompt_engine/test_system_prompt.py`

**Step 1: Write failing test**

Add to `tests/prompt_engine/test_system_prompt.py`:

```python
    def test_contains_voice_style_guidance(self) -> None:
        """System prompt must instruct Claude on voice_style for videos."""
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        prompt_lower = prompt.lower()
        assert "voice_style" in prompt_lower
        assert "male" in prompt_lower or "female" in prompt_lower
        assert "gender" in prompt_lower
```

**Step 2: Run to verify failure**

Run: `python3 -m pytest tests/prompt_engine/test_system_prompt.py::TestBuildSystemPrompt::test_contains_voice_style_guidance -v`
Expected: FAIL.

**Step 3: Add voice style layer to system prompt**

Add after `_CAPTION_QUALITY_RULES`:

```python
_VOICE_STYLE_RULES = """\
## Voice Style Selection (video content only)

The voice_style field controls which narrator voice is used for TTS.
Include BOTH gender AND personality in your voice_style descriptor.

Examples of good voice_style values:
- "confident female narrator, warm and authoritative"
- "energetic young male, playful and slightly irreverent"
- "calm female voice, conversational and trustworthy"
- "bold male narrator, deep baritone with humor"

Rules:
- Match the voice gender to the content: if the video features a female character
  prominently, prefer a female narrator (and vice versa)
- Match the voice energy to the content: hype videos get energetic voices,
  testimonial-style gets calm/warm voices
- VARY the voice_style across different videos for the same brand — don't always
  pick the same gender or energy level
- If the brand's tone is playful/irreverent, the voice should match — don't pair
  a playful brand with a corporate monotone narrator"""
```

Add `_VOICE_STYLE_RULES` to the `layers` list after `_CAPTION_QUALITY_RULES`.

**Step 4: Run all system prompt tests**

Run: `python3 -m pytest tests/prompt_engine/test_system_prompt.py -v`
Expected: All 17 tests PASS.

**Step 5: Commit**

```bash
git add pipeline/prompt_engine/system_prompt.py tests/prompt_engine/test_system_prompt.py
git commit -m "feat: add voice style guidance to system prompt for gender-aware TTS"
```

---

## Task 7: Wire Voice Pool into Orchestrator

**Files:**
- Modify: `pipeline/long_video/orchestrator.py`
- Modify: `pipeline/long_video/voice_library.py`
- Modify: `pipeline/brand_voice.py` (add voice_pool to BrandProfile)
- Modify: `tests/long_video/test_orchestrator.py`

**Step 1: Add voice_pool to BrandProfile**

In `pipeline/brand_voice.py`, add to the `BrandProfile` dataclass (after `default_image_style`):

```python
    voice_pool: list[dict] | None = None  # [{voice_id, gender, style_label}]
```

And in `load_brand_profile()`, the return statement (lines 95-105) explicitly maps each field.
Add `voice_pool` to the return block — the FULL modified return is:

```python
        return BrandProfile(
            tenant_id=tenant_id,
            name=tenant_name,
            tone_words=row.get("tone_words", []),
            audience_description=row.get("audience_description", ""),
            do_list=row.get("do_list", []),
            dont_list=row.get("dont_list", []),
            product_catalog=row.get("product_catalog"),
            compliance_notes=row.get("compliance_notes", ""),
            default_image_style=row.get("default_image_style", "photorealistic"),
            voice_pool=row.get("voice_pool"),  # <-- ADD THIS
        )
```

Also add a test to verify the field is loaded:

```python
# In tests/test_brand_voice.py or equivalent
def test_brand_profile_has_voice_pool():
    profile = BrandProfile(
        tenant_id="t1", name="Test", tone_words=[], audience_description="",
        do_list=[], dont_list=[], voice_pool=[{"voice_id": "v1", "gender": "male", "style_label": "deep"}],
    )
    assert profile.voice_pool is not None
    assert len(profile.voice_pool) == 1
```

**Step 2: Add pool-aware voice selection to voice_library.py**

Add to `pipeline/long_video/voice_library.py`:

```python
from pipeline.prompt_engine.voice_pool import VoicePoolEntry, select_voice_from_pool


async def get_voice_from_pool_or_create(
    tenant_id: str,
    voice_style: str,
    voice_pool: list[dict] | None = None,
    tenant_name: str = "Brand",
) -> VoiceInfo:
    """Select from pool if available, otherwise create and cache.

    1. If voice_pool has entries → select best match via select_voice_from_pool()
    2. If pool is empty → create voice via ElevenLabs, add to pool
    3. Return VoiceInfo
    """
    if voice_pool:
        entries = [VoicePoolEntry.from_dict(d) for d in voice_pool]
        match = select_voice_from_pool(entries, voice_style)
        if match:
            return VoiceInfo(voice_id=match.voice_id, name=match.style_label, is_new=False)

    # Fallback to existing create-and-cache behavior
    return await get_or_create_voice(tenant_id, voice_style, tenant_name)
```

**Step 3: Update orchestrator to use pool-aware selection**

In `pipeline/long_video/orchestrator.py`, change the voice selection line (around line 122):

```python
        # --- 3. Get/create voice (pool-aware) ---
        from pipeline.long_video.voice_library import get_voice_from_pool_or_create
        voice_info = await get_voice_from_pool_or_create(
            tenant_id,
            script.voice_style,
            voice_pool=profile.voice_pool,
            tenant_name=profile.name,
        )
```

**Step 4: Add tests for `get_voice_from_pool_or_create`**

Add to `tests/prompt_engine/test_voice_pool.py`:

```python
from unittest.mock import AsyncMock, patch
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
```

**Step 5: Update existing orchestrator tests for new voice path**

In `tests/long_video/test_orchestrator.py`, change mock targets from:
```python
patch("pipeline.long_video.orchestrator.get_or_create_voice", ...)
```
to:
```python
patch("pipeline.long_video.voice_library.get_voice_from_pool_or_create", ...)
```

And update assertions accordingly. The orchestrator now uses `get_voice_from_pool_or_create` with `voice_pool=profile.voice_pool` parameter.

Also remove the now-unused top-level import of `get_or_create_voice` from `orchestrator.py` (line 26).

**Step 6: Run all tests**

Run: `python3 -m pytest tests/ -x -q`
Expected: All pass.

**Step 6: Commit**

```bash
git add pipeline/brand_voice.py pipeline/long_video/voice_library.py pipeline/long_video/orchestrator.py tests/
git commit -m "feat: wire voice pool into orchestrator for gender-aware TTS rotation"
```

---

## Task 8: Fix Long Video Captions Gap

**Files:**
- Modify: `worker/jobs/generate_long_video.py`
- Modify: `tests/worker/test_generate_long_video.py` (if exists, else create)

**Step 1: Add `captions` to `PipelineResult`**

In `pipeline/long_video/orchestrator.py`, add `captions: list[dict]` to the `PipelineResult` dataclass:

```python
@dataclass
class PipelineResult:
    project_id: str
    video_path: str
    duration_seconds: float
    total_cost_usd: float
    script: LongVideoScript
    scene_count: int
    scenes_completed: int
    captions: list[dict] = field(default_factory=list)  # From GenerationPlan
```

And populate it from the generation plan when available (around the return statement at line 252):

```python
        return PipelineResult(
            ...
            captions=generation_plan.captions if generation_plan else [],
        )
```

**Step 2: Write failing test**

```python
"""Test that long video preview uses generated caption, not raw intent."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest


class TestLongVideoPreviewCaption:
    @pytest.mark.asyncio
    async def test_preview_uses_generated_caption(self) -> None:
        """Long video preview should show the generated caption, not raw intent."""
        from worker.jobs.generate_long_video import _send_video_preview

        with (
            patch("worker.jobs.generate_long_video.get_settings") as mock_settings,
            patch("worker.jobs.generate_long_video.Bot") as MockBot,
        ):
            mock_settings.return_value.telegram_bot_token = "test-token"
            mock_bot = MagicMock()
            mock_bot.send_video = AsyncMock()
            mock_bot.session = MagicMock()
            mock_bot.session.close = AsyncMock()
            MockBot.return_value = mock_bot

            await _send_video_preview(
                chat_id=12345,
                project_id="proj1",
                video_url="https://example.com/video.mp4",
                caption="Life's too short for mild sauce. Double-tap if you agree. #MondoShrimp",
            )

            call_kwargs = mock_bot.send_video.call_args
            caption_sent = call_kwargs.kwargs.get("caption") or call_kwargs[1].get("caption", "")
            assert "mild sauce" in caption_sent
```

**Step 3: Update `_send_video_preview` signature**

The function already accepts `intent: str` as a parameter. Rename it to `caption: str`:

```python
async def _send_video_preview(
    chat_id: int,
    project_id: str,
    video_url: str,
    caption: str,
) -> None:
```

**Step 4: Update the caller in `handle_generate_long_video()`**

The caller currently passes `intent=intent`. After the pipeline runs and returns `PipelineResult`, use the first caption if available:

```python
    # Pick best caption — from plan if available, else fall back to intent
    preview_caption = intent
    if result.captions:
        preview_caption = result.captions[0].get("text", intent)

    await _send_video_preview(
        chat_id=telegram_chat_id,
        project_id=project_id,
        video_url=video_url,
        caption=preview_caption,
    )
```

**Step 4: Run tests**

Run: `python3 -m pytest tests/worker/ -v`
Expected: All pass.

**Step 5: Commit**

```bash
git add worker/jobs/generate_long_video.py tests/worker/
git commit -m "fix: long video preview now shows generated caption instead of raw intent"
```

---

## Task 9: Engine Tool Schema — Caption Formula Field

**Files:**
- Modify: `pipeline/prompt_engine/engine.py`
- Modify: `pipeline/prompt_engine/models.py`

**Step 1: Add `formula` field to caption schema**

In `engine.py`, update the captions section of `_TOOL_SCHEMA`:

```python
            "captions": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "required": ["text", "platform_variant", "formula"],
                    "properties": {
                        "text": {"type": "string"},
                        "platform_variant": {"type": "string"},
                        "formula": {
                            "type": "string",
                            "enum": [
                                "hook_story_offer",
                                "problem_agitate_solution",
                                "punchy_one_liner",
                                "story_lesson",
                                "list_value_drop",
                            ],
                            "description": "Which copywriting formula was used. Each caption MUST use a different formula.",
                        },
                    },
                },
            },
```

This forces Claude to declare which formula it used, which prevents lazy repetition.

**Step 2: Add formula diversity validation to `GenerationPlan.validate()`**

In `pipeline/prompt_engine/models.py`, add to the `validate()` method:

```python
        # Caption formula diversity check
        if len(self.captions) >= 3:
            formulas = {c.get("formula") for c in self.captions if isinstance(c, dict)}
            formulas.discard(None)
            if len(formulas) < 2:
                errors.append("Caption formulas must be diverse — use at least 2 different formulas")
```

**Step 3: Run tests**

Run: `python3 -m pytest tests/prompt_engine/test_engine.py -v`
Expected: All pass (mock responses need updating if they don't include formula field).

**Step 3: Commit**

```bash
git add pipeline/prompt_engine/engine.py
git commit -m "feat: enforce caption formula diversity in tool schema"
```

---

## Task 10: Full Integration Test + Verify All Pass

**Files:**
- Modify: `scripts/test_prompt_engine_e2e.py` (update assertions for new caption structure)

**Step 1: Run full test suite**

Run: `python3 -m pytest tests/ -x -q`
Expected: All tests pass (target: 525+ existing + new tests from this plan).

**Step 2: Update E2E test to verify caption quality**

In `scripts/test_prompt_engine_e2e.py`, add caption quality assertions:

```python
        # Check captions have formula diversity
        if len(plan.captions) >= 3:
            formulas = {cap.get("formula") for cap in plan.captions}
            if len(formulas) < 2:
                errors.append(f"Caption formulas not diverse: {formulas}")

        # Check captions are substantial (not one-liners)
        for i, cap in enumerate(plan.captions):
            text = cap.get("text", "")
            if len(text) < 50:
                errors.append(f"Caption {i} too short ({len(text)} chars)")
```

**Step 3: Run E2E test (requires real API key)**

Run: `python3 scripts/test_prompt_engine_e2e.py`
Expected: 5/5 pass.

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: content quality upgrade — caption formulas, voice rotation, video captions"
```

---

## Verification Checklist

1. All existing tests still pass (525+)
2. New tests pass (voice pool, caption rules, long video caption fix)
3. System prompt contains all 5 copywriting formulas
4. System prompt bans corporate language explicitly
5. System prompt requires 3 different formulas per generation
6. Voice pool entries support gender + style_label
7. Voice selection picks randomly among gender-matched candidates
8. Long video preview shows generated caption, not raw intent
9. Tool schema enforces `formula` field on each caption
10. E2E test confirms caption diversity with real Claude calls

---

## DA Review Fixes Applied

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| C1 | CRITICAL | `voice_pool` never loaded — `load_brand_profile()` maps fields explicitly | Plan now shows full modified return block with `voice_pool=row.get("voice_pool")` |
| C2 | CRITICAL | Dead import in orchestrator after switching to pool-aware function | Plan explicitly removes old import, uses inline import |
| C3 | CRITICAL | `last_used_voice_id` never tracked — rotation doesn't rotate | Replaced sequential rotation with `random.choice()` — no state tracking needed |
| C4 | CRITICAL | Existing orchestrator tests mock old function, will break | Plan includes explicit test update instructions for mock targets |
| H1 | HIGH | No formula diversity validation in `GenerationPlan.validate()` | Added formula diversity check to Task 9 |
| H3 | HIGH | No tests for `get_voice_from_pool_or_create` | Added 3 unit tests (pool hit, empty fallback, None fallback) in Task 7 |
| H4 | HIGH | Long video caption source handwaved | Added `captions` to `PipelineResult`, explicit data flow from plan to preview |
| H5 | HIGH | Design decisions say AIDA but implementation uses List/Value Drop | Fixed documentation to match implementation |
| M1 | MEDIUM | System prompt getting long | Acknowledged — voice style rules are only ~20 lines, acceptable tradeoff |
| M4 | MEDIUM | Test assumes deterministic ordering | Replaced with random-based test that verifies variety over many calls |
