"""Telegram message builders — preview messages with inline buttons."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto


def build_preview_keyboard(draft_id: str) -> InlineKeyboardMarkup:
    """Build inline keyboard for draft approval/rejection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Approve", callback_data=f"approve:{draft_id}"),
                InlineKeyboardButton(text="Reject", callback_data=f"reject:{draft_id}"),
            ],
            [
                InlineKeyboardButton(text="Regenerate", callback_data=f"regen:{draft_id}"),
            ],
        ]
    )


def build_preview_caption(caption: str, platform_targets: list[str]) -> str:
    """Format a preview caption with platform targets."""
    platforms_str = ", ".join(p.title() for p in platform_targets)
    return (
        f"{caption}\n\n"
        f"<b>Posting to:</b> {platforms_str}\n\n"
        "<i>Tap Approve to post, Reject to skip, or Regenerate for new options.</i>"
    )


def build_multi_option_media_group(
    image_urls: list[str], captions: list[str]
) -> list[InputMediaPhoto]:
    """Build a media group for multiple image options."""
    media = []
    for i, (url, cap) in enumerate(zip(image_urls, captions, strict=False), 1):
        media.append(
            InputMediaPhoto(
                media=url,
                caption=f"<b>Option {i}:</b>\n{cap}" if i == 1 else f"<b>Option {i}:</b>\n{cap}",
                parse_mode="HTML",
            )
        )
    return media
