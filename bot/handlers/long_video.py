"""Telegram handler for /longvideo command."""

from __future__ import annotations

import logging
import time
from dataclasses import asdict

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from pipeline.long_video.models import LongVideoScript

logger = logging.getLogger(__name__)

router = Router(name="long_video")

# In-memory cooldown tracker: {tenant_id: last_request_timestamp}
_cooldowns: dict[str, float] = {}
COOLDOWN_SECONDS = 300  # 5 minutes


# ---------------------------------------------------------------------------
# Lazy imports for DB functions being built by another agent
# ---------------------------------------------------------------------------

async def get_tenant_by_telegram_user(telegram_user_id: int) -> dict | None:
    from bot.db import get_tenant_by_telegram_user as _fn
    return await _fn(telegram_user_id)


async def check_tenant_long_video_in_progress(tenant_id: str) -> bool:
    from bot.db import check_tenant_long_video_in_progress as _fn
    return await _fn(tenant_id)


async def create_video_project(
    tenant_id: str, intent: str, script_data: dict, status: str = "scripting",
    telegram_chat_id: int | None = None,
) -> dict:
    from bot.db import create_video_project as _fn
    return await _fn(
        tenant_id=tenant_id,
        intent=intent,
        script_data=script_data,
        status=status,
        telegram_chat_id=telegram_chat_id,
    )


async def get_video_project(project_id: str) -> dict | None:
    from bot.db import get_video_project as _fn
    return await _fn(project_id)


async def update_video_project_status(project_id: str, status: str) -> None:
    from bot.db import update_video_project_status as _fn
    await _fn(project_id, status)


async def update_video_project_script(project_id: str, script_data: dict) -> None:
    from bot.db import update_video_project_script as _fn
    await _fn(project_id, script_data)


async def enqueue_job(
    *, queue_name: str, job_type: str, payload: dict, idempotency_key: str,
) -> None:
    from bot.db import enqueue_job as _fn
    await _fn(
        queue_name=queue_name,
        job_type=job_type,
        payload=payload,
        idempotency_key=idempotency_key,
    )


async def load_brand_profile(tenant_id: str):  # type: ignore[no-untyped-def]
    from pipeline.brand_voice import load_brand_profile as _fn
    return await _fn(tenant_id)


async def generate_script(intent: str, profile: object) -> LongVideoScript:
    from pipeline.long_video.script_gen import generate_script as _fn
    return await _fn(intent, profile)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _format_script_preview(script: LongVideoScript) -> str:
    """Format a LongVideoScript into a human-readable Telegram preview."""
    lines: list[str] = []
    lines.append(f"\U0001f4dd Script Preview ({script.total_scenes} scenes, ~30s):\n")

    for scene in script.scenes:
        num = scene.index + 1
        lines.append(
            f"Scene {num}: {scene.visual_description} \u2192 {scene.camera_direction}"
        )

    lines.append("")
    lines.append("\U0001f399\ufe0f Voiceover preview:")
    if script.scenes:
        lines.append(f'"{script.scenes[0].voiceover_text}"')

    return "\n".join(lines)


