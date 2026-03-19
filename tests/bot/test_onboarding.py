"""Tests for onboarding battle-hardening: 5 gaps + pre-existing bug fix.

Tests cover:
- Gap 1: Skip website option
- Gap 2: Few-shot example seeding
- Gap 3: Platform connection prompt after completion
- Gap 4: Intake guard for incomplete onboarding + /start relaunch
- Gap 5: /brand placeholder command
- Pre-existing bug: error fallback updates onboarding_status
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.brand_gen import GeneratedBrandProfile, generate_starter_examples


# --- Gap 4: Intake guard ---


class TestIntakeOnboardingGuard:
    """Gap 4a: Intake handler blocks users with incomplete onboarding."""

    @pytest.mark.asyncio
    async def test_intake_blocks_pending_onboarding(self):
        """Free-text from user with onboarding_status != 'complete' gets redirect."""
        from bot.handlers.intake import handle_content_request

        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.text = "Post about our sauce"

        membership = {
            "tenant_id": "t1",
            "role": "owner",
            "onboarding_status": "pending",
            "tenants": {"id": "t1", "name": "Test", "slug": "test"},
        }

        with patch("bot.handlers.intake.get_tenant_by_telegram_user", return_value=membership):
            await handle_content_request(message)

        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        assert "/start" in call_text
        assert "finished setting up" in call_text

    @pytest.mark.asyncio
    async def test_intake_allows_complete_onboarding(self):
        """Free-text from user with onboarding_status == 'complete' proceeds normally."""
        from bot.handlers.intake import handle_content_request

        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.text = "Post about our sauce"
        message.chat = MagicMock(id=456)

        membership = {
            "tenant_id": "t1",
            "role": "owner",
            "onboarding_status": "complete",
            "tenants": {"id": "t1", "name": "Test", "slug": "test"},
        }

        with (
            patch("bot.handlers.intake.get_tenant_by_telegram_user", return_value=membership),
            patch("bot.handlers.intake.create_content_request", return_value={"id": "cr1"}),
            patch("bot.handlers.intake.enqueue_job", return_value={"id": "j1"}),
            patch("bot.handlers.intake.check_intake",
                  new_callable=AsyncMock,
                  return_value=MagicMock(action="proceed")),
            patch("bot.handlers.intake._pending_post_photos", {}),
            patch("bot.services.rate_limiter.is_rate_limited",
                  new_callable=AsyncMock, return_value=False),
            patch("bot.services.budget.check_can_generate",
                  new_callable=AsyncMock, return_value=(True, "")),
            patch("bot.services.budget.check_can_generate_video",
                  new_callable=AsyncMock, return_value=(True, "")),
            patch("bot.services.budget.increment_post_count",
                  new_callable=AsyncMock),
        ):
            await handle_content_request(message)

        # Should have called answer with "Got it!" (not the guard message)
        call_text = message.answer.call_args[0][0]
        assert "Got it!" in call_text


class TestPhotosOnboardingGuard:
    """Gap 4 (I1): Photos handler also guards against incomplete onboarding."""

    @pytest.mark.asyncio
    async def test_photo_blocks_pending_onboarding(self):
        from bot.handlers.photos import handle_photo_message

        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.photo = [MagicMock(file_unique_id="abc", file_id="def")]
        message.media_group_id = None
        message.caption = None
        message.text = None

        membership = {
            "tenant_id": "t1",
            "role": "owner",
            "onboarding_status": "pending",
        }

        bot = AsyncMock()

        with patch("bot.handlers.photos.get_tenant_by_telegram_user", return_value=membership):
            await handle_photo_message(message, bot)

        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        assert "/start" in call_text


class TestCmdStartIncompleteOnboarding:
    """Gap 4b: /start relaunches dialog for users with incomplete onboarding."""

    @pytest.mark.asyncio
    async def test_start_relaunches_for_incomplete(self):
        from bot.handlers.onboarding import cmd_start

        message = AsyncMock()
        message.from_user = MagicMock(id=123, first_name="Ron")
        dialog_manager = AsyncMock()

        membership = {
            "tenant_id": "t1",
            "role": "owner",
            "onboarding_status": "pending",
            "tenants": {"id": "t1", "name": "Test", "slug": "test"},
        }

        with patch("bot.handlers.onboarding.get_tenant_by_telegram_user", return_value=membership):
            await cmd_start(message, dialog_manager)

        # Should start dialog, not send "welcome back"
        dialog_manager.start.assert_called_once()
        message.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_welcomes_back_complete_user(self):
        from bot.handlers.onboarding import cmd_start

        message = AsyncMock()
        message.from_user = MagicMock(id=123, first_name="Ron")
        dialog_manager = AsyncMock()

        membership = {
            "tenant_id": "t1",
            "role": "owner",
            "onboarding_status": "complete",
            "tenants": {"id": "t1", "name": "Test Brand", "slug": "test"},
        }

        with patch("bot.handlers.onboarding.get_tenant_by_telegram_user", return_value=membership):
            await cmd_start(message, dialog_manager)

        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        assert "Welcome back" in call_text
        assert "Test Brand" in call_text
        dialog_manager.start.assert_not_called()


# --- Gap 1: Skip website ---


class TestEnsureTenant:
    """_ensure_tenant helper creates tenant + member, reuses existing."""

    @pytest.mark.asyncio
    async def test_creates_new_tenant_and_member(self):
        from bot.dialogs.onboarding import _ensure_tenant

        manager = MagicMock()
        manager.dialog_data = {"business_name": "Test Biz"}
        user = MagicMock(id=123)

        with (
            patch("bot.db.create_tenant", return_value={"id": "t-new"}) as mock_ct,
            patch("bot.db.create_tenant_member", return_value={}) as mock_cm,
        ):
            result = await _ensure_tenant(manager, user)

        assert result == "t-new"
        assert manager.dialog_data["tenant_id"] == "t-new"

    @pytest.mark.asyncio
    async def test_reuses_existing_tenant(self):
        from bot.dialogs.onboarding import _ensure_tenant

        manager = MagicMock()
        manager.dialog_data = {"business_name": "Test", "tenant_id": "t-existing"}
        user = MagicMock(id=123)

        result = await _ensure_tenant(manager, user)
        assert result == "t-existing"


class TestOnSkipWebsite:
    """Gap 1: Skip website button creates tenant with basic profile."""

    @pytest.mark.asyncio
    async def test_skip_creates_tenant_and_basic_profile(self):
        from bot.dialogs.onboarding import on_skip_website

        callback = AsyncMock()
        callback.from_user = MagicMock(id=123)
        button = MagicMock()
        manager = AsyncMock()
        manager.dialog_data = {"business_name": "No Website Biz"}

        with (
            patch("bot.db.create_tenant", return_value={"id": "t-skip"}),
            patch("bot.db.create_tenant_member", return_value={}),
            patch("bot.db.upsert_brand_profile") as mock_upsert,
            patch("bot.db.update_onboarding_status") as mock_status,
            patch("asyncio.create_task"),
        ):
            await on_skip_website(callback, button, manager)

        mock_upsert.assert_called_once()
        profile_data = mock_upsert.call_args[0][1]
        assert "professional" in profile_data["tone_words"]

        mock_status.assert_called_once_with("t-skip", 123, "complete")
        manager.switch_to.assert_called_once()


# --- Gap 2: Few-shot seeding ---


class TestSeedFewShotExamples:
    """Gap 2: Fire-and-forget few-shot seeding."""

    @pytest.mark.asyncio
    async def test_seed_with_profile(self):
        from bot.dialogs.onboarding import _seed_few_shot_examples

        profile = GeneratedBrandProfile(
            name="Test Brand",
            tone_words=["bold"],
            audience_description="Foodies",
            do_list=["Be fun"],
            dont_list=["Be boring"],
        )

        with (
            patch(
                "pipeline.brand_gen.generate_starter_examples",
                return_value=[
                    {"platform": "facebook", "content_type": "product_highlight", "caption": "Test"},
                ],
            ) as mock_gen,
            patch("bot.db.create_few_shot_examples_batch", return_value=[{}]) as mock_batch,
        ):
            await _seed_few_shot_examples("t1", "Test Brand", profile=profile)

        mock_gen.assert_called_once()
        mock_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_seed_without_profile(self):
        """Skip-website path: no profile, just business name."""
        from bot.dialogs.onboarding import _seed_few_shot_examples

        with (
            patch(
                "pipeline.brand_gen.generate_starter_examples",
                return_value=[
                    {"platform": "facebook", "content_type": "general", "caption": "Test"},
                ],
            ) as mock_gen,
            patch("bot.db.create_few_shot_examples_batch", return_value=[{}]) as mock_batch,
        ):
            await _seed_few_shot_examples("t1", "My Biz", profile=None)

        mock_gen.assert_called_once_with(profile=None, business_name="My Biz")
        mock_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_seed_handles_errors_gracefully(self):
        """Errors are logged but don't crash."""
        from bot.dialogs.onboarding import _seed_few_shot_examples

        with patch(
            "pipeline.brand_gen.generate_starter_examples",
            side_effect=RuntimeError("API down"),
        ):
            # Should not raise
            await _seed_few_shot_examples("t1", "Test", profile=None)


