"""Telegram message builders — preview messages with inline buttons."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto


def build_preview_keyboard(draft_id: str, num_options: int = 3) -> InlineKeyboardMarkup:
    """Build inline keyboard with per-option approve + edit buttons + reject/regen."""
    # One approve button per option
    option_buttons = [
        InlineKeyboardButton(
            text=f"Approve #{i}",
            callback_data=f"approve:{draft_id}:{i}",
        )
        for i in range(1, num_options + 1)
    ]

    # One edit button per option
    edit_buttons = [
        InlineKeyboardButton(text=f"✏️ Edit #{i}", callback_data=f"edit:{draft_id}:{i}")
        for i in range(1, num_options + 1)
    ]

    # One regen-image button per option
    regen_image_buttons = [
        InlineKeyboardButton(
            text=f"🖼️ New Image #{i}", callback_data=f"regen_image:{draft_id}:{i}"
        )
        for i in range(1, num_options + 1)
    ]

    # Video button
    video_buttons = [
        InlineKeyboardButton(
            text="Make Video",
            callback_data=f"make_video:{draft_id}",
        ),
    ]

    # Reject and regenerate all
    action_buttons = [
        InlineKeyboardButton(text="Reject All", callback_data=f"reject:{draft_id}"),
        InlineKeyboardButton(text="Regenerate", callback_data=f"regen:{draft_id}"),
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            option_buttons,
            edit_buttons,
            regen_image_buttons,
            video_buttons,
            action_buttons,
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
                caption=f"<b>Option {i}:</b>\n{cap}",
                parse_mode="HTML",
            )
        )
    return media
