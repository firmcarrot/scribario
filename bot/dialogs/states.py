"""State groups for aiogram_dialog flows."""

from aiogram.fsm.state import State, StatesGroup


class OnboardingSG(StatesGroup):
    """Onboarding flow states for new users."""

    welcome = State()
    business_name = State()
    timezone = State()
    website_url = State()
    scraping = State()
    profile_review = State()
    logo_upload = State()
    tour = State()
    complete = State()


class BrandEditSG(StatesGroup):
    """Brand profile editing states."""

    waiting_for_value = State()


class CaptionEditSG(StatesGroup):
    """Caption editing dialog states."""

    waiting_for_edit_instruction = State()


class FeedbackSG(StatesGroup):
    """Feedback submission flow."""

    waiting_for_description = State()
