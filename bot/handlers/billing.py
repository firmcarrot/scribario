"""Billing commands — /subscribe, /billing, /upgrade, /usage, /topoff."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.config import get_settings
from bot.db import get_supabase_client, get_tenant_by_telegram_user

logger = logging.getLogger(__name__)

router = Router(name="billing")

# Plan tier details
PLANS = {
    "starter": {
        "name": "Starter",
        "monthly": "$29/mo",
        "annual": "$278/yr (save 20%)",
        "posts": 15,
        "videos": 5,
        "features": ["15 posts/month", "5 short videos", "All platforms", "Brand voice AI"],
    },
    "growth": {
        "name": "Growth",
        "monthly": "$59/mo",
        "annual": "$566/yr (save 20%)",
        "posts": 40,
        "videos": 15,
        "features": [
            "40 posts/month", "15 short videos",
            "Priority support", "Autopilot mode",
        ],
    },
    "pro": {
        "name": "Pro",
        "monthly": "$99/mo",
        "annual": "$950/yr (save 20%)",
        "posts": 100,
        "videos": 40,
        "features": [
            "100 posts/month", "40 short videos",
            "Dedicated support", "Custom integrations",
        ],
    },
}

TOPOFFS = {
    "images": {"name": "+10 Image Posts", "price": "$5", "credits": 10},
    "short_videos": {"name": "+5 Short Videos", "price": "$12", "credits": 5},
    "long_video": {"name": "+1 Long Video", "price": "$6", "credits": 1},
}


def _build_plan_comparison() -> str:
    """Build a formatted plan comparison string."""
    lines = ["<b>Choose your plan:</b>\n"]
    for _tier, info in PLANS.items():
        lines.append(f"<b>{info['name']} — {info['monthly']}</b>")
        lines.append(f"  <i>or {info['annual']}</i>")
        for feat in info["features"]:
            lines.append(f"  • {feat}")
        lines.append("")
    lines.append(
        "<b>Free trial:</b> 5 posts + 1 video, no time limit\n"
        "<b>Cancel anytime</b> — use what you paid for, no refunds\n"
    )
    return "\n".join(lines)


def _progress_bar(used: int, limit: int, width: int = 10) -> str:
    """Build a visual progress bar."""
    if limit <= 0:
        return "▓" * width
    filled = min(int(used / limit * width), width)
    empty = width - filled
    pct = min(int(used / limit * 100), 100)
    return f"{'▓' * filled}{'░' * empty} {used}/{limit} ({pct}%)"


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

    # Build subscription buttons — monthly and annual for each tier
    buttons = []
    for tier, info in PLANS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{info['name']} — {info['monthly']}",
                callback_data=f"sub:{tier}:m",
            ),
            InlineKeyboardButton(
                text=f"Annual {info['annual'].split('(')[0].strip()}",
                callback_data=f"sub:{tier}:a",
            ),
        ])

    text = _build_plan_comparison() + "Tap a plan to subscribe:"
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("sub:"))
async def on_subscribe_callback(callback: CallbackQuery) -> None:
    """Handle subscribe:{tier}:{m|a} callback — create Stripe Checkout session."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer("Invalid selection.")
        return

    _, tier, interval = parts
    if tier not in PLANS:
        await callback.answer("Unknown plan.")
        return

    annual = interval == "a"

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Use /start first.")
        return

    tenant_id = membership["tenant_id"]
    chat_id = callback.message.chat.id

    try:
        from bot.services.stripe_service import create_checkout_session, get_price_id_for_tier

        price_id = get_price_id_for_tier(tier, annual=annual)
        if not price_id:
            await callback.answer("This plan isn't available yet.")
            return

        url = create_checkout_session(tenant_id, price_id, chat_id, is_annual=annual)
        plan_info = PLANS[tier]
        price_label = plan_info["annual"] if annual else plan_info["monthly"]

        await callback.message.answer(
            f"<b>Subscribe to {plan_info['name']} — {price_label}</b>\n\n"
            f"Tap the button below to complete your subscription:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Complete Payment", url=url)],
            ]),
        )
        await callback.answer()
    except Exception:
        logger.exception("Failed to create checkout session")
        await callback.answer("Something went wrong. Please try again.")


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
        "video_credits_remaining, trial_posts_used, trial_posts_limit, "
        "trial_videos_used, trial_video_limit, bonus_posts, bonus_videos, "
        "stripe_customer_id, current_period_end, canceled_at"
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
        vused = tenant.get("trial_videos_used") or 0
        vlimit = tenant.get("trial_video_limit") or 1
        text = (
            f"<b>Plan:</b> Free Trial\n"
            f"<b>Posts:</b> {_progress_bar(used, limit)}\n"
            f"<b>Videos:</b> {_progress_bar(vused, vlimit)}\n\n"
            "Ready to upgrade? Use /subscribe"
        )
    else:
        plan_info = PLANS.get(plan, {})
        used = tenant["monthly_posts_used"] or 0
        limit = tenant["monthly_post_limit"] or 0
        videos = tenant["video_credits_remaining"] or 0
        bonus_p = tenant.get("bonus_posts") or 0
        bonus_v = tenant.get("bonus_videos") or 0

        text = (
            f"<b>Plan:</b> {plan_info.get('name', plan.title())} ({status})\n"
            f"<b>Posts:</b> {_progress_bar(used, limit)}\n"
            f"<b>Video credits:</b> {videos}\n"
        )
        if bonus_p > 0:
            text += f"<b>Bonus posts:</b> {bonus_p}\n"
        if bonus_v > 0:
            text += f"<b>Bonus videos:</b> {bonus_v}\n"

        if tenant.get("current_period_end"):
            text += f"\n<b>Current period ends:</b> {tenant['current_period_end'][:10]}\n"

        if tenant.get("canceled_at") and status == "active":
            text += "\n<i>Your subscription will cancel at the end of this billing period. You can keep using Scribario until then.</i>\n"
        elif status == "canceled":
            text += "\n<i>Your subscription is canceled. You can use remaining credits until the end of your billing period.</i>\n"

        text += "\nNeed more credits? /topoff\nChange plan? /upgrade"

    # Add Customer Portal button if Stripe customer exists
    buttons = []
    if tenant.get("stripe_customer_id"):
        buttons.append([
            InlineKeyboardButton(
                text="Manage Subscription",
                callback_data="billing:portal",
            ),
        ])

    if buttons:
        await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    else:
        await message.answer(text)


