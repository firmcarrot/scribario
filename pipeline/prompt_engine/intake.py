"""Intake agent — checks if user intent needs clarification before generation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum

import anthropic

from bot.config import get_settings
from bot.db import count_reference_photos

logger = logging.getLogger(__name__)

INTAKE_COST_USD = 0.001  # Haiku per-call cost


class IntakeAction(StrEnum):
    PROCEED = "proceed"
    ASK_FOR_ASSET = "ask_for_asset"
    ASK_FOR_CLARITY = "ask_for_clarity"


@dataclass
class IntakeResult:
    action: IntakeAction
    message: str | None = None


_INTAKE_SYSTEM_PROMPT = """\
You are an intake classifier for a social media content generation bot.
Your job: decide if we have enough information to generate content, or if
we need ONE thing from the user first.

Rules:
- If the intent references something visual the user hasn't provided (their product,
  their logo, their face) AND there are NO reference photos on file → ask_for_asset.
  Phrase it as a single friendly question asking for the specific photo.
- If BOTH vagueness AND missing photos apply → prioritize ask_for_asset.
  Asking for the photo implicitly clarifies what the content is about.
- If the intent is completely ambiguous with zero useful context (just "make something"
  or a single word) AND there are no reference photos → ask_for_clarity.
- Otherwise → proceed. Most intents are workable. Don't interrogate.
- NEVER ask more than one question. Max 1 clarifying message.

Call the intake_decision tool with your decision."""

_INTAKE_TOOL = {
    "name": "intake_decision",
    "description": "Classify whether we can proceed with generation or need user input.",
    "input_schema": {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {
                "type": "string",
                "enum": ["proceed", "ask_for_asset", "ask_for_clarity"],
            },
            "message": {
                "type": "string",
                "description": (
                    "The single clarifying question to ask the user. "
                    "Required for ask_for_asset and ask_for_clarity. "
                    "Omit for proceed."
                ),
            },
        },
    },
}


async def check_intake(intent: str, tenant_id: str) -> IntakeResult:
    """Check if an intent needs clarification before generation.

    Uses Claude Haiku to classify the intent. Fails open — if anything goes
    wrong, returns PROCEED so the user isn't blocked.

    Args:
        intent: The user's content request text.
        tenant_id: Tenant to check photo inventory for.

    Returns:
        IntakeResult with action and optional clarifying message.
    """
    photo_count = await count_reference_photos(tenant_id)

    user_message = (
        f"User intent: {intent}\n"
        f"Reference photos on file: {photo_count}\n\n"
        f"Should we proceed, or ask the user for something first?"
    )

    try:
        client = anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=_INTAKE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            tools=[_INTAKE_TOOL],
            tool_choice={"type": "tool", "name": "intake_decision"},
        )

        # Extract tool_use block
        for block in response.content:
            if block.type == "tool_use" and block.name == "intake_decision":
                action_str = block.input.get("action", "proceed")
                try:
                    action = IntakeAction(action_str)
                except ValueError:
                    action = IntakeAction.PROCEED
                return IntakeResult(
                    action=action,
                    message=block.input.get("message"),
                )

        # No tool_use block — fail open
        logger.warning("Intake agent did not return tool_use, proceeding")
        return IntakeResult(action=IntakeAction.PROCEED)

    except Exception:
        logger.exception("Intake agent failed, proceeding by default")
        return IntakeResult(action=IntakeAction.PROCEED)