def _build_keyboard(project_id: str) -> InlineKeyboardMarkup:
    """Build inline keyboard for script preview."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Generate Video",
                    callback_data=f"longvideo_approve:{project_id}",
                ),
                InlineKeyboardButton(
                    text="Cancel",
                    callback_data=f"longvideo_cancel:{project_id}",
                ),
                InlineKeyboardButton(
                    text="New Script",
                    callback_data=f"longvideo_rescript:{project_id}",
                ),
            ]
        ]
    )


# ---------------------------------------------------------------------------
# /longvideo command
# ---------------------------------------------------------------------------

@router.message(Command("longvideo"))
async def cmd_longvideo(message: Message) -> None:
    """Handle /longvideo command."""
    user = message.from_user
    if not user:
        return

    # Look up tenant
    membership = await get_tenant_by_telegram_user(user.id)
    if not membership:
        await message.answer(
            "You're not set up yet! Send /start to get started."
        )
        return

    tenant_id: str = membership["tenant_id"]

    # Extract intent from the command text
    raw = (message.text or "").strip()
    parts = raw.split(maxsplit=1)
    intent = parts[1].strip() if len(parts) > 1 else ""

    if not intent:
        await message.answer(
            "Please describe what you want the video to be about.\n"
            "Usage: /longvideo showcase our shrimp sauce"
        )
        return

    # Check concurrent in-progress
    if await check_tenant_long_video_in_progress(tenant_id):
        await message.answer(
            "Please wait for your current video to finish before starting a new one."
        )
        return

    # Check cooldown
    last_request = _cooldowns.get(tenant_id, 0.0)
    elapsed = time.time() - last_request
    if elapsed < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - elapsed)
        await message.answer(
            f"Please wait {remaining}s before requesting another video (cooldown)."
        )
        return

    # Load brand profile
    profile = await load_brand_profile(tenant_id)

    # Generate script
    await message.answer("Generating script... this takes a few seconds.")
    script = await generate_script(intent, profile)

    # Store in DB
    project = await create_video_project(
        tenant_id=tenant_id,
        intent=intent,
        script_data=asdict(script),
        status="scripting",
        telegram_chat_id=message.chat.id,
    )
    project_id: str = project["id"]

    # Update cooldown
    _cooldowns[tenant_id] = time.time()

    # Send preview
    preview_text = _format_script_preview(script)
    keyboard = _build_keyboard(project_id)
    await message.answer(preview_text, reply_markup=keyboard)


# ---------------------------------------------------------------------------
# Callback: validate project access
# ---------------------------------------------------------------------------

async def _validate_project_access(
    callback: CallbackQuery, project_id: str,
) -> dict | None:
    """Validate that the calling user owns the project's tenant. Returns project or None."""
    user = callback.from_user
    if not user:
        await callback.answer("Unknown user.")
        return None

    project = await get_video_project(project_id)
    if not project:
        await callback.answer("Project not found.")
        return None

    membership = await get_tenant_by_telegram_user(user.id)
    if not membership or membership["tenant_id"] != project["tenant_id"]:
        logger.warning(
            "Unauthorized video project access attempt",
            extra={"user_id": user.id, "project_id": project_id},
        )
        await callback.answer("You don't have access to this project.")
        return None

    return project


# ---------------------------------------------------------------------------
# Callback: approve
# ---------------------------------------------------------------------------

@router.callback_query(lambda c: c.data and c.data.startswith("longvideo_approve:"))
async def cb_longvideo_approve(callback: CallbackQuery) -> None:
    """User approved script — start video generation."""
    if not callback.data:
        return

    project_id = callback.data.split(":", 1)[1]
    project = await _validate_project_access(callback, project_id)
    if not project:
        return

    if project.get("status") != "scripting":
        await callback.answer("Already handled.")
        return

    await update_video_project_status(project_id, "approved")

    minute_bucket = int(time.time()) // 60
    await enqueue_job(
        queue_name="content_generation",
        job_type="generate_long_video",
        payload={
            "project_id": project_id,
            "tenant_id": project["tenant_id"],
            "telegram_chat_id": callback.message.chat.id if callback.message else None,
        },
        idempotency_key=f"{project_id}:generate_long_video:{minute_bucket}",
    )

    await callback.answer("Starting video generation...")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(
            "Starting video generation... this may take several minutes."
        )


# ---------------------------------------------------------------------------
# Callback: cancel
# ---------------------------------------------------------------------------

@router.callback_query(lambda c: c.data and c.data.startswith("longvideo_cancel:"))
async def cb_longvideo_cancel(callback: CallbackQuery) -> None:
    """User cancelled long video."""
    if not callback.data:
        return

    project_id = callback.data.split(":", 1)[1]
    project = await _validate_project_access(callback, project_id)
    if not project:
        return

    if project.get("status") != "scripting":
        await callback.answer("Already handled.")
        return

    await update_video_project_status(project_id, "failed")

    await callback.answer("Cancelled.")
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply("Video cancelled. Send /longvideo again anytime.")


# ---------------------------------------------------------------------------
# Callback: rescript
# ---------------------------------------------------------------------------

@router.callback_query(lambda c: c.data and c.data.startswith("longvideo_rescript:"))
async def cb_longvideo_rescript(callback: CallbackQuery) -> None:
    """User wants a new script."""
    if not callback.data:
        return

    project_id = callback.data.split(":", 1)[1]
    project = await _validate_project_access(callback, project_id)
    if not project:
        return

    if project.get("status") != "scripting":
        await callback.answer("Already handled.")
        return

    intent = project.get("intent", "")
    tenant_id = project["tenant_id"]

    profile = await load_brand_profile(tenant_id)
    script = await generate_script(intent, profile)

    await update_video_project_script(project_id, asdict(script))

    # Send new preview
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)

    preview_text = _format_script_preview(script)
    keyboard = _build_keyboard(project_id)

    if callback.message:
        await callback.message.reply(preview_text, reply_markup=keyboard)

    await callback.answer("New script generated!")
