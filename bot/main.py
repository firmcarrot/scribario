"""Scribario Telegram bot — entry point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram_dialog import setup_dialogs

from bot.config import get_settings
from bot.dialogs.onboarding import dialog as onboarding_dialog
from bot.handlers import approval, autopilot, billing, caption_edit, commands, intake, library, logo, onboarding, photos

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    """Create and configure the Telegram bot instance."""
    return Bot(
        token=get_settings().telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Create dispatcher and register all routers."""
    redis_url = get_settings().redis_url
    storage = RedisStorage.from_url(
        redis_url,
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    dp = Dispatcher(storage=storage)
    dp.include_router(commands.router)    # commands first
    dp.include_router(billing.router)    # /subscribe, /billing, /upgrade — before intake
    dp.include_router(autopilot.router)   # /autopilot, /pause, /resume — before intake
    # long_video router removed — short-form video is now inline in generate_content
    dp.include_router(logo.router)        # /logo command + photo capture
    dp.include_router(caption_edit.router)  # FSM edit state — before approval/intake
    dp.include_router(onboarding.router)
    dp.include_router(onboarding_dialog)
    dp.include_router(photos.router)      # photo handler before intake
    dp.include_router(library.router)     # /library command — before intake catch-all
    dp.include_router(approval.router)
    dp.include_router(intake.router)      # intake last — catches free-text
    setup_dialogs(dp)
    return dp


async def main() -> None:
    """Start the bot with long-polling."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Scribario bot...")

    bot = create_bot()
    dp = create_dispatcher()

    # Drop pending updates on startup to avoid processing stale messages
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
