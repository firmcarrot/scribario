"""Autopilot Telegram command handler — /autopilot, /pause, /resume.

Uses simple FSM states (not aiogram_dialog per DA MED-4) for the setup flow.
"""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.db import (
    get_autopilot_config,
    get_tenant_by_telegram_user,
    get_tenant_monthly_cost,
    pause_autopilot,
    resume_autopilot,
    upsert_autopilot_config,
    count_tenant_posts_today,
    count_tenant_posts_this_week,
    advance_next_run_at,
)
from pipeline.schedule_parser import parse_schedule

logger = logging.getLogger(__name__)

router = Router(name="autopilot")


class AutopilotSetup(StatesGroup):
    """FSM states for autopilot setup flow."""
    choosing_mode = State()
    setting_schedule = State()
    choosing_platforms = State()


# --- Commands ---


@router.message(Command("autopilot"))
async def handle_autopilot_command(message: Message) -> None:
    """Show autopilot status or setup prompt."""
    if not message.from_user:
        return

    membership = await get_tenant_by_telegram_user(message.from_user.id)
    if not membership:
        await message.answer("You need to set up your account first. Use /start.")
        return

    tenant_id = membership["tenant_id"]
    config = await get_autopilot_config(tenant_id)

    if not config or config.get("mode") == "off":
        kb = InlineKeyboardBuilder()
        kb.button(text="Set Up Autopilot", callback_data="autopilot:setup")
        await message.answer(
            "🤖 <b>Autopilot is not configured yet.</b>\n\n"
            "Let me generate and post content for you automatically!",
            reply_markup=kb.as_markup(),
        )
        return

    # Show status
    mode = config["mode"].replace("_", " ").title()
    schedule = config.get("schedule_description", "Not set")
    is_paused = config.get("paused_at") is not None
    status_emoji = "⏸️ Paused" if is_paused else "✅ Active"

    daily = await count_tenant_posts_today(tenant_id)
    weekly = await count_tenant_posts_this_week(tenant_id)
    monthly_cost = await get_tenant_monthly_cost(tenant_id)
    cost_cap = config.get("monthly_cost_cap_usd", 50.0)
    next_run = config.get("next_run_at", "Not scheduled")

    text = (
        f"📊 <b>Autopilot Status</b>\n"
        f"Mode: {mode}\n"
        f"Schedule: {schedule}\n"
        f"Status: {status_emoji}\n\n"
        f"Today: {daily}/{config.get('daily_post_limit', 3)} posts\n"
        f"This week: {weekly}/{config.get('weekly_post_limit', 15)} posts\n"
        f"This month: ${monthly_cost:.2f} (cap: ${cost_cap:.2f})\n"
        f"Next post: {next_run}\n"
    )

    warmup = config.get("warmup_posts_remaining", 0)
    if warmup > 0:
        text += f"\n🔰 Warmup: {warmup} posts remaining (Smart Queue mode)\n"

    kb = InlineKeyboardBuilder()
    kb.button(text="Change Schedule", callback_data="autopilot:change_schedule")
    kb.button(text="Change Mode", callback_data="autopilot:setup")
    if is_paused:
        kb.button(text="▶️ Resume", callback_data="autopilot:resume")
    else:
        kb.button(text="⏸️ Pause", callback_data="autopilot:pause_confirm")
    kb.button(text="🔴 Turn Off", callback_data="autopilot:off")
    kb.adjust(2)

    await message.answer(text, reply_markup=kb.as_markup())


@router.message(Command("pause"))
async def handle_pause(message: Message) -> None:
    """Immediately pause autopilot."""
    if not message.from_user:
        return

    membership = await get_tenant_by_telegram_user(message.from_user.id)
    if not membership:
        await message.answer("You need to set up your account first.")
        return

    await pause_autopilot(membership["tenant_id"])
    await message.answer(
        "⏸️ <b>Autopilot paused.</b> No more posts will be generated.\n"
        "Use /resume when you're ready to restart."
    )


@router.message(Command("resume"))
async def handle_resume(message: Message) -> None:
    """Resume paused autopilot."""
    if not message.from_user:
        return

    membership = await get_tenant_by_telegram_user(message.from_user.id)
    if not membership:
        await message.answer("You need to set up your account first.")
        return

    tenant_id = membership["tenant_id"]
    config = await get_autopilot_config(tenant_id)
    if not config or config.get("mode") == "off":
        await message.answer("Autopilot is not configured. Use /autopilot to set it up.")
        return

    await resume_autopilot(tenant_id)
    await advance_next_run_at(tenant_id)
    await message.answer(
        "▶️ <b>Autopilot resumed!</b> Content generation will restart on schedule."
    )


# --- Setup flow callbacks ---


@router.callback_query(F.data == "autopilot:setup")
async def handle_setup_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Start setup: choose mode."""
    kb = InlineKeyboardBuilder()
    kb.button(text="Smart Queue (recommended)", callback_data="autopilot:mode:smart_queue")
    kb.button(text="Full Autopilot", callback_data="autopilot:mode:full_autopilot")
    kb.adjust(1)

    await state.set_state(AutopilotSetup.choosing_mode)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "Choose your autopilot mode:\n\n"
            "<b>Smart Queue:</b> I'll generate posts and show you a preview. "
            "If you don't reject within 2 hours, I'll post automatically.\n\n"
            "<b>Full Autopilot:</b> I generate and post automatically — "
            "you just get a notification after posting.",
            reply_markup=kb.as_markup(),
        )


@router.callback_query(F.data.startswith("autopilot:mode:"))
async def handle_setup_mode(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle mode selection → ask for schedule."""
    if not callback.data:
        return

    mode = callback.data.split(":")[-1]
    await state.update_data(mode=mode)
    await state.set_state(AutopilotSetup.setting_schedule)

    mode_desc = "Smart Queue" if mode == "smart_queue" else "Full Autopilot"
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            f"<b>{mode_desc}</b> selected!\n\n"
            "How often should I post? Examples:\n"
            "• daily at 10am\n"
            "• Mon/Wed/Fri at 10am\n"
            "• weekdays at 9am\n"
            "• every other day at 3pm\n\n"
            "Type your schedule:",
        )


