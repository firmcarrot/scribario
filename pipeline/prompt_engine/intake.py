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
Your job: decide if we have enough information to generate GREAT content.

Your goal is to ask ZERO questions — proceed whenever possible. But if the output
quality would genuinely suffer without more info, ask. Quality is the priority.

Rules:
- If the intent references something visual the user hasn't provided (their product,
  their logo, their face) AND there are NO reference photos on file → ask_for_asset.
  Phrase it as a friendly question asking for the specific photo.
- If BOTH vagueness AND missing photos apply → prioritize ask_for_asset.
  Asking for the photo implicitly clarifies what the content is about.
- If the intent is too vague to produce quality content → ask_for_clarity.
  Ask ONE clear question that gets you the most information per question.
- Otherwise → proceed. Most intents are workable with the brand profile context.

Philosophy on questions:
- Ask as FEW as possible, as MANY as necessary.
- Never ask just to ask. Every question must directly improve output quality.
- If you can reasonably infer the answer from the brand profile or context, proceed.
- But if a user gives you almost nothing to work with, don't guess — ask.
  People sometimes need help articulating what they want.
- One well-crafted question is better than three vague ones.

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
