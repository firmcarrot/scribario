"""Job handler — long-form video generation pipeline."""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import os

from bot.config import get_settings
from bot.db import get_video_project, log_usage_event, update_video_project_status
from pipeline.long_video import run_pipeline

logger = logging.getLogger(__name__)


async def handle_generate_long_video(message: dict) -> None:
    """Generate a long-form video.

    Message format:
        {
            "project_id": "uuid",
            "tenant_id": "uuid",
            "telegram_chat_id": 12345,
        }
    """
    project_id = message["project_id"]
    tenant_id = message["tenant_id"]
    telegram_chat_id = message.get("telegram_chat_id")

    logger.info(
        "Long video generation started",
        extra={"project_id": project_id, "tenant_id": tenant_id},
    )

    try:
        # Load the project to get intent and aspect_ratio
        project = await get_video_project(project_id)
        if project is None:
            raise RuntimeError(f"Video project {project_id} not found")

        intent = project.get("intent", "")
        aspect_ratio = project.get("aspect_ratio", "16:9")

        # Build a status callback that updates DB
        async def status_callback(status: str, status_message: str = "") -> None:
            await update_video_project_status(project_id, status)

        # Run the full pipeline (script -> TTS -> frames -> clips -> stitch)
        pipeline_result = await run_pipeline(
            project_id=project_id,
            tenant_id=tenant_id,
            intent=intent,
            aspect_ratio=aspect_ratio,
            status_callback=status_callback,
        )

        # Upload final video to Supabase Storage
        video_url = _upload_to_storage(
            output_path=pipeline_result.video_path,
            project_id=project_id,
            tenant_id=tenant_id,
        )

        # Log total cost
        await log_usage_event(
            tenant_id=tenant_id,
            event_type="long_video_generation",
            provider="multi",
            cost_usd=pipeline_result.total_cost_usd,
            metadata={
                "project_id": project_id,
                "duration_seconds": pipeline_result.duration_seconds,
                "scene_count": pipeline_result.scene_count,
                "scenes_completed": pipeline_result.scenes_completed,
            },
        )

        # Clean up the output file now that it's uploaded
        try:
            os.remove(pipeline_result.video_path)
        except OSError:
            pass

        # Update project with final URL and status
        await update_video_project_status(
            project_id, "preview_ready", final_video_url=video_url
        )

        logger.info(
            "Long video generation complete",
            extra={"project_id": project_id, "video_url": video_url},
        )

        # Send preview to Telegram — use generated caption if available
        if telegram_chat_id:
            preview_caption = intent
            if pipeline_result.captions:
                preview_caption = pipeline_result.captions[0].get("text", intent)

            await _send_video_preview(
                chat_id=telegram_chat_id,
                project_id=project_id,
                video_url=video_url,
                caption=preview_caption,
            )

    except Exception as exc:
        logger.exception(
            "Long video generation failed",
            extra={"project_id": project_id},
        )
        await update_video_project_status(
            project_id, "failed", error_message=str(exc)
        )
        if telegram_chat_id:
            await _send_error_message(
                chat_id=telegram_chat_id,
                project_id=project_id,
                error=str(exc),
            )


def _upload_to_storage(
    output_path: str,
    project_id: str,
    tenant_id: str,
) -> str:
    """Upload the final stitched video to Supabase Storage and return the public URL."""
    from bot.db import get_supabase_client

    client = get_supabase_client()
    storage_path = f"long-videos/{tenant_id}/{project_id}.mp4"

    with open(output_path, "rb") as f:
        video_bytes = f.read()

    client.storage.from_("long-videos").upload(
        storage_path,
        video_bytes,
        file_options={"content-type": "video/mp4", "upsert": "true"},
    )

    # Get public URL
    url_response = client.storage.from_("long-videos").get_public_url(storage_path)
    return url_response


def _build_video_keyboard(project_id: str) -> InlineKeyboardMarkup:
    """Build inline keyboard for long video approval."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Approve Video",
                    callback_data=f"approve_long_video:{project_id}",
                ),
                InlineKeyboardButton(
                    text="Reject Video",
                    callback_data=f"reject_long_video:{project_id}",
                ),
            ],
        ]
    )


async def _send_video_preview(
    chat_id: int,
    project_id: str,
    video_url: str,
    caption: str,
) -> None:
    """Send long video preview to Telegram with approve/reject buttons."""
    settings = get_settings()
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    try:
        caption = f"<b>Long video preview:</b>\n{caption}" if caption else "Long video preview"
        if len(caption) > 1020:
            caption = caption[:1017] + "..."

        keyboard = _build_video_keyboard(project_id)

        await bot.send_video(
            chat_id=chat_id,
            video=video_url,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
        logger.info(
            "Long video preview sent",
            extra={"project_id": project_id, "chat_id": chat_id},
        )
    except Exception:
        logger.exception(
            "Failed to send long video preview",
            extra={"project_id": project_id, "chat_id": chat_id},
        )
    finally:
        await bot.session.close()


async def _send_error_message(
    chat_id: int,
    project_id: str,
    error: str,
) -> None:
    """Send error notification to Telegram when video generation fails."""
    settings = get_settings()
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"Video generation failed.\n\n"
                f"<b>Error:</b> {error[:500]}\n\n"
                f"Please try again or contact support."
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        logger.exception(
            "Failed to send error message",
            extra={"project_id": project_id, "chat_id": chat_id},
        )
    finally:
        await bot.session.close()