@router.message(AutopilotSetup.setting_schedule)
async def handle_setup_schedule(message: Message, state: FSMContext) -> None:
    """Parse schedule text and ask for platform selection."""
    if not message.text or not message.from_user:
        return

    membership = await get_tenant_by_telegram_user(message.from_user.id)
    if not membership:
        await message.answer("Account not found.")
        return

    data = await state.get_data()
    tenant_data = membership.get("tenants") or {}
    timezone = tenant_data.get("timezone", "UTC") if isinstance(tenant_data, dict) else "UTC"

    cron, desc, error = parse_schedule(message.text, timezone=timezone)
    if error:
        await message.answer(f"❌ {error}\n\nPlease try again:")
        return

    await state.update_data(schedule_cron=cron, schedule_description=desc, timezone=timezone)
    await state.set_state(AutopilotSetup.choosing_platforms)

    kb = InlineKeyboardBuilder()
    kb.button(text="All Connected", callback_data="autopilot:platforms:all")
    kb.button(text="Facebook Only", callback_data="autopilot:platforms:facebook")
    kb.button(text="Instagram Only", callback_data="autopilot:platforms:instagram")
    kb.adjust(1)

    await message.answer(
        f"Got it! Schedule: <b>{desc}</b>\n\n"
        "Which platforms?",
        reply_markup=kb.as_markup(),
    )


@router.callback_query(F.data.startswith("autopilot:platforms:"))
async def handle_setup_platforms(callback: CallbackQuery, state: FSMContext) -> None:
    """Final setup step: save config and activate."""
    if not callback.data or not callback.from_user:
        return

    platform_choice = callback.data.split(":")[-1]
    platforms: list[str] = []
    if platform_choice != "all":
        platforms = [platform_choice]

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Account not found.")
        return

    tenant_id = membership["tenant_id"]
    data = await state.get_data()

    await upsert_autopilot_config(
        tenant_id,
        mode=data["mode"],
        schedule_cron=data["schedule_cron"],
        schedule_description=data["schedule_description"],
        timezone=data.get("timezone", "UTC"),
        platform_targets=platforms,
    )

    # Set initial next_run_at
    await advance_next_run_at(tenant_id)

    await state.clear()

    mode_label = "Smart Queue (2hr review window)" if data["mode"] == "smart_queue" else "Full Autopilot"
    platform_label = platform_choice.title() if platform_choice != "all" else "All connected"

    await callback.answer("Autopilot activated!")
    if callback.message:
        await callback.message.edit_text(
            "✅ <b>Autopilot activated!</b>\n\n"
            f"Mode: {mode_label}\n"
            f"Schedule: {data['schedule_description']}\n"
            f"Platforms: {platform_label}\n"
            f"Daily limit: 3 posts\n\n"
            "🔰 Your first 5 posts will always use Smart Queue for safety.\n"
            "Use /pause anytime to stop.",
        )


# --- Inline button actions ---


@router.callback_query(F.data == "autopilot:pause_confirm")
async def handle_pause_button(callback: CallbackQuery) -> None:
    """Pause autopilot via inline button."""
    if not callback.from_user:
        return

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Account not found.")
        return

    await pause_autopilot(membership["tenant_id"])
    await callback.answer("Paused!")
    if callback.message:
        await callback.message.edit_text(
            "⏸️ <b>Autopilot paused.</b> No more posts will be generated.\n"
            "Use /resume when you're ready to restart."
        )


@router.callback_query(F.data == "autopilot:resume")
async def handle_resume_button(callback: CallbackQuery) -> None:
    """Resume autopilot via inline button."""
    if not callback.from_user:
        return

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Account not found.")
        return

    tenant_id = membership["tenant_id"]
    await resume_autopilot(tenant_id)
    await advance_next_run_at(tenant_id)
    await callback.answer("Resumed!")
    if callback.message:
        await callback.message.edit_text(
            "▶️ <b>Autopilot resumed!</b> Content generation will restart on schedule."
        )


@router.callback_query(F.data == "autopilot:off")
async def handle_turn_off(callback: CallbackQuery) -> None:
    """Turn off autopilot completely."""
    if not callback.from_user:
        return

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Account not found.")
        return

    await upsert_autopilot_config(membership["tenant_id"], mode="off")
    await callback.answer("Turned off.")
    if callback.message:
        await callback.message.edit_text(
            "🔴 <b>Autopilot turned off.</b>\n"
            "Use /autopilot to set it up again anytime."
        )


@router.callback_query(F.data == "autopilot:change_schedule")
async def handle_change_schedule(callback: CallbackQuery, state: FSMContext) -> None:
    """Start schedule change flow — preserves existing mode in FSM state."""
    if not callback.from_user:
        return

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Account not found.")
        return

    config = await get_autopilot_config(membership["tenant_id"])
    current_mode = config.get("mode", "smart_queue") if config else "smart_queue"

    await state.update_data(mode=current_mode)
    await state.set_state(AutopilotSetup.setting_schedule)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "Type your new schedule:\n\n"
            "Examples:\n"
            "• daily at 10am\n"
            "• Mon/Wed/Fri at 10am\n"
            "• weekdays at 9am",
        )
