"""Caption generation — Claude API with brand voice few-shot injection."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

import anthropic

from bot.config import get_settings
from pipeline.brand_voice import BrandProfile, FewShotExample, format_brand_context

logger = logging.getLogger(__name__)

CAPTION_SYSTEM_PROMPT = """You are a social media content creator for small businesses.
You write engaging, on-brand captions that drive engagement.

Rules:
- Match the brand's tone and voice exactly
- Include relevant hashtags (5-10 per post)
- Keep captions concise but compelling
- Include a clear call-to-action when appropriate
- Never use generic filler — every word should serve the brand
- Respect all DO/DON'T guidelines from the brand profile

Output JSON with exactly this structure:
{
  "captions": [
    {"text": "caption text with hashtags", "visual_prompt": "description for image generation"}
  ]
}

Generate exactly 3 caption options with corresponding visual prompts."""


@dataclass
class CaptionResult:
    """A generated caption with its visual prompt for image generation."""

    text: str
    visual_prompt: str


async def generate_captions(
    intent: str,
    profile: BrandProfile,
    examples: list[FewShotExample],
    platform_targets: list[str],
    num_options: int = 3,
    style: str | None = None,
) -> list[CaptionResult]:
    """Generate caption options using Claude API with brand voice context.

    Args:
        intent: What the user wants to post about.
        profile: Brand identity and voice rules.
        examples: Few-shot examples of real posts.
        platform_targets: Platforms this content will be posted to.
        num_options: Number of caption variants to generate.
        style: Optional image style to inject into visual prompts (e.g. "cinematic").

    Returns:
        List of CaptionResult with text and visual prompts.
    """
    brand_context = format_brand_context(profile, examples)
    platforms_str = ", ".join(platform_targets) if platform_targets else "all connected platforms"

    user_message = (
        f"{brand_context}\n\n"
        f"---\n\n"
        f"Create {num_options} social media post options for: {intent}\n"
        f"Target platforms: {platforms_str}\n"
        f"Each option should have a different angle or approach."
    )

    client = anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=CAPTION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        # Extract text content
        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content += block.text

        # Strip markdown fences if Claude wraps JSON in code blocks
        text_content = text_content.strip()
        if text_content.startswith("```"):
            text_content = text_content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        # Parse JSON response
        parsed = json.loads(text_content)
        captions = parsed.get("captions", [])

        results = []
        for cap in captions[:num_options]:
            visual_prompt = cap.get("visual_prompt", intent)
            if style:
                visual_prompt = f"[STYLE: {style}] {visual_prompt}"
            results.append(
                CaptionResult(
                    text=cap["text"],
                    visual_prompt=visual_prompt,
                )
            )

        logger.info(
            "Captions generated",
            extra={"count": len(results), "intent": intent[:50]},
        )
        return results

    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Failed to parse caption response", extra={"error": str(e)})
        raise
    except anthropic.APIError as e:
        logger.error("Anthropic API error", extra={"error": str(e)})
        raise


REVISE_SYSTEM_PROMPT = """You are a social media content creator for small businesses.
Your task is to revise an existing caption according to the user's instruction.

Rules:
- Preserve the brand's tone and voice exactly
- Apply only the requested change — don't rewrite everything if a small edit suffices
- Keep relevant hashtags unless the instruction says to remove them
- Respect all DO/DON'T guidelines from the brand profile
- Return ONLY the revised caption text — no JSON, no explanation, no markdown fences."""


async def revise_caption(
    current_caption: str,
    instruction: str,
    profile: BrandProfile,
    examples: list[FewShotExample],
) -> str:
    """Revise a caption using Claude based on a user instruction.

    Args:
        current_caption: The existing caption to be revised.
        instruction: What the user wants changed (e.g. "make it shorter").
        profile: Brand identity and voice rules.
        examples: Few-shot examples of real posts.

    Returns:
        The revised caption as a plain string.
    """
    brand_context = format_brand_context(profile, examples)

    user_message = (
        f"{brand_context}\n\n"
        f"---\n\n"
        f"Current caption:\n{current_caption}\n\n"
        f"Instruction: {instruction}\n\n"
        f"Return only the revised caption text, no JSON wrapper."
    )

    client = anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=REVISE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content += block.text

        result = text_content.strip()
        logger.info(
            "Caption revised",
            extra={"instruction": instruction[:50], "original_len": len(current_caption)},
        )
        return result

    except anthropic.APIError as e:
        logger.error("Anthropic API error during revision", extra={"error": str(e)})
        raise
