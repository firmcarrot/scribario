"""Caption generation — Claude API with brand voice few-shot injection."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

import anthropic

from bot.config import settings
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
) -> list[CaptionResult]:
    """Generate caption options using Claude API with brand voice context.

    Args:
        intent: What the user wants to post about.
        profile: Brand identity and voice rules.
        examples: Few-shot examples of real posts.
        platform_targets: Platforms this content will be posted to.
        num_options: Number of caption variants to generate.

    Returns:
        List of CaptionResult with text and visual prompts.
    """
    brand_context = format_brand_context(profile, examples)
    platforms_str = ", ".join(platform_targets)

    user_message = (
        f"{brand_context}\n\n"
        f"---\n\n"
        f"Create {num_options} social media post options for: {intent}\n"
        f"Target platforms: {platforms_str}\n"
        f"Each option should have a different angle or approach."
    )

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

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

        # Parse JSON response
        parsed = json.loads(text_content)
        captions = parsed.get("captions", [])

        results = []
        for cap in captions[:num_options]:
            results.append(
                CaptionResult(
                    text=cap["text"],
                    visual_prompt=cap.get("visual_prompt", intent),
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
