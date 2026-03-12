"""State groups for aiogram_dialog flows."""

from aiogram.fsm.state import State, StatesGroup


class OnboardingSG(StatesGroup):
    """Onboarding flow states for new users."""

    welcome = State()
    business_name = State()
    website_url = State()
    scraping = State()
    profile_review = State()
    complete = State()


class CaptionEditSG(StatesGroup):
    """Caption editing dialog states."""

    waiting_for_edit_instruction = State()
