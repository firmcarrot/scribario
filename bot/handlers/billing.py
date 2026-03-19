"""Billing commands — /subscribe, /billing, /upgrade."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import get_settings
from bot.db import get_supabase_client, get_tenant_by_telegram_user

logger = logging.getLogger(__name__)

router = Router(name="billing")

# Plan tier details
PLANS = {
    "starter": {
        "name": "Starter",
        "price": "$29/mo",
        "posts": 15,
        "videos": "3 short",
        "features": ["15 posts/month", "3 short videos", "All platforms", "Brand voice AI"],
    },
    "growth": {
        "name": "Growth",
        "price": "$59/mo",
        "posts": 40,
        "videos": "10 short + 2 long",
        "features": ["40 posts/month", "10 short + 2 long videos", "Priority support", "Autopilot mode"],
    },
    "pro": {
        "name": "Pro",
        "price": "$99/mo",
        "posts": 100,
        "videos": "25 short + 5 long",
        "features": ["100 posts/month", "25 short + 5 long videos", "Dedicated support", "Custom integrations"],
    },
}


def _build_plan_comparison() -> str:
    """Build a formatted plan comparison string."""
    lines = ["<b>Choose your plan:</b>\n"]
    for tier, info in PLANS.items():
        lines.append(f"<b>{info['name']} — {info['price']}</b>")
        for feat in info["features"]:
            lines.append(f"  • {feat}")
        lines.append("")
    return "\n".join(lines)


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message) -> None:
    """Show plan comparison and subscription options."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer("Use /start to set up your account first.")
        return

    settings = get_settings()
    if not settings.stripe_api_key:
        await message.answer(
            _build_plan_comparison()
            + "\nSubscriptions are being set up. Check back soon!"
        )
        return

    # Build Stripe Checkout buttons
    buttons = []
    price_ids = {
        "starter": settings.stripe_starter_price_id,
        "growth": settings.stripe_growth_price_id,
        "pro": settings.stripe_pro_price_id,
    }

    for tier, price_id in price_ids.items():
        if price_id:
            buttons.append([
                InlineKeyboardButton(
                    text=f"{PLANS[tier]['name']} — {PLANS[tier]['price']}",
                    callback_data=f"subscribe:{tier}",
                )
            ])

    text = _build_plan_comparison()

    if buttons:
        text += "Tap a plan to subscribe:"
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(text, reply_markup=markup)
    else:
        text += "\nSubscriptions are being set up. Check back soon!"
        await message.answer(text)


@router.message(Command("billing"))
async def cmd_billing(message: Message) -> None:
    """Show current plan, usage, and billing portal link."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer("Use /start to set up your account first.")
        return

    tenant_id = membership["tenant_id"]
    client = get_supabase_client()
    result = client.table("tenants").select(
        "plan_tier, subscription_status, monthly_posts_used, monthly_post_limit, "
        "video_credits_remaining, trial_posts_used, trial_posts_limit"
    ).eq("id", tenant_id).single().execute()

    tenant = result.data
    if not tenant:
        await message.answer("Account data not found.")
        return

    plan = tenant["plan_tier"]
    status = tenant["subscription_status"]

    if plan == "free_trial":
        used = tenant["trial_posts_used"] or 0
        limit = tenant["trial_posts_limit"] or 5
        text = (
            f"<b>Plan:</b> Free Trial\n"
            f"<b>Posts used:</b> {used}/{limit}\n\n"
            "Ready to upgrade? Use /subscribe"
        )
    else:
        plan_info = PLANS.get(plan, {})
        used = tenant["monthly_posts_used"] or 0
        limit = tenant["monthly_post_limit"] or 0
        videos = tenant["video_credits_remaining"] or 0
        text = (
            f"<b>Plan:</b> {plan_info.get('name', plan.title())} ({status})\n"
            f"<b>Posts this month:</b> {used}/{limit}\n"
            f"<b>Video credits:</b> {videos}\n\n"
            "Manage subscription: /upgrade"
        )

    await message.answer(text)


@router.message(Command("upgrade"))
async def cmd_upgrade(message: Message) -> None:
    """Direct to plan upgrade options."""
    await cmd_subscribe(message)
