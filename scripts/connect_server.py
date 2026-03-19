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

import httpx
import jwt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config from environment
POSTIZ_URL = os.environ.get("POSTIZ_URL", "https://postiz.scribario.com")
POSTIZ_API_KEY = os.environ.get("POSTIZ_API_KEY", "")
POSTIZ_JWT_SECRET = os.environ.get("POSTIZ_JWT_SECRET", "")
SCRIBARIO_BASE_URL = os.environ.get("SCRIBARIO_BASE_URL", "https://connect.scribario.com")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

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
                message=f"Unknown platform: {platform}"))
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
        # Read request body
        body = b""
        while True:
            message = await receive()
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break

        logger.info("Connect callback received: %s", body[:500])
        await respond(200, "application/json", '{"ok":true}')
        return

    # Health check
    if method == "GET" and path == "/health":
        await respond(200, "application/json", '{"status":"ok"}')
        return

    # 404
    await respond(404, "text/html", ERROR_HTML.format(
        message="Page not found."))
