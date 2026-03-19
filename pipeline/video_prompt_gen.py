"""Video prompt generation — Claude-powered Veo 3.1 prompt engineering.

Transforms simple user intents (e.g. "make a video about our shrimp special")
into professional cinematographic prompts optimized for Veo 3.1 video generation.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import anthropic

from bot.config import get_settings
from pipeline.brand_voice import BrandProfile, format_brand_context

logger = logging.getLogger(__name__)

# Approximate cost per Claude Sonnet prompt generation call (fallback)
VIDEO_PROMPT_COST_USD = 0.02


@dataclass
class VideoPromptResult:
    """Video prompt with API usage metadata for cost tracking."""

    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    model: str = "claude-sonnet-4-20250514"

    def __str__(self) -> str:
        return self.text

VIDEO_PROMPT_SYSTEM = """You are an expert cinematographer and video prompt engineer specializing in \
AI video generation with Google Veo 3.1.

Your job: transform a simple content idea into a professional video generation prompt that produces \
broadcast-quality 8-second social media videos.

## The Formula (ALWAYS follow this structure)

[Camera/Cinematography] + [Subject] + [Action/Motion] + [Setting/Environment] + [Style/Mood] + [Audio]

## Camera & Cinematography Vocabulary

Use these specific terms — Veo 3.1 understands them:
- Shot types: wide establishing, medium shot, close-up, extreme close-up, over-the-shoulder
- Camera movement: slow pan, dolly-in, tracking shot, crane shot, orbit, push-in, pull-back, reveal
- Angles: low angle, high angle, bird's eye, eye level
- Focus: shallow depth of field, rack focus, bokeh
- Transitions: smooth transition, whip pan

## Style Keywords That Improve Quality
- "Cinematic", "broadcast-quality", "professional cinematography"
- Color: "warm golden light", "cool blue tones", "vibrant saturation"
- Lens: "anamorphic lens", "shallow depth of field", "35mm film"
- Texture: "slightly grainy, film-like" (pushes away AI aesthetic)

## Audio (CRITICAL — Veo 3.1's secret weapon)
ALWAYS include an explicit Audio line at the end:
  Audio: [primary ambient] + [secondary layer] + [effects]
Example: "Audio: sizzling oil, gentle kitchen ambiance, soft upbeat music"
If you don't specify audio, Veo will hallucinate random sounds.
No dialogue for social media videos — keep it visual.

## ABSOLUTE RULES (violating these produces garbage)
- NEVER include any text, words, writing, signs, letters, subtitles, captions, title cards, \
or logo text in the scene — Veo renders these as gibberish
- ONE continuous shot only — no scene changes, no cuts
- Keep it to ONE clear action/moment — 8 seconds max
- Be SPECIFIC — "a golden shrimp sizzling" not "some food cooking"
- Use motion verbs — sizzling, pouring, drizzling, steaming, flowing

## Output Format
- 3-6 sentences, 100-150 words total
- Plain text, no markdown, no labels, no bullet points
- End with "Audio: ..." line

## Content Type Guidelines
- Food/product: extreme close-up, slow dolly, steam/motion, warm lighting
- Lifestyle: tracking shot, golden hour, shallow DOF, ambient music
- Brand reveal: smooth push-in, clean background, particle effects
- Atmosphere: slow pan, cinematic color grading, layered audio"""


async def generate_video_prompt(
    intent: str,
    brand_profile: BrandProfile,
    visual_prompt: str | None = None,
    aspect_ratio: str = "16:9",
    reference_has_image: bool = False,
) -> VideoPromptResult:
    """Transform a user intent into a Veo 3.1-optimized video prompt.

    Args:
        intent: What the user wants the video to show.
        brand_profile: Brand identity for context.
        visual_prompt: Optional image visual_prompt from caption gen (scene context).
        aspect_ratio: Target aspect ratio ("16:9" or "9:16").
        reference_has_image: Whether a reference image will be used.

    Returns:
        VideoPromptResult with prompt text and token usage for cost tracking.
        On failure, falls back to visual_prompt or intent with None tokens.
    """
    brand_context = format_brand_context(brand_profile, [])

    parts = [
        f"# Brand Context\n{brand_context}",
        f"\n# Video Request\nIntent: {intent}",
        f"\nAspect ratio: {aspect_ratio}",
    ]

    if aspect_ratio == "9:16":
        parts.append(
            "Composition note: This is VERTICAL video (portrait). "
            "Frame subjects in the center, use vertical motion (tilt up/down), "
            "and keep key action in the middle third."
        )
    else:
        parts.append(
            "Composition note: This is LANDSCAPE video. "
            "Use the full horizontal frame, lateral movements work well."
        )

    if visual_prompt:
        parts.append(f"\nScene context from image prompt: {visual_prompt}")

    if reference_has_image:
        parts.append(
            "\nA reference image will be provided alongside this prompt. "
            "The video should animate/bring to life what's shown in the reference image. "
            "Match the reference image's composition and subject closely."
        )

    parts.append(
        "\nGenerate a single Veo 3.1 video prompt following the formula. "
        "3-6 sentences, 100-150 words. End with an Audio line."
    )

    user_message = "\n".join(parts)

    model = "claude-sonnet-4-20250514"
    try:
        client = anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)
        response = await client.messages.create(
            model=model,
            max_tokens=500,
            system=VIDEO_PROMPT_SYSTEM,
            messages=[{"role": "user", "content": user_message}],
        )

        input_tokens = getattr(response.usage, "input_tokens", None)
        output_tokens = getattr(response.usage, "output_tokens", None)

        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content += block.text

        result = text_content.strip()
        result = sanitize_video_prompt(result)

        # If sanitizer stripped everything, fall back to raw response
        if not result:
            logger.warning("Sanitizer stripped all sentences, using raw response")
            result = text_content.strip()

        logger.info(
            "Video prompt generated",
            extra={
                "intent": intent[:50],
                "word_count": len(result.split()),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )
        return VideoPromptResult(
            text=result,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
        )

    except Exception as exc:
        logger.warning(
            "Video prompt gen failed, using fallback",
            extra={"error": str(exc), "intent": intent[:50]},
        )
        return VideoPromptResult(text=visual_prompt or intent)


# Patterns that indicate text-in-scene instructions (Veo renders these as gibberish)
_FORBIDDEN_PATTERNS = re.compile(
    r'\b(?:text\s+overlay|text\s+reading|text\s+saying|'
    r'sign\s+reads|sign\s+saying|sign\s+that\s+reads|'
    r'with\s+(?:the\s+)?(?:text|words|writing|letters?|subtitle|caption|title\s+card|logo\s+text)'
    r'|subtitle|title\s+card|logo\s+text)\b',
    re.IGNORECASE,
)


def sanitize_video_prompt(prompt: str) -> str:
    """Remove sentences containing forbidden text-in-scene instructions.

    Veo 3.1 renders any text/signs/words as gibberish, so we strip sentences
    that instruct the model to include them — insurance against Claude hallucinating
    these despite system prompt instructions.
    """
    if not prompt:
        return ""

    # Split into sentences (period, exclamation, or end of string)
    sentences = re.split(r'(?<=[.!?])\s+', prompt)
    clean = [s for s in sentences if not _FORBIDDEN_PATTERNS.search(s)]

    return " ".join(clean).strip()
