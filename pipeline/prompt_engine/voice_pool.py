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
