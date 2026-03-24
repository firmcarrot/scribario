"""Lightweight OAuth connect proxy for Scribario.

Serves:
- GET  /connect/{platform}?chat_id={chat_id}  → redirects to Postiz enterprise OAuth
- GET  /connected                              → success page ("go back to Telegram")
- POST /api/connect/callback                   → webhook from Postiz after OAuth completes

Runs as a simple ASGI app on the VPS behind nginx.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from urllib.parse import parse_qs, urlparse

from html import escape as html_escape

import httpx
import jwt
import stripe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config from environment
POSTIZ_URL = os.environ.get("POSTIZ_URL", "https://postiz.scribario.com")
POSTIZ_API_KEY = os.environ.get("POSTIZ_API_KEY", "")
POSTIZ_JWT_SECRET = os.environ.get("POSTIZ_JWT_SECRET", "")
SCRIBARIO_BASE_URL = os.environ.get("SCRIBARIO_BASE_URL", "https://connect.scribario.com")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Meta (Facebook/Instagram)
FACEBOOK_APP_SECRET = os.environ.get("FACEBOOK_APP_SECRET", "")

# Stripe
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Supabase (for webhook DB updates)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# Tier limits: plan_tier -> (monthly_post_limit, video_credits)
# NOTE: Also defined in bot/services/stripe_service.py — keep in sync!
TIER_LIMITS = {
    "starter": {"posts": 15, "videos": 5},
    "growth": {"posts": 40, "videos": 15},
    "pro": {"posts": 100, "videos": 40},
}

# Top-off credits by price metadata
TOPOFF_CREDITS = {
    "images": {"bonus_posts": 10},
    "short_videos": {"bonus_videos": 5},
    "long_video": {"bonus_videos": 1},
}

_supabase_client = None


def _get_supabase():
    """Lazy-init Supabase client for webhook handler."""
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase_client

ALLOWED_PLATFORMS = {
    "facebook", "instagram", "linkedin", "youtube",
    "tiktok", "twitter", "pinterest", "threads", "bluesky",
}

PLATFORM_NAMES = {
    "facebook": "Facebook",
    "instagram": "Instagram",
    "linkedin": "LinkedIn",
    "youtube": "YouTube",
    "tiktok": "TikTok",
    "twitter": "X / Twitter",
    "pinterest": "Pinterest",
    "threads": "Threads",
    "bluesky": "Bluesky",
}

# Store pending connections: state → chat_id
_pending_connections: dict[str, str] = {}


def _generate_enterprise_jwt(platform: str, chat_id: str) -> str:
    """Sign a JWT for the Postiz enterprise endpoint."""
    payload = {
        "redirectUrl": f"{SCRIBARIO_BASE_URL}/connected?platform={platform}&chat_id={chat_id}",
        "apiKey": POSTIZ_API_KEY,
        "provider": platform,
        "webhookUrl": f"{SCRIBARIO_BASE_URL}/api/connect/callback",
    }
    return jwt.encode(payload, POSTIZ_JWT_SECRET, algorithm="HS256")


async def _get_oauth_url(platform: str, chat_id: str) -> str | None:
    """Get OAuth URL from Postiz enterprise endpoint."""
    token = _generate_enterprise_jwt(platform, chat_id)
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{POSTIZ_URL}/api/enterprise/url",
            json={"params": token},
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code == 201 and resp.text:
            return resp.text.strip().strip('"')
    return None


async def _notify_telegram(chat_id: str, platform: str) -> None:
    """Send a confirmation message to the user in Telegram."""
    name = PLATFORM_NAMES.get(platform, platform)
    text = (
        f"<b>{name} connected!</b> \u2705\n\n"
        "You're all set. Send me a message about what you'd like to post, like:\n"
        '<i>"Post about our weekend special — 20% off all pizzas"</i>'
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        })
    logger.info("Sent connection confirmation to chat_id=%s for %s", chat_id, platform)


SUCCESS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connected! — Scribario</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .card {{
            background: white;
            border-radius: 24px;
            padding: 48px 32px;
            max-width: 400px;
            width: 100%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .checkmark {{
            font-size: 64px;
            margin-bottom: 16px;
        }}
        h1 {{
            font-size: 24px;
            color: #1a1a2e;
            margin-bottom: 12px;
        }}
        p {{
            font-size: 16px;
            color: #666;
            line-height: 1.5;
            margin-bottom: 24px;
        }}
        .btn {{
            display: inline-block;
            background: #0088cc;
            color: white;
            text-decoration: none;
            padding: 14px 32px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            transition: background 0.2s;
        }}
        .btn:hover {{ background: #006daa; }}
        .brand {{
            margin-top: 32px;
            font-size: 13px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="checkmark">\u2705</div>
        <h1>{platform_name} Connected!</h1>
        <p>Your account is linked. Every post you approve in Scribario will be published to {platform_name} automatically.</p>
        <a href="https://t.me/ScribarioBot" class="btn">Back to Telegram</a>
        <p class="brand">Scribario — AI content on autopilot</p>
    </div>
</body>
</html>"""

