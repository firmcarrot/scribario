"""Intake handler — processes free-text content requests."""

from __future__ import annotations

import logging
import re
from datetime import datetime

import dateparser
import dateparser.search
from aiogram import F, Router
from aiogram.types import Message

from bot.db import create_content_request, enqueue_job, get_tenant_by_telegram_user
from bot.handlers.photos import _pending_post_photos
from pipeline.prompt_engine.intake import IntakeAction, check_intake

logger = logging.getLogger(__name__)

router = Router(name="intake")

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


def parse_scheduled_time(text: str) -> datetime | None:
    """Return a datetime if the text contains scheduling intent, else None.

    Uses dateparser.search.search_dates to detect phrases like "post this Friday
    at 9am", "schedule for tomorrow noon", "send on Monday".
    Returns None if no scheduling intent is detected.
    """
    if not _SCHEDULE_TRIGGERS.search(text):
        return None

    settings: dict = {
        "PREFER_DATES_FROM": "future",
        "RETURN_AS_TIMEZONE_AWARE": False,
    }
    matches = dateparser.search.search_dates(text, settings=settings)
    if matches:
        # Return the first detected datetime
        return matches[0][1]
    return None


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

    # --- Intake Agent: check if we need clarification before generating ---
    try:
        intake_result = await check_intake(raw_intent, tenant_id)
        if intake_result.action != IntakeAction.PROCEED:
            await message.answer(intake_result.message or "Could you tell me more about what you'd like?")
            return
    except Exception:
        logger.warning("Intake agent check failed, proceeding anyway", exc_info=True)

    # --- Feature 3: Scheduling ---
    scheduled_time = parse_scheduled_time(raw_intent)
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
        f"\n\nI'll post this on <b>{scheduled_time.strftime('%A, %B %-d at %-I:%M %p')}</b>."
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
