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

YOUR DEFAULT ANSWER IS ALWAYS "proceed". You should ALMOST NEVER ask questions.

The user is a busy business owner texting a bot from their phone. They do NOT want
to answer questions — they want their post made. Respect their time.

ONLY return ask_for_clarity if the message is completely unusable — like a single
word with zero context (e.g., just "post" or "hello"). Even short requests like
"post about our sale" or "new product drop" are perfectly fine to proceed with.

NEVER ask_for_asset. We generate images with AI — we don't need the user's photos.

When in doubt: proceed. Always proceed. The user can edit later if they don't like it.

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
                "enum": ["proceed", "ask_for_clarity"],
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
