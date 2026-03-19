"""Brand profile editing — inline edit flow via FSM."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.db import get_supabase_client, get_tenant_by_telegram_user
from bot.dialogs.states import BrandEditSG

logger = logging.getLogger(__name__)

router = Router(name="brand_edit")

# Maps edit field keys to DB columns and user-friendly prompts
FIELD_CONFIG = {
    "name": {
        "column": "brand_name",
        "prompt": "What's your brand name?",
        "parse": "text",
    },
    "tone": {
        "column": "tone",
        "prompt": (
            "What tone should your brand use?\n\n"
            "Send a comma-separated list, e.g.:\n"
            "<i>bold, witty, warm</i>"
        ),
        "parse": "list",
    },
    "audience": {
        "column": "target_audience",
        "prompt": (
            "Who is your target audience?\n\n"
            "Example: <i>Millennials and Gen Z foodies in Miami "
            "who love bold flavors and fun dining experiences</i>"
        ),
        "parse": "text",
    },
    "dos": {
        "column": "dos",
        "prompt": (
            "What should your content <b>always</b> do?\n\n"
            "Send one item per line, e.g.:\n"
            "<i>Mention our website\n"
            "Use a casual, friendly tone\n"
            "Include a call to action</i>"
        ),
        "parse": "lines",
    },
    "donts": {
        "column": "donts",
        "prompt": (
            "What should your content <b>never</b> do?\n\n"
            "Send one item per line, e.g.:\n"
            "<i>Don't use corporate jargon\n"
            "Never mention competitors\n"
            "Avoid exclamation marks</i>"
        ),
        "parse": "lines",
    },
}


@router.callback_query(F.data.startswith("brand_edit:"))
async def on_brand_edit(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle tap on an edit button — prompt user for new value."""
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Invalid action.")
        return

    field_key = parts[1]
    tenant_id = parts[2]

    if field_key not in FIELD_CONFIG:
        await callback.answer("Unknown field.")
        return

    config = FIELD_CONFIG[field_key]

    # Store context for when user replies
    await state.set_state(BrandEditSG.waiting_for_value)
    await state.update_data(
        brand_edit_field=field_key,
        brand_edit_tenant_id=tenant_id,
    )

    await callback.message.answer(config["prompt"], parse_mode="HTML")
    await callback.answer()


@router.message(BrandEditSG.waiting_for_value)
async def on_brand_edit_value(message: Message, state: FSMContext) -> None:
    """Receive the new value and update the brand profile."""
    data = await state.get_data()
    field_key = data.get("brand_edit_field")
    tenant_id = data.get("brand_edit_tenant_id")

    if not field_key or not tenant_id:
        await state.clear()
        await message.answer("Something went wrong. Try /brand again.")
        return

    # Verify user owns this tenant
    user = message.from_user
    if not user:
        await state.clear()
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership or membership["tenant_id"] != tenant_id:
        await state.clear()
        await message.answer("You don't have access to this brand.")
        return

    config = FIELD_CONFIG[field_key]
    raw_text = (message.text or "").strip()

    if not raw_text:
        await message.answer("Please send a text value. Try again or use /brand to cancel.")
        return

    # Parse based on field type
    if config["parse"] == "list":
        value = [w.strip() for w in raw_text.split(",") if w.strip()]
    elif config["parse"] == "lines":
        value = [line.strip() for line in raw_text.splitlines() if line.strip()]
    else:
        value = raw_text

    # Update in DB
    try:
        client = get_supabase_client()
        client.table("brand_profiles").update(
            {config["column"]: value}
        ).eq("tenant_id", tenant_id).execute()
    except Exception:
        logger.exception("Failed to update brand profile field %s", field_key)
        await state.clear()
        await message.answer("Something went wrong. Please try again.")
        return

    await state.clear()

    # Show confirmation with the updated value
    if isinstance(value, list):
        display = ", ".join(value)
    else:
        display = value

    field_label = {
        "name": "Brand name",
        "tone": "Tone",
        "audience": "Target audience",
        "dos": "Always do",
        "donts": "Never do",
    }.get(field_key, field_key)

    await message.answer(
        f"✅ <b>{field_label}</b> updated to:\n{display}\n\n"
        "Use /brand to see your full profile or edit more fields.",
        parse_mode="HTML",
    )
