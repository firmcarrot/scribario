"""Intake handler — processes free-text content requests."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import dateparser
import dateparser.search
from aiogram import F, Router
from aiogram.types import Message

from bot.db import create_content_request, enqueue_job, get_tenant_by_telegram_user
from bot.handlers.photos import _pending_post_photos
from pipeline.prompt_engine.intake import IntakeAction, check_intake

logger = logging.getLogger(__name__)

router = Router(name="intake")

# --- Rate limiting ---
# In-memory rate limiter: user_id → list of timestamps
# Capped at 10k users to prevent unbounded growth. Oldest entries evicted on overflow.
_rate_limiter: dict[int, list[float]] = {}
_RATE_LIMITER_MAX_USERS = 10_000
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 5  # max requests per window


def _check_rate_limit(user_id: int) -> bool:
    """Return True if user is within rate limit, False if exceeded."""
    now = datetime.now(timezone.utc).timestamp()
    if user_id not in _rate_limiter:
        # Evict oldest users if at capacity
        if len(_rate_limiter) >= _RATE_LIMITER_MAX_USERS:
            oldest_key = next(iter(_rate_limiter))
            del _rate_limiter[oldest_key]
        _rate_limiter[user_id] = []

    # Evict entries outside the window
    _rate_limiter[user_id] = [
        t for t in _rate_limiter[user_id] if now - t < RATE_LIMIT_WINDOW
    ]

    if len(_rate_limiter[user_id]) >= RATE_LIMIT_MAX:
        return False

    _rate_limiter[user_id].append(now)
    return True


def truncate_telegram_caption(text: str, max_bytes: int = 1024) -> str:
    """Truncate text to fit within Telegram's caption byte limit.

    Telegram captions are limited to 1024 bytes (UTF-8). This truncates
    by character while checking byte length to avoid splitting multi-byte chars.
    """
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text

    suffix = "..."
    suffix_bytes = len(suffix.encode("utf-8"))
    target = max_bytes - suffix_bytes

    # Linear scan from end — fast enough for caption-length strings
    for i in range(len(text), 0, -1):
        if len(text[:i].encode("utf-8")) <= target:
            return text[:i] + suffix
    return suffix

# Patterns: each maps a regex (case-insensitive, word-boundary) to a canonical platform name.
# The \bX\b pattern is case-sensitive (no IGNORECASE) to avoid matching lowercase "x".
_PLATFORM_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bfacebook\b", re.IGNORECASE), "facebook"),
    (re.compile(r"\binstagram\b", re.IGNORECASE), "instagram"),
    (re.compile(r"\blinkedin\b", re.IGNORECASE), "linkedin"),
    (re.compile(r"\btwitter\b", re.IGNORECASE), "twitter"),
    (re.compile(r"\bX\b"), "twitter"),  # Capital X only — avoid false-positives on "x"
    (re.compile(r"\btiktok\b", re.IGNORECASE), "tiktok"),
]


def parse_platform_targets(text: str) -> list[str] | None:
    """Detect platform mentions in text and return canonical platform names.

    Returns a deduplicated list of matched platforms, or None if no platforms
    were detected (callers should treat None as "post to all connected").
    """
    found: list[str] = []
    for pattern, platform in _PLATFORM_PATTERNS:
        if pattern.search(text) and platform not in found:
            found.append(platform)
    return found if found else None


# Scheduling trigger phrases — signal that dateparser should parse the whole text
_SCHEDULE_TRIGGERS = re.compile(
    r"\b(post|send|schedule|publish|share)\s+(this|on|for|next)?\s*"
    r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"tomorrow|today|tonight|noon|midnight|morning|evening|afternoon|"
    r"next\s+week|at\s+\d)",
    re.IGNORECASE,
)

# Style keyword mappings
_STYLE_MAP: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(cartoon|illustrated|animated)\b", re.IGNORECASE), "cartoon"),
    (re.compile(r"\b(cinematic|dramatic)\b", re.IGNORECASE), "cinematic"),
    (re.compile(r"\b(watercolor|painted)\b", re.IGNORECASE), "watercolor"),
    (re.compile(r"\b(photorealistic|realistic)\b", re.IGNORECASE), "photorealistic"),
]


def parse_scheduled_time(
    text: str, tenant_timezone: str | None = None
) -> datetime | None:
    """Return a UTC datetime if the text contains scheduling intent, else None.

    Uses dateparser.search.search_dates to detect phrases like "post this Friday
    at 9am", "schedule for tomorrow noon", "send on Monday".

    When tenant_timezone is provided (e.g. "America/New_York"), the parsed time
    is interpreted in that timezone and converted to UTC. Without it, the server's
    local time is used and converted to UTC.

    Always returns a timezone-aware UTC datetime or None.
    """
    if not _SCHEDULE_TRIGGERS.search(text):
        return None

    settings: dict = {
        "PREFER_DATES_FROM": "future",
        "RETURN_AS_TIMEZONE_AWARE": False,
    }
    if tenant_timezone:
        settings["TIMEZONE"] = tenant_timezone

    matches = dateparser.search.search_dates(text, settings=settings)
    if not matches:
        return None

    parsed_dt = matches[0][1]

    # dateparser returns a naive datetime in the tenant's timezone (or server local).
    # Attach the tenant timezone, then convert to UTC.
    # Note: replace(tzinfo=ZoneInfo(...)) works correctly for ZoneInfo in Python 3.9+
    # except during DST fall-back "fold" ambiguity, where it picks the first occurrence
    # (summer time), which is the expected user behavior.
    tz: ZoneInfo | None = None
    if tenant_timezone:
        try:
            tz = ZoneInfo(tenant_timezone)
        except (KeyError, Exception):
            logger.warning("Invalid tenant timezone %s, falling back to UTC", tenant_timezone)
    if parsed_dt.tzinfo is None:
        if tz:
            parsed_dt = parsed_dt.replace(tzinfo=tz)
        else:
            # No tenant timezone — assume server local, make UTC
            parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)

    # Convert to UTC
    return parsed_dt.astimezone(timezone.utc)


def format_scheduled_time_for_user(
    utc_dt: datetime, tenant_timezone: str | None = None
) -> str:
    """Format a UTC datetime for display in the user's local timezone.

    Returns a human-readable string like "Friday, March 20 at 3:00 PM EDT".
    """
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)

    if tenant_timezone:
        try:
            tz = ZoneInfo(tenant_timezone)
            local_dt = utc_dt.astimezone(tz)
        except (KeyError, Exception):
            logger.warning("Invalid timezone %s in format_scheduled_time_for_user", tenant_timezone)
            local_dt = utc_dt
    else:
        local_dt = utc_dt

    # Format with timezone abbreviation
    return local_dt.strftime("%A, %B %-d at %-I:%M %p %Z")


def _strip_scheduling_language(text: str) -> str:
    """Remove scheduling trigger phrases from intent text."""
    cleaned = re.sub(
        r"\b(post|send|schedule|publish|share)\s+(this|on|for|next)?\s*"
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
        r"tomorrow|today|tonight|noon|midnight|morning|evening|afternoon)"
        r"(\s+at\s+[\d:apm]+)?",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = cleaned.strip(" ,;.\u2014\u2013-")
    return cleaned if cleaned else text


_VIDEO_KEYWORDS = re.compile(
    r"\b(video|reel|clip|animate|animation|motion)\b", re.IGNORECASE
)

_VERTICAL_VIDEO_KEYWORDS = re.compile(
    r"\b(reel|reels|story|stories|tiktok|shorts)\b", re.IGNORECASE
)


def detect_video_request(text: str) -> bool:
    """Return True if the text contains video-related keywords."""
    return bool(_VIDEO_KEYWORDS.search(text))


def parse_video_aspect_ratio(text: str) -> str:
    """Return "9:16" for vertical video keywords (reel, story, tiktok, shorts), else "16:9"."""
    if _VERTICAL_VIDEO_KEYWORDS.search(text):
        return "9:16"
    return "16:9"


def parse_style_override(text: str) -> str | None:
    """Return a style string if a style keyword is found in text, else None.

    Mappings:
        cartoon | illustrated | animated  → "cartoon"
        cinematic | dramatic              → "cinematic"
        watercolor | painted              → "watercolor"
        photorealistic | realistic        → "photorealistic"
    """
    for pattern, style in _STYLE_MAP:
        if pattern.search(text):
            return style
    return None


@router.message(F.text)
async def handle_content_request(message: Message) -> None:
    """Handle free-text messages as content creation requests.

    Flow: user message → look up tenant → create content_request → enqueue generation → ack.
    """
    user = message.from_user
    if not user or not message.text:
        return

    raw_intent = message.text.strip()

    # Rate limit check
    if not _check_rate_limit(user.id):
        await message.answer(
            "You're sending requests too quickly. "
            "Please wait a minute before trying again."
        )
        return

    # Look up tenant for this Telegram user
    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer(
            "You're not connected to any brand yet.\n"
            "Use /start to set up your account."
        )
        return

    # Guard: incomplete onboarding
    if membership.get("onboarding_status") != "complete":
        await message.answer(
            "Looks like you haven't finished setting up yet. "
            "Use /start to complete your profile."
        )
        return

    tenant_id = membership["tenant_id"]
    tenant_data = membership.get("tenants") or {}
    tenant_timezone: str | None = tenant_data.get("timezone") if isinstance(tenant_data, dict) else None

    # --- Intake Agent: check if we need clarification before generating ---
    try:
        intake_result = await check_intake(raw_intent, tenant_id)
        if intake_result.action != IntakeAction.PROCEED:
            await message.answer(intake_result.message or "Could you tell me more about what you'd like?")
            return
    except Exception:
        logger.warning("Intake agent check failed, proceeding anyway", exc_info=True)

    # --- Feature 3: Scheduling (timezone-aware) ---
    scheduled_time = parse_scheduled_time(raw_intent, tenant_timezone=tenant_timezone)
    intent = _strip_scheduling_language(raw_intent) if scheduled_time else raw_intent

    # --- Feature 4: Style override ---
    style_override = parse_style_override(raw_intent)

    # --- Feature 5: Video detection ---
    is_video = detect_video_request(raw_intent)
    video_aspect_ratio = parse_video_aspect_ratio(raw_intent) if is_video else None

    logger.info(
        "Content request received",
        extra={
            "user_id": user.id,
            "tenant_id": tenant_id,
            "intent": intent[:100],
            "scheduled_time": scheduled_time.isoformat() if scheduled_time else None,
            "style_override": style_override,
            "is_video": is_video,
        },
    )

    # Detect any platform mentions in the intent; None means "all connected"
    platform_targets = parse_platform_targets(intent)

    # Create content request in database
    request = await create_content_request(
        tenant_id=tenant_id,
        intent=intent,
        platform_targets=platform_targets,
        due_at=scheduled_time,
        style_override=style_override,
        generate_video=is_video,
        video_aspect_ratio=video_aspect_ratio,
    )
    request_id = request["id"]

    # Check if user has a pending photo from "Create a Post" tap
    pending_photo = _pending_post_photos.pop(user.id, None)
    new_photo_storage_paths = [pending_photo["storage_path"]] if pending_photo else []

    # Enqueue generation job
    payload: dict = {
        "request_id": request_id,
        "tenant_id": tenant_id,
        "intent": intent,
        "platform_targets": platform_targets,
        "telegram_chat_id": message.chat.id,
    }
    if new_photo_storage_paths:
        payload["new_photo_storage_paths"] = new_photo_storage_paths
    if style_override:
        payload["style_override"] = style_override
    if is_video:
        payload["generate_video"] = True
        payload["video_aspect_ratio"] = video_aspect_ratio

    await enqueue_job(
        queue_name="content_generation",
        job_type="generate_content",
        payload=payload,
        idempotency_key=f"{request_id}:generate_content",
        scheduled_for=scheduled_time,
    )

    photo_note = " I'll use your photo as a reference." if pending_photo else ""
    schedule_note = (
        f"\n\nI'll post this on <b>{format_scheduled_time_for_user(scheduled_time, tenant_timezone)}</b>."
        if scheduled_time
        else ""
    )
    video_note = " I'll also generate a video." if is_video else ""
    time_note = "1-3 minutes" if is_video else "30-60 seconds"

    await message.answer(
        "Got it! I'm generating content for:\n\n"
        f"<i>{intent}</i>\n\n"
        f"This usually takes about {time_note}.{photo_note}{video_note} "
        f"I'll send you a preview with options to approve.{schedule_note}",
        parse_mode="HTML",
    )


@router.message()
async def handle_unsupported_message(message: Message) -> None:
    """Catch-all for unsupported message types (stickers, voice, documents, etc.).

    Registered last so it only fires when no other handler matches.
    """
    user = message.from_user
    if not user:
        return

    content_type = message.content_type or "unknown"
    logger.info(
        "Unsupported message type received",
        extra={"user_id": user.id, "content_type": content_type},
    )

    await message.answer(
        "I can only process text messages and photos right now.\n\n"
        "Try typing what you'd like to post, like:\n"
        '<i>"Post about our weekend special"</i>\n\n'
        "Or send a photo with a caption to use it as creative direction.\n"
        "Type /help for a full list of features.",
        parse_mode="HTML",
    )
