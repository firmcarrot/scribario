"""Script generation — Claude API generates multi-scene video scripts."""

from __future__ import annotations

import json
import logging

import anthropic

from bot.config import get_settings
from pipeline.brand_voice import BrandProfile, format_brand_context
from pipeline.long_video.models import LongVideoScript, Scene, SceneType

logger = logging.getLogger(__name__)

SCRIPT_GEN_COST_USD = 0.03

NO_AUDIO_SUFFIX = " No music, no sound effects, no dialogue."

SCRIPT_SYSTEM_PROMPT = """You are a video scriptwriter for short-form social media content.

Your job is to generate a multi-scene video script in JSON format.

Rules:
- Generate exactly 4 scenes for a 30-second video (~7-8 seconds of voiceover per scene)
- Alternate a_roll / b_roll scene types for visual variety (scene 0: a_roll, scene 1: b_roll, etc.)
- Write frame-pair prompts (start_frame_prompt + end_frame_prompt) that create natural animation paths
- Keep voiceover text punchy: 10-25 words per scene
- Include camera_direction for each scene (e.g. "slow dolly push-in", "overhead crane down")
- Include sfx_description for transition/ambient sounds per scene
- visual_description is a brief summary of the scene's visual content
- start_frame_prompt and end_frame_prompt should be detailed, cinematic image prompts

Output valid JSON matching this exact schema:
{
  "title": "Video Title",
  "voice_style": "description of narrator voice style",
  "scenes": [
    {
      "index": 0,
      "scene_type": "a_roll",
      "voiceover_text": "Narration text for this scene.",
      "visual_description": "Brief visual summary",
      "start_frame_prompt": "Detailed cinematic prompt for the opening frame",
      "end_frame_prompt": "Detailed cinematic prompt for the closing frame",
      "camera_direction": "camera movement description",
      "sfx_description": "sound effect description"
    }
  ]
}

Output ONLY the JSON. No markdown fences, no explanation."""


async def generate_script(
    intent: str,
    profile: BrandProfile,
) -> LongVideoScript:
    """Generate a multi-scene video script using Claude API.

    Args:
        intent: What the user wants the video to be about.
        profile: Brand identity and voice rules.

    Returns:
        LongVideoScript with Scene objects.

    Raises:
        json.JSONDecodeError: If Claude returns unparseable JSON.
        KeyError: If required fields are missing from the response.
        anthropic.APIError: If the Claude API call fails.
    """
    brand_context = format_brand_context(profile, [])

    user_message = (
        f"{brand_context}\n\n"
        f"---\n\n"
        f"Create a 30-second video script for: {intent}\n"
        f"Generate exactly 4 scenes alternating a_roll and b_roll."
    )

    client = anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SCRIPT_SYSTEM_PROMPT,
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

        # Build Scene objects
        raw_scenes = parsed["scenes"]
        scenes = []
        for s in raw_scenes:
            start_prompt = s["start_frame_prompt"]
            end_prompt = s["end_frame_prompt"]

            # Append no-audio suffix to visual prompts
            if not start_prompt.endswith(NO_AUDIO_SUFFIX.strip()):
                start_prompt = start_prompt + NO_AUDIO_SUFFIX
            if not end_prompt.endswith(NO_AUDIO_SUFFIX.strip()):
                end_prompt = end_prompt + NO_AUDIO_SUFFIX

            scenes.append(
                Scene(
                    index=s["index"],
                    scene_type=SceneType(s["scene_type"]),
                    voiceover_text=s["voiceover_text"],
                    visual_description=s["visual_description"],
                    start_frame_prompt=start_prompt,
                    end_frame_prompt=end_prompt,
                    camera_direction=s["camera_direction"],
                    sfx_description=s["sfx_description"],
                )
            )

        script = LongVideoScript(
            title=parsed["title"],
            voice_style=parsed["voice_style"],
            scenes=scenes,
        )

        logger.info(
            "Script generated",
            extra={
                "title": script.title,
                "total_scenes": script.total_scenes,
                "intent": intent[:50],
            },
        )
        return script

    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Failed to parse script response", extra={"error": str(e)})
        raise
    except anthropic.APIError as e:
        logger.error("Anthropic API error", extra={"error": str(e)})
        raise
