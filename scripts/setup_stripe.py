#!/usr/bin/env python3
"""Create Stripe products and prices for Scribario.

Run once to set up all subscription tiers + top-off bundles.
Prints .env lines to paste into your .env file.

Usage:
    python scripts/setup_stripe.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.environ["STRIPE_API_KEY"]

TIERS = {
    "starter": {"monthly": 2900, "annual": 27800, "posts": 15, "videos": 5},
    "growth": {"monthly": 5900, "annual": 56600, "posts": 40, "videos": 15},
    "pro": {"monthly": 9900, "annual": 95000, "posts": 100, "videos": 40},
}

TOPOFFS = {
    "images": {"amount": 500, "name": "+10 Image Posts", "description": "10 additional image posts"},
    "short_videos": {"amount": 1200, "name": "+5 Short Videos", "description": "5 additional short videos"},
    "long_video": {"amount": 600, "name": "+1 Long Video", "description": "1 additional long-form video"},
}


def create_products_and_prices() -> dict[str, str]:
    """Create all Stripe products and prices. Returns dict of env key -> price ID."""
    env_lines: dict[str, str] = {}

    # --- Subscription products ---
    for tier, config in TIERS.items():
        product = stripe.Product.create(
            name=f"Scribario {tier.title()}",
            description=f"{config['posts']} posts/mo + {config['videos']} videos/mo",
            metadata={"tier": tier, "posts": str(config["posts"]), "videos": str(config["videos"])},
        )
        print(f"Created product: {product.name} ({product.id})")

        # Monthly price
        monthly_price = stripe.Price.create(
            product=product.id,
            unit_amount=config["monthly"],
            currency="usd",
            recurring={"interval": "month"},
            metadata={"tier": tier, "interval": "monthly"},
        )
        env_lines[f"STRIPE_{tier.upper()}_PRICE_ID"] = monthly_price.id
        print(f"  Monthly: ${config['monthly'] / 100:.0f}/mo -> {monthly_price.id}")

        # Annual price
        annual_price = stripe.Price.create(
            product=product.id,
            unit_amount=config["annual"],
            currency="usd",
            recurring={"interval": "year"},
            metadata={"tier": tier, "interval": "annual"},
        )
        env_lines[f"STRIPE_{tier.upper()}_ANNUAL_PRICE_ID"] = annual_price.id
        print(f"  Annual: ${config['annual'] / 100:.0f}/yr -> {annual_price.id}")

    # --- Top-off products (one-time) ---
    for key, config in TOPOFFS.items():
        product = stripe.Product.create(
            name=f"Scribario Top-Off: {config['name']}",
            description=config["description"],
            metadata={"topoff": key},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=config["amount"],
            currency="usd",
            metadata={"topoff": key},
        )
        env_key = f"STRIPE_TOPOFF_{key.upper()}_PRICE_ID"
        env_lines[env_key] = price.id
        print(f"Top-off {config['name']}: ${config['amount'] / 100:.0f} -> {price.id}")

    # --- Customer Portal ---
    portal_config = stripe.billing_portal.Configuration.create(
        business_profile={
            "headline": "Scribario — Manage your subscription",
        },
        features={
            "subscription_cancel": {"enabled": True, "mode": "at_period_end"},
            "subscription_update": {
                "enabled": True,
                "default_allowed_updates": ["price"],
                "proration_behavior": "create_prorations",
                "products": [],  # Will be populated after creation
            },
            "payment_method_update": {"enabled": True},
            "invoice_history": {"enabled": True},
        },
    )
    env_lines["STRIPE_PORTAL_CONFIG_ID"] = portal_config.id
    print(f"Portal config: {portal_config.id}")

    return env_lines


def main() -> None:
    print(f"Using Stripe key: {stripe.api_key[:12]}...\n")

    env_lines = create_products_and_prices()

    print("\n" + "=" * 60)
    print("Add these to your .env file:")
    print("=" * 60)
    for key, value in env_lines.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
