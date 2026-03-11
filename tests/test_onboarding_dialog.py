"""Tests for the aiogram_dialog onboarding flow — states and window definitions."""

from __future__ import annotations

import pytest

from bot.dialogs.states import OnboardingSG


class TestOnboardingStates:
    """Verify the onboarding state group has all required states."""

    def test_has_welcome_state(self):
        assert hasattr(OnboardingSG, "welcome")

    def test_has_business_name_state(self):
        assert hasattr(OnboardingSG, "business_name")

    def test_has_website_url_state(self):
        assert hasattr(OnboardingSG, "website_url")

    def test_has_scraping_state(self):
        assert hasattr(OnboardingSG, "scraping")

    def test_has_profile_review_state(self):
        assert hasattr(OnboardingSG, "profile_review")

    def test_has_complete_state(self):
        assert hasattr(OnboardingSG, "complete")


class TestOnboardingDialogImports:
    """Verify the onboarding dialog module can be imported."""

    def test_dialog_importable(self):
        from bot.dialogs.onboarding import dialog
        assert dialog is not None

    def test_dialog_is_dialog_type(self):
        from aiogram_dialog import Dialog
        from bot.dialogs.onboarding import dialog
        assert isinstance(dialog, Dialog)
