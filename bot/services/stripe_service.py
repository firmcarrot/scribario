"""Stripe service — Checkout sessions, Customer Portal, customer management."""

from __future__ import annotations

import logging

import stripe

from bot.config import get_settings

logger = logging.getLogger(__name__)

# Plan tier → (monthly_post_limit, video_credits)
# NOTE: Also defined in scripts/connect_server.py — keep in sync!
TIER_LIMITS = {
    "starter": {"posts": 15, "videos": 5},
    "growth": {"posts": 40, "videos": 15},
    "pro": {"posts": 100, "videos": 40},
}


def _init_stripe() -> None:
    """Set stripe API key from settings."""
    settings = get_settings()
    stripe.api_key = settings.stripe_api_key


def get_or_create_customer(tenant_id: str, email: str | None = None) -> str:
    """Get existing Stripe customer or create one. Returns customer ID."""
    _init_stripe()
    from bot.db import get_supabase_client

    client = get_supabase_client()
    result = (
        client.table("tenants")
        .select("stripe_customer_id, name")
        .eq("id", tenant_id)
        .single()
        .execute()
    )
    tenant = result.data
    if not tenant:
        raise ValueError(f"Tenant {tenant_id} not found")

    if tenant.get("stripe_customer_id"):
        return tenant["stripe_customer_id"]

    # Create new Stripe customer
    customer = stripe.Customer.create(
        metadata={"tenant_id": tenant_id},
        name=tenant.get("name", ""),
        email=email,
    )

    # Save to DB
    client.table("tenants").update(
        {"stripe_customer_id": customer.id}
    ).eq("id", tenant_id).execute()

    logger.info("Created Stripe customer %s for tenant %s", customer.id, tenant_id)
    return customer.id


def create_checkout_session(
    tenant_id: str,
    price_id: str,
    chat_id: int,
    is_annual: bool = False,
) -> str:
    """Create a Stripe Checkout session for subscription. Returns checkout URL."""
    _init_stripe()
    settings = get_settings()

    customer_id = get_or_create_customer(tenant_id)

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=(
            f"{settings.connect_base_url}/subscribed"
            f"?chat_id={chat_id}&session_id={{CHECKOUT_SESSION_ID}}"
        ),
        cancel_url=f"https://t.me/ScribarioBot",
        metadata={
            "tenant_id": tenant_id,
            "chat_id": str(chat_id),
        },
        subscription_data={
            "metadata": {
                "tenant_id": tenant_id,
                "chat_id": str(chat_id),
            },
        },
        allow_promotion_codes=True,
    )
    logger.info(
        "Created checkout session %s for tenant %s (price=%s)",
        session.id, tenant_id, price_id,
    )
    return session.url


def create_topoff_checkout(
    tenant_id: str,
    price_id: str,
    chat_id: int,
) -> str:
    """Create a Stripe Checkout session for one-time top-off purchase. Returns URL."""
    _init_stripe()
    settings = get_settings()

    customer_id = get_or_create_customer(tenant_id)

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="payment",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=(
            f"{settings.connect_base_url}/subscribed"
            f"?chat_id={chat_id}&type=topoff&session_id={{CHECKOUT_SESSION_ID}}"
        ),
        cancel_url=f"https://t.me/ScribarioBot",
        metadata={
            "tenant_id": tenant_id,
            "chat_id": str(chat_id),
            "type": "topoff",
        },
    )
    logger.info(
        "Created top-off checkout %s for tenant %s (price=%s)",
        session.id, tenant_id, price_id,
    )
    return session.url


def create_portal_session(stripe_customer_id: str) -> str:
    """Create a Stripe Customer Portal session. Returns portal URL."""
    _init_stripe()
    settings = get_settings()

    session = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url="https://t.me/ScribarioBot",
        **({"configuration": settings.stripe_portal_config_id}
           if settings.stripe_portal_config_id else {}),
    )
    return session.url


def get_price_id_for_tier(tier: str, annual: bool = False) -> str | None:
    """Map tier name + annual flag to Stripe price ID from config."""
    settings = get_settings()
    mapping = {
        ("starter", False): settings.stripe_starter_price_id,
        ("growth", False): settings.stripe_growth_price_id,
        ("pro", False): settings.stripe_pro_price_id,
        ("starter", True): settings.stripe_starter_annual_price_id,
        ("growth", True): settings.stripe_growth_annual_price_id,
        ("pro", True): settings.stripe_pro_annual_price_id,
    }
    return mapping.get((tier, annual)) or None


def get_topoff_price_id(topoff_type: str) -> str | None:
    """Map top-off type to Stripe price ID."""
    settings = get_settings()
    mapping = {
        "images": settings.stripe_topoff_images_price_id,
        "short_videos": settings.stripe_topoff_short_videos_price_id,
        "long_video": settings.stripe_topoff_long_video_price_id,
    }
    return mapping.get(topoff_type) or None