class TestGenerateStarterExamples:
    """Gap 2: generate_starter_examples in brand_gen.py."""

    def test_is_async(self):
        assert asyncio.iscoroutinefunction(generate_starter_examples)

    @pytest.mark.asyncio
    async def test_returns_examples_with_profile(self):
        profile = GeneratedBrandProfile(
            name="Test",
            tone_words=["bold"],
            audience_description="Foodies",
            do_list=[],
            dont_list=[],
            tagline="Stay hungry",
        )

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='[{"content_type": "product_highlight", "caption": "Check this out!"}]')]

        with patch("pipeline.brand_gen.anthropic.AsyncAnthropic") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.messages.create.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = await generate_starter_examples(profile=profile, business_name="Test")

        # Should duplicate for facebook and instagram
        assert len(result) == 2
        assert result[0]["platform"] == "facebook"
        assert result[1]["platform"] == "instagram"
        assert result[0]["caption"] == "Check this out!"

    @pytest.mark.asyncio
    async def test_returns_empty_on_bad_json(self):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="not json")]

        with patch("pipeline.brand_gen.anthropic.AsyncAnthropic") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.messages.create.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = await generate_starter_examples(profile=None, business_name="Test")

        assert result == []

    @pytest.mark.asyncio
    async def test_accepts_none_profile(self):
        """Skip-website path: profile=None falls back to business name."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='[{"content_type": "brand_story", "caption": "Hi!"}]')]

        with patch("pipeline.brand_gen.anthropic.AsyncAnthropic") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.messages.create.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = await generate_starter_examples(profile=None, business_name="My Biz")

        assert len(result) == 2


# --- Gap 3: Platform connection prompt ---


class TestOnConnectPlatforms:
    """Gap 3: Connect platforms button closes dialog and sends OAuth buttons."""

    @pytest.mark.asyncio
    async def test_connect_platforms_closes_dialog_and_sends_buttons(self):
        from bot.dialogs.onboarding import on_connect_platforms

        callback = AsyncMock()
        callback.from_user = MagicMock(id=123)
        callback.message = MagicMock()
        callback.message.chat.id = 456
        callback.bot = AsyncMock()

        button = MagicMock()
        manager = AsyncMock()

        with patch("bot.handlers.onboarding.send_platform_buttons") as mock_send:
            await on_connect_platforms(callback, button, manager)

        manager.done.assert_called_once()
        mock_send.assert_called_once_with(callback.bot, 456)


class TestSendPlatformButtons:
    """Gap 3: send_platform_buttons helper uses bot.send_message."""

    @pytest.mark.asyncio
    async def test_sends_buttons_via_bot(self):
        from bot.handlers.onboarding import send_platform_buttons

        bot = AsyncMock()
        mock_settings = MagicMock()
        mock_settings.connect_base_url = "https://connect.scribario.com"

        with patch("bot.config.get_settings", return_value=mock_settings):
            await send_platform_buttons(bot, 456)

        bot.send_message.assert_called()
        call_args = bot.send_message.call_args
        assert call_args[0][0] == 456  # chat_id


# --- Gap 5: /brand placeholder ---


class TestCmdBrand:
    """Gap 5: /brand shows current profile."""

    @pytest.mark.asyncio
    async def test_brand_shows_profile(self):
        from bot.handlers.onboarding import cmd_brand
        from pipeline.brand_voice import BrandProfile

        message = AsyncMock()
        message.from_user = MagicMock(id=123)

        membership = {
            "tenant_id": "t1",
            "onboarding_status": "complete",
        }
        profile = BrandProfile(
            tenant_id="t1",
            name="Mondo Shrimp",
            tone_words=["bold", "playful"],
            audience_description="Hot sauce lovers",
            do_list=["Use humor"],
            dont_list=["Be boring"],
        )

        with (
            patch("bot.handlers.onboarding.get_tenant_by_telegram_user", return_value=membership),
            patch("pipeline.brand_voice.load_brand_profile", return_value=profile),
        ):
            await cmd_brand(message)

        call_text = message.answer.call_args[0][0]
        assert "Mondo Shrimp" in call_text
        assert "bold" in call_text
        assert "edit" in call_text.lower()  # edit buttons prompt
        # Should have inline keyboard with edit buttons
        reply_markup = message.answer.call_args[1].get("reply_markup")
        assert reply_markup is not None

    @pytest.mark.asyncio
    async def test_brand_blocks_incomplete_onboarding(self):
        from bot.handlers.onboarding import cmd_brand

        message = AsyncMock()
        message.from_user = MagicMock(id=123)

        membership = {
            "tenant_id": "t1",
            "onboarding_status": "pending",
        }

        with patch("bot.handlers.onboarding.get_tenant_by_telegram_user", return_value=membership):
            await cmd_brand(message)

        call_text = message.answer.call_args[0][0]
        assert "/start" in call_text


# --- Pre-existing bug fix ---


class TestErrorFallbackUpdatesStatus:
    """Pre-existing bug: error fallback now calls update_onboarding_status."""

    @pytest.mark.asyncio
    async def test_error_path_marks_onboarding_complete(self):
        """When scraping fails, fallback path should still mark onboarding complete."""
        from bot.dialogs.onboarding import on_website_url_input

        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.text = "https://example.com"
        status_msg = AsyncMock()
        message.answer.return_value = status_msg

        widget = MagicMock()
        manager = MagicMock()
        manager.dialog_data = {"business_name": "Test"}
        manager.switch_to = AsyncMock()

        with (
            patch("bot.db.create_tenant", return_value={"id": "t-err"}),
            patch("bot.db.create_tenant_member", return_value={}),
            patch("bot.db.update_tenant_website_url"),
            patch("pipeline.scraper.scrape_website", side_effect=RuntimeError("Network down")),
            patch("bot.db.upsert_brand_profile"),
            patch("bot.db.update_onboarding_status") as mock_status,
            patch("asyncio.create_task"),
        ):
            await on_website_url_input(message, widget, manager)

        # Should have called update_onboarding_status in the error fallback
        mock_status.assert_called_once_with("t-err", 123, "complete")


# --- Approve profile seeds few-shot examples ---


class TestOnApproveProfileSeedsFewShot:
    """Gap 2: on_approve_profile triggers async few-shot seeding."""

    @pytest.mark.asyncio
    async def test_approve_creates_seeding_task(self):
        from bot.dialogs.onboarding import on_approve_profile

        callback = AsyncMock()
        callback.from_user = MagicMock(id=123)
        button = MagicMock()
        manager = AsyncMock()
        manager.dialog_data = {
            "tenant_id": "t1",
            "profile_name": "Test Brand",
            "_profile_obj": {
                "name": "Test Brand",
                "tone_words": ["bold"],
                "audience_description": "Foodies",
                "do_list": [],
                "dont_list": [],
                "product_catalog": [],
                "tagline": None,
            },
        }

        with (
            patch("bot.db.update_onboarding_status"),
            patch("asyncio.create_task") as mock_task,
        ):
            await on_approve_profile(callback, button, manager)

        mock_task.assert_called_once()


# --- DB select includes onboarding_status ---


class TestGetTenantIncludesOnboardingStatus:
    """Gap 4 (I4): get_tenant_by_telegram_user select includes onboarding_status."""

    def test_select_string_includes_onboarding_status(self):
        """Verify the select string in the source code includes onboarding_status."""
        import inspect
        from bot.db import get_tenant_by_telegram_user

        source = inspect.getsource(get_tenant_by_telegram_user)
        assert "onboarding_status" in source
