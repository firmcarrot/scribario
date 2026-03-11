"""Onboarding dialog — multi-step flow for new users via aiogram_dialog.

Flow:
1. Welcome — explain what Scribario does
2. Business Name — ask for their business name
3. Website URL — ask for their website (triggers scrape + brand gen inline)
4. Profile Review — show generated profile, ask for confirmation
5. Complete — welcome them, ready to create content

NOTE: The "scraping" state exists only as a visual placeholder. All scraping
and brand generation happens inline in on_website_url_input before switching
to profile_review. This avoids the aiogram_dialog on_process_result issue
(it only fires on sub-dialog return, not on state entry).
"""

from __future__ import annotations

import logging
import random
import re
import string

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.states import OnboardingSG

logger = logging.getLogger(__name__)


def _make_slug(name: str) -> str:
    """Generate a URL-safe slug from a business name with random suffix."""
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{base}-{suffix}"


# --- Handlers ---


async def on_start_onboarding(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    """User clicked 'Get Started' — move to business name input."""
    await manager.switch_to(OnboardingSG.business_name)


async def on_business_name_input(
    message: Message, widget: MessageInput, manager: DialogManager
) -> None:
    """User typed their business name."""
    name = (message.text or "").strip()
    if not name or len(name) < 2:
        await message.answer("Please enter a valid business name (at least 2 characters).")
        return

    manager.dialog_data["business_name"] = name
    await manager.switch_to(OnboardingSG.website_url)


async def on_website_url_input(
    message: Message, widget: MessageInput, manager: DialogManager
) -> None:
    """User typed their website URL — validate, scrape, generate profile, then show review."""
    from bot.db import (
        create_tenant,
        create_tenant_member,
        update_tenant_website_url,
        upsert_brand_profile,
    )
    from pipeline.brand_gen import generate_brand_profile
    from pipeline.scraper import scrape_website

    url = (message.text or "").strip()

    if not url:
        await message.answer("Please enter your website URL.")
        return

    if not url.startswith("http"):
        url = f"https://{url}"

    if not re.match(r"https?://[\w.-]+\.\w{2,}", url):
        await message.answer(
            "That doesn't look like a valid URL. "
            "Please enter something like: mondoshrimp.com"
        )
        return

    manager.dialog_data["website_url"] = url
    business_name = manager.dialog_data.get("business_name", "Brand")
    user = message.from_user

    if not user:
        return

    # Send a "working on it" message
    status_msg = await message.answer(
        f"Analyzing <b>{business_name}</b>'s website...\n\n"
        "I'm scraping your website and building a brand voice profile. "
        "This takes about 15-30 seconds."
    )

    try:
        # Reuse existing tenant if retrying (C2 fix — no duplicates on "Try Again")
        tenant_id = manager.dialog_data.get("tenant_id")
        if not tenant_id:
            slug = _make_slug(business_name)
            tenant = await create_tenant(
                name=business_name,
                slug=slug,
                website_url=url,
            )
            tenant_id = tenant["id"]

            await create_tenant_member(
                tenant_id=tenant_id,
                telegram_user_id=user.id,
                role="owner",
            )
            manager.dialog_data["tenant_id"] = tenant_id
        else:
            # Retry path — just update the website URL
            await update_tenant_website_url(tenant_id, url)

        # Scrape website
        scraped = await scrape_website(url)

        # Generate brand profile via Claude
        profile = await generate_brand_profile(scraped)

        # Save brand profile to DB
        # NOTE: brand_profiles table has no "name" column — don't include it
        # compliance_notes is NOT NULL DEFAULT '' — pass empty string, not None
        profile_data = {
            "tone_words": profile.tone_words,
            "audience_description": profile.audience_description,
            "do_list": profile.do_list,
            "dont_list": profile.dont_list,
            "product_catalog": profile.product_catalog,
            "compliance_notes": profile.compliance_notes or "",
            "scraped_data": {
                "url": scraped.url,
                "title": scraped.title,
                "description": scraped.description,
                "headings": scraped.headings[:10],
                "social_links": scraped.social_links,
                "products": scraped.products,
            },
        }
        await upsert_brand_profile(tenant_id, profile_data)

        # Store results for the review screen
        manager.dialog_data["profile_name"] = profile.name
        manager.dialog_data["tone_words"] = ", ".join(profile.tone_words)
        manager.dialog_data["audience"] = profile.audience_description
        manager.dialog_data["do_list"] = "\n".join(f"  - {d}" for d in profile.do_list)
        manager.dialog_data["dont_list"] = "\n".join(f"  - {d}" for d in profile.dont_list)
        manager.dialog_data["tagline"] = profile.tagline or "(none found)"

        products_text = ", ".join(
            p["name"] if isinstance(p, dict) else str(p) for p in profile.product_catalog[:5]
        )
        manager.dialog_data["products"] = products_text or "(none found)"

        social_text = ", ".join(
            f"{k.title()}" for k in scraped.social_links.keys()
        )
        manager.dialog_data["social_platforms"] = social_text or "(none found)"

        await status_msg.edit_text("Analysis complete! Here's what I found:")
        await manager.switch_to(OnboardingSG.profile_review)

    except Exception:
        logger.exception("Onboarding scrape/generate failed")
        await status_msg.edit_text(
            "Something went wrong analyzing your website. "
            "Don't worry — you can still use Scribario! "
            "I'll set up a basic profile and you can refine it later."
        )

        # Fallback: reuse existing tenant if already created, otherwise create one
        try:
            tenant_id = manager.dialog_data.get("tenant_id")
            if not tenant_id:
                slug = _make_slug(business_name)
                tenant = await create_tenant(
                    name=business_name, slug=slug, website_url=url
                )
                tenant_id = tenant["id"]
                await create_tenant_member(
                    tenant_id=tenant_id,
                    telegram_user_id=user.id,
                    role="owner",
                )
                manager.dialog_data["tenant_id"] = tenant_id

            await upsert_brand_profile(tenant_id, {
                "tone_words": ["professional", "engaging"],
                "audience_description": "General audience",
                "do_list": [],
                "dont_list": [],
                "compliance_notes": "",
            })
            manager.dialog_data["profile_name"] = business_name
        except Exception:
            logger.exception("Fallback tenant creation also failed")

        await manager.switch_to(OnboardingSG.complete)


async def on_approve_profile(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    """User approved the generated brand profile."""
    from bot.db import update_onboarding_status

    tenant_id = manager.dialog_data.get("tenant_id")
    user = callback.from_user
    if tenant_id and user:
        await update_onboarding_status(tenant_id, user.id, "complete")

    await manager.switch_to(OnboardingSG.complete)


async def on_reject_profile(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    """User wants to redo — go back to website URL step."""
    await manager.switch_to(OnboardingSG.website_url)


# --- Getters (data providers for Format widgets) ---


async def get_profile_review_data(dialog_manager: DialogManager, **kwargs):
    """Provide data for the profile review window."""
    return {
        "profile_name": dialog_manager.dialog_data.get("profile_name", "Brand"),
        "tone_words": dialog_manager.dialog_data.get("tone_words", ""),
        "audience": dialog_manager.dialog_data.get("audience", ""),
        "do_list": dialog_manager.dialog_data.get("do_list", ""),
        "dont_list": dialog_manager.dialog_data.get("dont_list", ""),
        "tagline": dialog_manager.dialog_data.get("tagline", ""),
        "products": dialog_manager.dialog_data.get("products", ""),
        "social_platforms": dialog_manager.dialog_data.get("social_platforms", ""),
    }


async def get_complete_data(dialog_manager: DialogManager, **kwargs):
    """Provide data for the completion window."""
    return {
        "profile_name": dialog_manager.dialog_data.get("profile_name", "your brand"),
    }


# --- Dialog Definition ---

dialog = Dialog(
    Window(
        Const(
            "<b>Welcome to Scribario!</b>\n\n"
            "I'm your AI social media assistant. I create images and captions "
            "for your business, send you previews, and post to your platforms "
            "when you approve.\n\n"
            "Let's set up your brand in about 60 seconds."
        ),
        Button(Const("Get Started"), id="start_onboarding", on_click=on_start_onboarding),
        state=OnboardingSG.welcome,
    ),
    Window(
        Const(
            "<b>What's your business name?</b>\n\n"
            "Just type it below (e.g., Mondo Shrimp, Coastal Coffee, etc.)"
        ),
        MessageInput(on_business_name_input),
        state=OnboardingSG.business_name,
    ),
    Window(
        Const(
            "<b>What's your website URL?</b>\n\n"
            "I'll scrape it to learn about your brand, products, and voice.\n\n"
            "Just type it below (e.g., mondoshrimp.com)"
        ),
        MessageInput(on_website_url_input),
        state=OnboardingSG.website_url,
    ),
    Window(
        Const("Analyzing your website... Please wait."),
        state=OnboardingSG.scraping,
    ),
    Window(
        Format(
            "<b>Here's your brand profile:</b>\n\n"
            "<b>Name:</b> {profile_name}\n"
            "<b>Tagline:</b> {tagline}\n"
            "<b>Tone:</b> {tone_words}\n"
            "<b>Target Audience:</b> {audience}\n\n"
            "<b>Do:</b>\n{do_list}\n\n"
            "<b>Don't:</b>\n{dont_list}\n\n"
            "<b>Products:</b> {products}\n"
            "<b>Social:</b> {social_platforms}\n\n"
            "Does this look right?"
        ),
        Button(Const("Looks Great!"), id="approve_profile", on_click=on_approve_profile),
        Button(Const("Try Again"), id="reject_profile", on_click=on_reject_profile),
        state=OnboardingSG.profile_review,
        getter=get_profile_review_data,
    ),
    Window(
        Format(
            "<b>You're all set!</b>\n\n"
            "Your brand profile for <b>{profile_name}</b> is ready.\n\n"
            "Just send me a message anytime about what you want to post, like:\n"
            '<i>"Post about our weekend special"</i>\n\n'
            "I'll generate images and captions, show you a preview, "
            "and post to your platforms when you approve."
        ),
        state=OnboardingSG.complete,
        getter=get_complete_data,
    ),
)
