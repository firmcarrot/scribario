"""Intake handler — processes free-text content requests."""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.types import Message

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

router = Router(name="intake")


@router.message(F.text)
async def handle_content_request(message: Message) -> None:
    """Handle free-text messages as content creation requests.

    Flow: user message → create content_request in DB → enqueue generation job → ack to user.
    """
    user = message.from_user
    if not user or not message.text:
        return

    request_id = str(uuid.uuid4())
    intent = message.text.strip()

    logger.info(
        "Content request received",
        extra={"request_id": request_id, "user_id": user.id, "intent": intent[:100]},
    )

    # TODO: Look up tenant_id from telegram_user_id via tenant_members
    # TODO: Insert content_request row (status='pending')
    # TODO: Enqueue generation job to pgmq

    await message.answer(
        "Got it! I'm generating content for:\n\n"
        f"<i>{intent}</i>\n\n"
        "This usually takes about 30-60 seconds. I'll send you a preview with options to approve."
    )