@router.callback_query(F.data == "billing:portal")
async def on_billing_portal(callback: CallbackQuery) -> None:
    """Open Stripe Customer Portal."""
    if not callback.from_user or not callback.message:
        return

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Use /start first.")
        return

    tenant_id = membership["tenant_id"]
    client = get_supabase_client()
    result = client.table("tenants").select(
        "stripe_customer_id"
    ).eq("id", tenant_id).single().execute()

    if not result.data or not result.data.get("stripe_customer_id"):
        await callback.answer("No billing account found. Use /subscribe first.")
        return

    try:
        from bot.services.stripe_service import create_portal_session

        url = create_portal_session(result.data["stripe_customer_id"])
        await callback.message.answer(
            "Manage your subscription, update payment methods, or view invoices:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Open Billing Portal", url=url)],
            ]),
        )
        await callback.answer()
    except Exception:
        logger.exception("Failed to create portal session")
        await callback.answer("Something went wrong. Try again.")


@router.message(Command("usage"))
async def cmd_usage(message: Message) -> None:
    """Show detailed usage with visual progress bars."""
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
        "video_credits_remaining, trial_posts_used, trial_posts_limit, "
        "trial_videos_used, trial_video_limit, bonus_posts, bonus_videos"
    ).eq("id", tenant_id).single().execute()

    tenant = result.data
    if not tenant:
        await message.answer("Account data not found.")
        return

    plan = tenant["plan_tier"]

    if plan == "free_trial":
        used = tenant["trial_posts_used"] or 0
        limit = tenant["trial_posts_limit"] or 5
        vused = tenant.get("trial_videos_used") or 0
        vlimit = tenant.get("trial_video_limit") or 1
        text = (
            "<b>Usage — Free Trial</b>\n\n"
            f"<b>Posts</b>\n{_progress_bar(used, limit, 15)}\n\n"
            f"<b>Videos</b>\n{_progress_bar(vused, vlimit, 15)}\n\n"
        )
        if used >= limit and vused >= vlimit:
            text += "You've used all your free credits! /subscribe to continue."
        elif used >= limit:
            text += "Posts used up! You still have video credits. /subscribe for more posts."
        else:
            remaining = limit - used
            text += f"{remaining} posts remaining. Keep creating!"
    else:
        plan_info = PLANS.get(plan, {})
        used = tenant["monthly_posts_used"] or 0
        limit = tenant["monthly_post_limit"] or 0
        videos = tenant["video_credits_remaining"] or 0
        bonus_p = tenant.get("bonus_posts") or 0
        bonus_v = tenant.get("bonus_videos") or 0
        total_posts = limit + bonus_p
        total_videos = videos + bonus_v

        text = (
            f"<b>Usage — {plan_info.get('name', plan.title())}</b>\n\n"
            f"<b>Posts this month</b>\n{_progress_bar(used, total_posts, 15)}\n"
        )
        if bonus_p > 0:
            text += f"  <i>(includes {bonus_p} bonus posts)</i>\n"

        text += (
            f"\n<b>Video credits</b>\n"
            f"  {total_videos} remaining"
        )
        if bonus_v > 0:
            text += f" <i>(includes {bonus_v} bonus)</i>"
        text += "\n"

        # Warning if approaching limit
        if total_posts > 0 and used / total_posts >= 0.8:
            text += "\n<b>You're running low on posts!</b> /topoff for more."
        if total_videos == 0:
            text += "\n<b>No video credits left!</b> /topoff for more."

        text += "\n\nNeed more? /topoff"

    await message.answer(text)


