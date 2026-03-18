from __future__ import annotations

import asyncio
import json
import logging

import anthropic

from bot.config import get_settings

logger = logging.getLogger(__name__)

EDIT_ANALYSIS_COST_USD = 0.001  # ~$0.001 per Haiku call


async def analyze_edit(
    tenant_id: str,
    original_caption: str,
    edit_instruction: str,
    edited_caption: str,
) -> None:
    """Analyze an edit triple with Haiku and store the learned pattern.

    Called as fire-and-forget -- never blocks the user's flow.
    """
    try:
        client = anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)

        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f'Original: "{original_caption}"\n'
                        f'User instruction: "{edit_instruction}"\n'
                        f'Result: "{edited_caption}"\n\n'
                        "Extract ONE concrete structural change. Examples:\n"
                        '- "shortened from 120 words to 45 words"\n'
                        '- "removed all exclamation marks"\n'
                        '- "changed formal tone to casual"\n'
                        '- "removed emoji"\n'
                        "- \"changed CTA from 'click link' to 'comment below'\"\n\n"
                        'Return JSON: {"feature": "...", "value": "...", "lesson": "..."}\n'
                        "feature = category (word_count, tone, punctuation, emoji, cta, etc.)\n"
                        "value = the direction of change (shorter, casual, no_exclamation, etc.)\n"
                        "lesson = one-sentence instruction for future captions"
                    ),
                }
            ],
        )

        # Parse the JSON from Haiku's response
        text = response.content[0].text.strip()
        # Handle markdown code blocks
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        result = json.loads(text)
        feature = result.get("feature", "unknown")
        value = result.get("value", "unknown")
        lesson = result.get("lesson")

        # Log usage
        from bot.db import log_usage_event

        await log_usage_event(
            tenant_id=tenant_id,
            event_type="edit_analysis",
            provider="anthropic",
            cost_usd=EDIT_ANALYSIS_COST_USD,
        )

        # Store the signal
        from pipeline.learning.preference_engine import accumulate_edit_signal

        await accumulate_edit_signal(
            tenant_id=tenant_id,
            feature=feature,
            value=value,
            lesson_text=lesson,
        )

    except Exception:
        logger.exception("Edit analysis failed -- non-fatal", extra={"tenant_id": tenant_id})


def fire_and_forget_edit_analysis(
    tenant_id: str,
    original_caption: str,
    edit_instruction: str,
    edited_caption: str,
) -> None:
    """Schedule edit analysis as a background task. Never blocks."""
    try:
        loop = asyncio.get_running_loop()
        task = loop.create_task(
            analyze_edit(tenant_id, original_caption, edit_instruction, edited_caption)
        )
        task.add_done_callback(lambda t: t.exception() if not t.cancelled() else None)
    except RuntimeError:
        logger.warning("No running event loop -- skipping edit analysis")
