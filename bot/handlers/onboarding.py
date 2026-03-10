"""Onboarding handler — /start command and new user registration."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="onboarding")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start — welcome message and registration check."""
    user = message.from_user
    if not user:
        return

    # TODO: Check if user exists in tenant_members table
    # If yes → welcome back
    # If no → start brand profile setup flow

    await message.answer(
        f"Welcome to <b>Scribario</b>, {user.first_name}!\n\n"
        "I create and post social media content for your business.\n\n"
        "Just tell me what you want to post, like:\n"
        '<i>"Post about our new ghost pepper sauce launching Friday"</i>\n\n'
        "I'll generate images and captions, send you a preview, "
        "and post to your platforms when you approve.\n\n"
        "Let's get started! Send me a message about what you'd like to post."
    )
