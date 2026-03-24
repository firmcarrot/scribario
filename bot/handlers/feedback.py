"""Feedback and support ticket handlers — /feedback, /ticket."""

from __future__ import annotations

import html
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import get_settings
from bot.db import (
    create_support_ticket,
    get_support_ticket_by_number,
    get_tenant_by_telegram_user,
    get_user_tickets,
)
from bot.dialogs.states import FeedbackSG

router = Router(name="feedback")
logger = logging.getLogger(__name__)


# --- /feedback command ---


@router.message(Command("feedback"))
async def handle_feedback(message: Message) -> None:
    """Show category selection keyboard."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer("You're not set up yet! Use /start first.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="\U0001f41b Bug", callback_data="feedback_cat:bug"),
            InlineKeyboardButton(text="\U0001f4a1 Idea", callback_data="feedback_cat:idea"),
        ]
    ])
    await message.answer(
        "What would you like to report?",
        reply_markup=keyboard,
    )


# --- Category callback ---


@router.callback_query(F.data.startswith("feedback_cat:"))
async def handle_feedback_category(callback: CallbackQuery, state: FSMContext) -> None:
    """Store category and enter description state."""
    user = callback.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await callback.answer("You're not set up yet!", show_alert=True)
        return

    category = callback.data.split(":", 1)[1]  # "bug" or "idea"
    tenant_data = membership.get("tenants") or {}
    business_name = tenant_data.get("name", "Unknown") if isinstance(tenant_data, dict) else "Unknown"

    await state.update_data(
        category=category,
        tenant_id=membership["tenant_id"],
        chat_id=callback.message.chat.id,
        business_name=business_name,
    )
    await state.set_state(FeedbackSG.waiting_for_description)

    label = "\U0001f41b Bug" if category == "bug" else "\U0001f4a1 Idea"
    await callback.message.answer(
        f"Got it — <b>{label}</b>.\n\n"
        "Describe it in a message. Type /cancel to abort.",
        parse_mode="HTML",
    )
    await callback.answer()


# --- /cancel in description state ---


@router.message(Command("cancel"), FeedbackSG.waiting_for_description)
async def handle_feedback_cancel(message: Message, state: FSMContext) -> None:
    """Cancel feedback submission."""
    await state.clear()
    await message.answer("Feedback cancelled.")


# --- Description handler ---


@router.message(FeedbackSG.waiting_for_description, F.text)
async def handle_feedback_description(message: Message, state: FSMContext) -> None:
    """Create the support ticket from the user's description."""
    description = (message.text or "").strip()
    if not description:
        await message.answer("Please describe the issue — can't submit an empty ticket.")
        return

    # Truncate very long descriptions to stay safe with Telegram message limits
    max_desc_len = 2000
    if len(description) > max_desc_len:
        description = description[:max_desc_len] + "..."

    data = await state.get_data()
    category = data.get("category", "bug")
    tenant_id = data.get("tenant_id", "")
    chat_id = data.get("chat_id", message.chat.id)
    business_name = data.get("business_name", "Unknown")

    try:
        ticket = await create_support_ticket(
            tenant_id=tenant_id,
            category=category,
            description=description,
            creator_telegram_user_id=message.from_user.id,
            creator_telegram_chat_id=chat_id,
        )
    except Exception:
        logger.exception("Failed to create support ticket")
        await message.answer("Something went wrong creating your ticket. Please try again.")
        return

    ticket_number = ticket["ticket_number"]
    await state.clear()

    await message.answer(
        f"\U0001f3ab Ticket <b>{ticket_number}</b> created! We'll get back to you.",
        parse_mode="HTML",
    )

    # Send admin alert (plain text to avoid HTML injection from user input)
    settings = get_settings()
    cat_icon = "\U0001f41b Bug" if category == "bug" else "\U0001f4a1 Idea"
    username = f"@{message.from_user.username}" if message.from_user.username else "no username"
    admin_text = (
        f"\U0001f3ab New Ticket: {ticket_number}\n"
        f"Category: {cat_icon}\n"
        f"From: {username} ({business_name})\n\n"
        f"{description}"
    )
    try:
        await message.bot.send_message(
            chat_id=settings.admin_telegram_user_id,
            text=admin_text,
            parse_mode=None,
        )
    except Exception:
        logger.exception("Failed to send admin alert for ticket %s", ticket_number)


# --- /ticket command ---


@router.message(Command("ticket"))
async def handle_ticket(message: Message) -> None:
    """Look up a ticket by number, or list recent tickets."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer("You're not set up yet! Use /start first.")
        return

    tenant_id = membership["tenant_id"]
    parts = (message.text or "").split(maxsplit=1)

    # No argument → list recent tickets
    if len(parts) < 2 or not parts[1].strip():
        tickets = await get_user_tickets(user.id, limit=5, tenant_id=tenant_id)
        if not tickets:
            await message.answer("You don't have any tickets yet. Use /feedback to create one.")
            return

        lines: list[str] = ["\U0001f3ab <b>Your Tickets</b>\n"]
        status_icons = {"open": "\U0001f7e1", "in_progress": "\U0001f535", "resolved": "\u2705"}
        for t in tickets:
            icon = status_icons.get(t.get("status", ""), "\u2753")
            cat_icon = "\U0001f41b" if t.get("category") == "bug" else "\U0001f4a1"
            raw_desc = t.get("description", "")
            desc_preview = html.escape(raw_desc[:50])
            if len(raw_desc) > 50:
                desc_preview += "..."
            lines.append(
                f"{icon} <b>{t['ticket_number']}</b> {cat_icon} {t.get('status', 'open')}\n"
                f"   {desc_preview}"
            )
            lines.append("")

        await message.answer("\n".join(lines).strip(), parse_mode="HTML")
        return

    # Argument provided → look up specific ticket
    ticket_number = parts[1].strip().upper()
    ticket = await get_support_ticket_by_number(ticket_number, tenant_id=tenant_id)

    if not ticket:
        await message.answer(f"Couldn't find ticket <b>{ticket_number}</b>.", parse_mode="HTML")
        return

    status_icons = {"open": "\U0001f7e1 Open", "in_progress": "\U0001f535 In Progress", "resolved": "\u2705 Resolved"}
    cat_icon = "\U0001f41b Bug" if ticket.get("category") == "bug" else "\U0001f4a1 Idea"
    status_text = status_icons.get(ticket.get("status", ""), ticket.get("status", "unknown"))

    desc_escaped = html.escape(ticket.get("description", ""))
    text = (
        f"\U0001f3ab <b>{ticket['ticket_number']}</b>\n"
        f"Category: {cat_icon}\n"
        f"Status: {status_text}\n\n"
        f"{desc_escaped}"
    )
    if ticket.get("admin_response"):
        text += f"\n\n<b>Response:</b>\n{html.escape(ticket['admin_response'])}"

    await message.answer(text, parse_mode="HTML")