CONNECT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connecting... — Scribario</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .card {{
            background: white;
            border-radius: 24px;
            padding: 48px 32px;
            max-width: 400px;
            width: 100%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .spinner {{
            width: 48px; height: 48px;
            border: 4px solid #eee;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 24px;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        h1 {{ font-size: 20px; color: #1a1a2e; margin-bottom: 8px; }}
        p {{ font-size: 14px; color: #666; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="spinner"></div>
        <h1>Connecting to {platform_name}...</h1>
        <p>You'll be redirected to authorize your account.</p>
    </div>
    <script>
        // Auto-redirect after brief pause so user sees the loading state
        setTimeout(function() {{ window.location.href = "{oauth_url}"; }}, 800);
    </script>
</body>
</html>"""

ERROR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error — Scribario</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .card {{
            background: white;
            border-radius: 24px;
            padding: 48px 32px;
            max-width: 400px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        h1 {{ font-size: 20px; color: #e74c3c; margin-bottom: 12px; }}
        p {{ font-size: 14px; color: #666; line-height: 1.5; }}
        .btn {{
            display: inline-block; margin-top: 20px;
            background: #0088cc; color: white; text-decoration: none;
            padding: 12px 28px; border-radius: 12px; font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Something went wrong</h1>
        <p>{message}</p>
        <a href="https://t.me/ScribarioBot" class="btn">Back to Telegram</a>
    </div>
</body>
</html>"""


SUBSCRIBED_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subscribed! — Scribario</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .card {{
            background: white;
            border-radius: 24px;
            padding: 48px 32px;
            max-width: 400px;
            width: 100%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .checkmark {{ font-size: 64px; margin-bottom: 16px; }}
        h1 {{ font-size: 24px; color: #1a1a2e; margin-bottom: 12px; }}
        p {{ font-size: 16px; color: #666; line-height: 1.5; margin-bottom: 24px; }}
        .btn {{
            display: inline-block;
            background: #0088cc; color: white; text-decoration: none;
            padding: 14px 32px; border-radius: 12px; font-size: 16px; font-weight: 600;
            transition: background 0.2s;
        }}
        .btn:hover {{ background: #006daa; }}
        .brand {{ margin-top: 32px; font-size: 13px; color: #999; }}
    </style>
    <script>
        // Auto-redirect to Telegram after 3 seconds
        setTimeout(function() {{ window.location.href = "https://t.me/ScribarioBot"; }}, 3000);
    </script>
</head>
<body>
    <div class="card">
        <div class="checkmark">\u2705</div>
        <h1>{title}</h1>
        <p>{message}</p>
        <a href="https://t.me/ScribarioBot" class="btn">Back to Telegram</a>
        <p class="brand">Scribario — AI content on autopilot</p>
    </div>
</body>
</html>"""


# --- Stripe Webhook Handling ---


def _resolve_tier_from_price(price_id: str) -> str | None:
    """Map a Stripe price ID back to a plan tier."""
    price_to_tier = {}
    for tier in ("starter", "growth", "pro"):
        for suffix in ("_PRICE_ID", "_ANNUAL_PRICE_ID"):
            env_key = f"STRIPE_{tier.upper()}{suffix}"
            val = os.environ.get(env_key, "")
            if val:
                price_to_tier[val] = tier
    return price_to_tier.get(price_id)


def _resolve_topoff_from_price(price_id: str) -> str | None:
    """Map a Stripe price ID back to a top-off type."""
    for topoff_key in ("images", "short_videos", "long_video"):
        env_key = f"STRIPE_TOPOFF_{topoff_key.upper()}_PRICE_ID"
        if os.environ.get(env_key, "") == price_id:
            return topoff_key
    return None


async def _handle_checkout_completed(session: dict) -> None:
    """Process checkout.session.completed — activate subscription or apply top-off."""
    metadata = session.get("metadata", {})
    tenant_id = metadata.get("tenant_id")
    chat_id = metadata.get("chat_id")
    mode = session.get("mode")

    if not tenant_id:
        logger.warning("Checkout session missing tenant_id metadata: %s", session.get("id"))
        return

    client = _get_supabase()

    if mode == "subscription":
        # Subscription checkout — activate the plan
        subscription_id = session.get("subscription")
        customer_id = session.get("customer")

        # Fetch the subscription to get price info
        stripe.api_key = STRIPE_API_KEY
        sub = stripe.Subscription.retrieve(subscription_id)
        price_id = sub["items"]["data"][0]["price"]["id"]
        tier = _resolve_tier_from_price(price_id)

        if not tier:
            logger.error("Unknown price ID %s in subscription %s", price_id, subscription_id)
            return

        limits = TIER_LIMITS[tier]
        period_end = sub.get("current_period_end")

        # Activate tenant
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()

        update_data = {
            "plan_tier": tier,
            "subscription_status": "active",
            "stripe_subscription_id": subscription_id,
            "stripe_customer_id": customer_id,
            "monthly_post_limit": limits["posts"],
            "video_credits_remaining": limits["videos"],
            "monthly_posts_used": 0,
            "billing_started_at": now_iso,
        }
        if period_end:
            update_data["current_period_end"] = datetime.fromtimestamp(
                period_end, tz=timezone.utc
            ).isoformat()

        client.table("tenants").update(update_data).eq("id", tenant_id).execute()
        logger.info("Activated %s plan for tenant %s (sub=%s)", tier, tenant_id, subscription_id)

        # Notify user in Telegram
        if chat_id:
            plan_name = tier.title()
            await _notify_telegram_billing(
                chat_id,
                f"<b>Welcome to Scribario {plan_name}!</b> \u2705\n\n"
                f"Your plan is now active:\n"
                f"• {limits['posts']} posts/month\n"
                f"• {limits['videos']} video credits\n\n"
                "Start creating! Just send me what you want to post."
            )

    elif mode == "payment":
        # One-time top-off purchase
        topoff_type = metadata.get("type")
        if topoff_type != "topoff":
            return

        # Get line items to determine which top-off
        stripe.api_key = STRIPE_API_KEY
        line_items = stripe.checkout.Session.list_line_items(session["id"], limit=1)
        if not line_items.data:
            return

        price_id = line_items.data[0]["price"]["id"]
        topoff_key = _resolve_topoff_from_price(price_id)
        if not topoff_key:
            logger.error("Unknown top-off price %s", price_id)
            return

        credits = TOPOFF_CREDITS[topoff_key]

        # Apply credits atomically via RPC (C1 fix: race-safe)
        client.rpc("apply_topoff_credits", {
            "p_tenant_id": tenant_id,
            "p_bonus_posts": credits.get("bonus_posts", 0),
            "p_bonus_videos": credits.get("bonus_videos", 0),
        }).execute()
        logger.info("Applied top-off %s for tenant %s", topoff_key, tenant_id)

        if chat_id:
            desc = TOPOFF_CREDITS[topoff_key]
            parts = []
            if "bonus_posts" in desc:
                parts.append(f"+{desc['bonus_posts']} bonus posts")
            if "bonus_videos" in desc:
                parts.append(f"+{desc['bonus_videos']} bonus videos")
            await _notify_telegram_billing(
                chat_id,
                f"<b>Top-off applied!</b> \u2705\n\n"
                f"{', '.join(parts)} added to your account.\n\n"
                "Check your balance: /usage"
            )


async def _handle_invoice_paid(invoice: dict) -> None:
    """Process invoice.paid — reset monthly counters on renewal only."""
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return

    # Only reset counters on actual renewals, not the initial subscription invoice
    billing_reason = invoice.get("billing_reason", "")
    if billing_reason not in ("subscription_cycle", "subscription_update"):
        logger.info(
            "Skipping invoice.paid for billing_reason=%s (sub=%s)",
            billing_reason, subscription_id,
        )
        return

    client = _get_supabase()
    result = client.table("tenants").select(
        "id, plan_tier"
    ).eq("stripe_subscription_id", subscription_id).maybe_single().execute()

    if not result.data:
        logger.info("No tenant found for subscription %s (invoice.paid)", subscription_id)
        return

    tenant = result.data
    tier = tenant["plan_tier"]
    limits = TIER_LIMITS.get(tier, {})

    if not limits:
        return

    # Reset monthly counters on renewal
    from datetime import datetime, timezone
    client.table("tenants").update({
        "monthly_posts_used": 0,
        "video_credits_remaining": limits["videos"],
        "subscription_status": "active",
        "monthly_posts_reset_at": datetime.now(timezone.utc).isoformat(),
        "bonus_posts_purchased_this_month": 0,
        "bonus_videos_purchased_this_month": 0,
    }).eq("id", tenant["id"]).execute()

    logger.info("Renewed %s for tenant %s", tier, tenant["id"])


async def _handle_invoice_payment_failed(invoice: dict) -> None:
    """Process invoice.payment_failed — set status to past_due."""
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return

    client = _get_supabase()
    result = client.table("tenants").select("id").eq(
        "stripe_subscription_id", subscription_id
    ).maybe_single().execute()

    if not result.data:
        logger.info("No tenant found for subscription %s (payment_failed)", subscription_id)
        return

    tenant_id = result.data["id"]
    client.table("tenants").update({
        "subscription_status": "past_due"
    }).eq("id", tenant_id).execute()

    logger.info("Set tenant %s to past_due (payment failed)", tenant_id)

    # Try to notify via Telegram
    member_result = client.table("tenant_members").select(
        "telegram_user_id"
    ).eq("tenant_id", tenant_id).eq("role", "owner").limit(1).execute()

    if member_result.data:
        chat_id = member_result.data[0]["telegram_user_id"]
        await _notify_telegram_billing(
            str(chat_id),
            "<b>Payment failed</b>\n\n"
            "Your subscription payment couldn't be processed. "
            "Please update your payment method to continue creating content.\n\n"
            "Use /billing to manage your payment."
        )


async def _handle_subscription_updated(subscription: dict) -> None:
    """Process customer.subscription.updated — handle tier changes, cancellation."""
    subscription_id = subscription.get("id")
    status = subscription.get("status")
    cancel_at_period_end = subscription.get("cancel_at_period_end", False)

    client = _get_supabase()
    result = client.table("tenants").select("id, plan_tier").eq(
        "stripe_subscription_id", subscription_id
    ).maybe_single().execute()

    if not result.data:
        logger.info("No tenant found for subscription %s (may not be linked yet)", subscription_id)
        return

    tenant_id = result.data["id"]
    update = {}

    # Map Stripe status to our status
    status_map = {
        "active": "active",
        "past_due": "past_due",
        "canceled": "canceled",
        "unpaid": "past_due",
        "paused": "paused",
    }

    if cancel_at_period_end:
        # User initiated cancellation — keep active until period end
        from datetime import datetime, timezone
        update["canceled_at"] = datetime.now(timezone.utc).isoformat()
        period_end = subscription.get("current_period_end")
        if period_end:
            from datetime import datetime, timezone
            update["current_period_end"] = datetime.fromtimestamp(
                period_end, tz=timezone.utc
            ).isoformat()
    elif status in status_map:
        update["subscription_status"] = status_map[status]

    # Check if tier changed (upgrade/downgrade)
    items = subscription.get("items", {}).get("data", [])
    if items:
        price_id = items[0]["price"]["id"]
        new_tier = _resolve_tier_from_price(price_id)
        if new_tier and new_tier != result.data["plan_tier"]:
            limits = TIER_LIMITS[new_tier]
            update["plan_tier"] = new_tier
            update["monthly_post_limit"] = limits["posts"]
            update["video_credits_remaining"] = limits["videos"]

    if update:
        client.table("tenants").update(update).eq("id", tenant_id).execute()
        logger.info("Updated subscription for tenant %s: %s", tenant_id, update)


async def _handle_subscription_deleted(subscription: dict) -> None:
    """Process customer.subscription.deleted — final cancellation."""
    subscription_id = subscription.get("id")

    client = _get_supabase()
    result = client.table("tenants").select("id").eq(
        "stripe_subscription_id", subscription_id
    ).maybe_single().execute()

    if not result.data:
        logger.info("No tenant found for subscription %s", subscription_id)
        return

    tenant_id = result.data["id"]
    client.table("tenants").update({
        "subscription_status": "canceled",
    }).eq("id", tenant_id).execute()

    logger.info("Subscription deleted for tenant %s", tenant_id)

    # Notify
    member_result = client.table("tenant_members").select(
        "telegram_user_id"
    ).eq("tenant_id", tenant_id).eq("role", "owner").limit(1).execute()

    if member_result.data:
        chat_id = member_result.data[0]["telegram_user_id"]
        await _notify_telegram_billing(
            str(chat_id),
            "<b>Subscription ended</b>\n\n"
            "Your subscription has expired. Your content is safe — nothing gets deleted.\n\n"
            "Ready to come back? /subscribe"
        )


async def _notify_telegram_billing(chat_id: str, text: str) -> None:
    """Send a billing notification to user in Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        })


async def _process_stripe_webhook(body: bytes, sig_header: str) -> tuple[int, str]:
    """Validate and process a Stripe webhook event. Returns (status, message)."""
    try:
        event = stripe.Webhook.construct_event(body, sig_header, STRIPE_WEBHOOK_SECRET)
    except stripe.SignatureVerificationError:
        logger.warning("Invalid Stripe webhook signature")
        return 400, '{"error":"invalid signature"}'
    except Exception as e:
        logger.error("Stripe webhook error: %s", e)
        return 400, '{"error":"bad request"}'

    event_id = event["id"]
    event_type = event["type"]

    # Idempotency check
    client = _get_supabase()
    existing = client.table("stripe_events").select("id").eq(
        "event_id", event_id
    ).limit(1).execute()

    if existing.data:
        logger.info("Duplicate Stripe event %s, skipping", event_id)
        return 200, '{"ok":true,"duplicate":true}'

    # Record event
    client.table("stripe_events").insert({
        "event_id": event_id,
        "event_type": event_type,
        "payload": event.get("data", {}),
    }).execute()

    # Route to handler
    data_object = event["data"]["object"]
    try:
        if event_type == "checkout.session.completed":
            await _handle_checkout_completed(data_object)
        elif event_type == "invoice.paid":
            await _handle_invoice_paid(data_object)
        elif event_type == "invoice.payment_failed":
            await _handle_invoice_payment_failed(data_object)
        elif event_type == "customer.subscription.updated":
            await _handle_subscription_updated(data_object)
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(data_object)
        else:
            logger.info("Unhandled Stripe event type: %s", event_type)
    except Exception:
        logger.exception("Error processing Stripe event %s (%s)", event_id, event_type)
        # Delete the idempotency record so Stripe retry will reprocess
        try:
            client.table("stripe_events").delete().eq("event_id", event_id).execute()
        except Exception:
            logger.warning("Failed to delete idempotency record for %s", event_id)
        # Return 500 so Stripe retries (up to ~72 hours with exponential backoff)
        return 500, '{"error":"processing failed, will retry"}'

    return 200, '{"ok":true}'


async def app(scope: dict, receive: object, send: object) -> None:
    """ASGI application."""
    if scope["type"] != "http":
        return

    path = scope["path"]
    method = scope["method"]
    query_string = scope.get("query_string", b"").decode()
    params = parse_qs(query_string)

    async def respond(status: int, content_type: str, body: str) -> None:
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", content_type.encode()],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body.encode(),
        })

    async def redirect(url: str) -> None:
        await send({
            "type": "http.response.start",
            "status": 302,
            "headers": [
                [b"location", url.encode()],
                [b"content-type", b"text/html"],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": b"Redirecting...",
        })

    # GET /connect/{platform}?chat_id={chat_id}
    if method == "GET" and path.startswith("/connect/"):
        platform = path.split("/connect/", 1)[1].strip("/").lower()
        chat_id = params.get("chat_id", [""])[0]

        if platform not in ALLOWED_PLATFORMS:
            await respond(400, "text/html", ERROR_HTML.format(
                message=f"Unknown platform: {html_escape(platform)}"))
            return

        if not chat_id:
            await respond(400, "text/html", ERROR_HTML.format(
                message="Missing chat_id parameter. Please use the button in Telegram."))
            return

        oauth_url = await _get_oauth_url(platform, chat_id)
        if not oauth_url:
            await respond(500, "text/html", ERROR_HTML.format(
                message=f"Could not get authorization URL for {PLATFORM_NAMES.get(platform, platform)}. Please try again."))
            return

        platform_name = PLATFORM_NAMES.get(platform, platform)
        await respond(200, "text/html", CONNECT_HTML.format(
            platform_name=platform_name, oauth_url=oauth_url))
        return

    # GET /connected?platform={platform}&chat_id={chat_id}
    if method == "GET" and path == "/connected":
        platform = params.get("platform", [""])[0]
        chat_id = params.get("chat_id", [""])[0]
        platform_name = PLATFORM_NAMES.get(platform, platform or "your account")

        # Notify user in Telegram
        if chat_id and TELEGRAM_BOT_TOKEN:
            asyncio.create_task(_notify_telegram(chat_id, platform))

        await respond(200, "text/html", SUCCESS_HTML.format(
            platform_name=platform_name))
        return

    # POST /api/connect/callback — webhook from Postiz
    if method == "POST" and path == "/api/connect/callback":
        body = b""
        while True:
            message = await receive()
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break

        logger.info("Connect callback received: %s", body[:500])
        await respond(200, "application/json", '{"ok":true}')
        return

    # POST /stripe/webhook — Stripe webhook events
    if method == "POST" and path == "/stripe/webhook":
        body = b""
        while True:
            message = await receive()
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break

        # Extract Stripe-Signature header
        sig_header = ""
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"stripe-signature":
                sig_header = header_value.decode()
                break

        stripe.api_key = STRIPE_API_KEY
        status_code, response_body = await _process_stripe_webhook(body, sig_header)
        await respond(status_code, "application/json", response_body)
        return

    # GET /subscribed — success page after Stripe Checkout
    if method == "GET" and path == "/subscribed":
        topoff = params.get("type", [""])[0] == "topoff"
        if topoff:
            title = "Top-Off Complete!"
            msg = "Your bonus credits have been added. Redirecting back to Telegram..."
        else:
            title = "You're Subscribed!"
            msg = "Your plan is now active. Redirecting back to Telegram..."

        await respond(200, "text/html", SUBSCRIBED_HTML.format(
            title=title, message=msg))
        return

    # POST /meta/data-deletion — Meta Data Deletion Callback
    if method == "POST" and path == "/meta/data-deletion":
        body = b""
        while True:
            message = await receive()
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break

        if not FACEBOOK_APP_SECRET:
            logger.error("FACEBOOK_APP_SECRET not set — cannot process data deletion")
            await respond(500, "application/json", '{"error":"server misconfigured"}')
            return

        # Parse form-encoded body: signed_request=XXX
        from urllib.parse import parse_qs as _parse_qs
        form_data = _parse_qs(body.decode())
        signed_request = form_data.get("signed_request", [""])[0]

        if not signed_request:
            await respond(400, "application/json", '{"error":"missing signed_request"}')
            return

        from scripts.meta_data_deletion import (
            build_deletion_response,
            parse_signed_request,
        )

        payload = parse_signed_request(signed_request, FACEBOOK_APP_SECRET)
        if not payload:
            await respond(403, "application/json", '{"error":"invalid signature"}')
            return

        meta_user_id = str(payload.get("user_id", ""))
        logger.info("Meta data deletion request for user_id=%s", meta_user_id)

        response = build_deletion_response(meta_user_id)

        # Log deletion request for compliance tracking
        try:
            sb = _get_supabase()
            sb.table("data_deletion_requests").insert({
                "platform": "meta",
                "platform_user_id": meta_user_id,
                "confirmation_code": response["confirmation_code"],
            }).execute()
            logger.info("Logged Meta data deletion request for user_id=%s", meta_user_id)
        except Exception:
            logger.exception("Failed to log Meta deletion request for user_id=%s", meta_user_id)

        await respond(200, "application/json", json.dumps(response))
        return

    # Health check
    if method == "GET" and path == "/health":
        await respond(200, "application/json", '{"status":"ok"}')
        return

    # 404
    await respond(404, "text/html", ERROR_HTML.format(
        message="Page not found."))