@router.message(Command("topoff"))
async def cmd_topoff(message: Message) -> None:
    """Show top-off bundle options."""
    user = message.from_user
    if not user:
        return

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer("Use /start to set up your account first.")
        return

    tenant_id = membership["tenant_id"]

    # Check purchase caps (3 per category per month)
    client = get_supabase_client()
    result = client.table("tenants").select(
        "plan_tier, subscription_status, "
        "bonus_posts_purchased_this_month, bonus_videos_purchased_this_month"
    ).eq("id", tenant_id).single().execute()

    tenant = result.data
    if not tenant:
        await message.answer("Account data not found.")
        return

    if tenant["plan_tier"] == "free_trial":
        await message.answer(
            "Top-offs are available for paid subscribers.\n"
            "Use /subscribe to get started!"
        )
        return

    settings = get_settings()
    if not settings.stripe_api_key:
        await message.answer("Top-offs are being set up. Check back soon!")
        return

    posts_bought = tenant.get("bonus_posts_purchased_this_month") or 0
    videos_bought = tenant.get("bonus_videos_purchased_this_month") or 0

    buttons = []
    text = "<b>Top-Off Bundles</b>\n\nAdd extra credits to your account:\n\n"

    for topoff_key, info in TOPOFFS.items():
        text += f"<b>{info['name']}</b> — {info['price']}\n"

        # Check cap (3 per category per month)
        if topoff_key == "images":
            capped = posts_bought >= 3
        else:
            capped = videos_bought >= 3

        if capped:
            text += "  <i>(max 3 purchases this month — limit reached)</i>\n"
        else:
            buttons.append([
                InlineKeyboardButton(
                    text=f"{info['name']} — {info['price']}",
                    callback_data=f"topoff:{topoff_key}",
                ),
            ])
        text += "\n"

    text += "<i>Top-offs are one-time purchases. Credits are added immediately.</i>"

    if buttons:
        await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    else:
        await message.answer(text)


@router.callback_query(F.data.startswith("topoff:"))
async def on_topoff_callback(callback: CallbackQuery) -> None:
    """Handle topoff:{type} callback — create Stripe Checkout for one-time purchase."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    topoff_type = callback.data.split(":", 1)[1]
    if topoff_type not in TOPOFFS:
        await callback.answer("Unknown bundle.")
        return

    membership = await get_tenant_by_telegram_user(callback.from_user.id)
    if not membership:
        await callback.answer("Use /start first.")
        return

    tenant_id = membership["tenant_id"]
    chat_id = callback.message.chat.id

    try:
        from bot.services.stripe_service import create_topoff_checkout, get_topoff_price_id

        # C2 fix: server-side cap check before creating checkout
        client = get_supabase_client()
        cap_type = "images" if topoff_type == "images" else "videos"
        cap_result = client.rpc("check_topoff_cap", {
            "p_tenant_id": tenant_id, "p_topoff_type": cap_type,
        }).execute()
        if not cap_result.data:
            await callback.answer("You've reached the monthly top-off limit (3 per category).")
            return

        price_id = get_topoff_price_id(topoff_type)
        if not price_id:
            await callback.answer("This bundle isn't available yet.")
            return

        url = create_topoff_checkout(tenant_id, price_id, chat_id)
        info = TOPOFFS[topoff_type]

        await callback.message.answer(
            f"<b>Top-Off: {info['name']} — {info['price']}</b>\n\n"
            f"Tap below to complete your purchase:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Complete Purchase", url=url)],
            ]),
        )
        await callback.answer()
    except Exception:
        logger.exception("Failed to create top-off checkout")
        await callback.answer("Something went wrong. Try again.")


@router.message(Command("upgrade"))
async def cmd_upgrade(message: Message) -> None:
    """Direct to plan upgrade options."""
    await cmd_subscribe(message)
