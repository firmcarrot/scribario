"""Intake handler — processes free-text content requests."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import Message

from bot.db import create_content_request, enqueue_job, get_tenant_by_telegram_user

logger = logging.getLogger(__name__)

router = Router(name="intake")


@router.message(F.text)
async def handle_content_request(message: Message) -> None:
    """Handle free-text messages as content creation requests.

    Flow: user message → look up tenant → create content_request → enqueue generation → ack.
    """
    user = message.from_user
    if not user or not message.text:
        return

    intent = message.text.strip()

    # Look up tenant for this Telegram user
    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer(
            "You're not connected to any brand yet.\n"
            "Use /start to set up your account."
        )
        return

    tenant_id = membership["tenant_id"]

    logger.info(
        "Content request received",
        extra={"user_id": user.id, "tenant_id": tenant_id, "intent": intent[:100]},
    )

    # Create content request in database
    request = await create_content_request(
        tenant_id=tenant_id,
        intent=intent,
        platform_targets=["instagram", "facebook"],
    )
    request_id = request["id"]

    # Enqueue generation job
    await enqueue_job(
        queue_name="content_generation",
        job_type="generate_content",
        payload={
            "request_id": request_id,
            "tenant_id": tenant_id,
            "intent": intent,
            "platform_targets": ["instagram", "facebook"],
            "telegram_chat_id": message.chat.id,
        },
        idempotency_key=f"{request_id}:generate_content",
    )

    await message.answer(
        "Got it! I'm generating content for:\n\n"
        f"<i>{intent}</i>\n\n"
        "This usually takes about 30-60 seconds. I'll send you a preview with options to approve."
    )
