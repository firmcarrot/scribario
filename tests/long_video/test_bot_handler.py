"""Tests for /longvideo Telegram bot handler."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

from pipeline.brand_voice import BrandProfile
from pipeline.long_video.models import LongVideoScript, Scene, SceneType

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _make_profile(**overrides) -> BrandProfile:
    defaults = {
        "tenant_id": "test-tenant-111",
        "name": "Mondo Shrimp",
        "tone_words": ["bold", "fun", "spicy"],
        "audience_description": "Hot sauce enthusiasts aged 25-45",
        "do_list": ["Use fire emojis"],
        "dont_list": ["No health claims"],
        "product_catalog": {},
        "compliance_notes": "",
    }
    defaults.update(overrides)
    return BrandProfile(**defaults)


def _make_script(num_scenes: int = 4) -> LongVideoScript:
    scenes = []
    for i in range(num_scenes):
        scenes.append(
            Scene(
                index=i,
                scene_type=SceneType.A_ROLL if i % 2 == 0 else SceneType.B_ROLL,
                voiceover_text=f"Voiceover for scene {i}.",
                visual_description=f"Visual desc {i}",
                start_frame_prompt=f"Start frame {i}",
                end_frame_prompt=f"End frame {i}",
                camera_direction=f"camera move {i}",
                sfx_description=f"sfx {i}",
            )
        )
    return LongVideoScript(title="Test Video", voice_style="narrator", scenes=scenes)


def _make_message(text: str = "/longvideo showcase our shrimp sauce") -> MagicMock:
    """Create a mock aiogram Message."""
    msg = AsyncMock()
    msg.text = text
    msg.from_user = MagicMock()
    msg.from_user.id = 7560539974
    msg.chat = MagicMock()
    msg.chat.id = 12345
    msg.answer = AsyncMock()
    return msg


def _make_callback(data: str) -> MagicMock:
    """Create a mock aiogram CallbackQuery."""
    cb = AsyncMock()
    cb.data = data
    cb.from_user = MagicMock()
    cb.from_user.id = 7560539974
    cb.answer = AsyncMock()
    cb.message = MagicMock()
    cb.message.chat = MagicMock()
    cb.message.chat.id = 12345
    cb.message.edit_reply_markup = AsyncMock()
    cb.message.reply = AsyncMock()
    cb.message.edit_text = AsyncMock()
    return cb


# ---------------------------------------------------------------------------
# Test: Intent extraction
# ---------------------------------------------------------------------------

class TestIntentExtraction:
    """Test /longvideo extracts intent from the command text."""

    @patch("bot.handlers.long_video.generate_script", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.load_brand_profile", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.create_video_project", new_callable=AsyncMock)
    @patch(
        "bot.handlers.long_video.check_tenant_long_video_in_progress",
        new_callable=AsyncMock,
    )
    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    async def test_extracts_intent_from_command(
        self,
        mock_get_tenant,
        mock_in_progress,
        mock_create_project,
        mock_load_profile,
        mock_gen_script,
    ) -> None:
        from bot.handlers.long_video import cmd_longvideo

        mock_get_tenant.return_value = {"tenant_id": "t1"}
        mock_in_progress.return_value = False
        mock_load_profile.return_value = _make_profile()
        script = _make_script()
        mock_gen_script.return_value = script
        mock_create_project.return_value = {"id": "proj-1"}

        msg = _make_message("/longvideo showcase our shrimp sauce")
        await cmd_longvideo(msg)

        mock_gen_script.assert_awaited_once()
        call_args = mock_gen_script.call_args
        assert call_args[0][0] == "showcase our shrimp sauce"

    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    async def test_no_intent_replies_usage(self, mock_get_tenant) -> None:
        from bot.handlers.long_video import cmd_longvideo

        mock_get_tenant.return_value = {"tenant_id": "t1"}

        msg = _make_message("/longvideo")
        await cmd_longvideo(msg)

        msg.answer.assert_awaited_once()
        reply_text = msg.answer.call_args[0][0]
        assert "usage" in reply_text.lower() or "describe" in reply_text.lower()

    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    async def test_no_tenant_replies_not_set_up(self, mock_get_tenant) -> None:
        from bot.handlers.long_video import cmd_longvideo

        mock_get_tenant.return_value = None

        msg = _make_message("/longvideo promo video")
        await cmd_longvideo(msg)

        msg.answer.assert_awaited_once()
        reply_text = msg.answer.call_args[0][0]
        assert "not set up" in reply_text.lower() or "start" in reply_text.lower()


# ---------------------------------------------------------------------------
# Test: Rate limiting (concurrent in-progress check)
# ---------------------------------------------------------------------------

class TestRateLimiting:
    """Test that concurrent long video generation is blocked."""

    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    @patch(
        "bot.handlers.long_video.check_tenant_long_video_in_progress",
        new_callable=AsyncMock,
    )
    async def test_blocks_when_video_in_progress(
        self, mock_in_progress, mock_get_tenant
    ) -> None:
        from bot.handlers.long_video import cmd_longvideo

        mock_get_tenant.return_value = {"tenant_id": "t1"}
        mock_in_progress.return_value = True

        msg = _make_message("/longvideo new promo")
        await cmd_longvideo(msg)

        msg.answer.assert_awaited_once()
        reply_text = msg.answer.call_args[0][0]
        assert "wait" in reply_text.lower() or "current video" in reply_text.lower()


# ---------------------------------------------------------------------------
# Test: Cooldown (5-minute minimum between requests)
# ---------------------------------------------------------------------------

class TestCooldown:
    """Test 5-minute cooldown between requests."""

    @patch("bot.handlers.long_video.generate_script", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.load_brand_profile", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.create_video_project", new_callable=AsyncMock)
    @patch(
        "bot.handlers.long_video.check_tenant_long_video_in_progress",
        new_callable=AsyncMock,
    )
    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    async def test_cooldown_blocks_second_request(
        self,
        mock_get_tenant,
        mock_in_progress,
        mock_create_project,
        mock_load_profile,
        mock_gen_script,
    ) -> None:
        from bot.handlers.long_video import _cooldowns, cmd_longvideo

        mock_get_tenant.return_value = {"tenant_id": "cooldown-tenant"}
        mock_in_progress.return_value = False
        mock_load_profile.return_value = _make_profile()
        mock_gen_script.return_value = _make_script()
        mock_create_project.return_value = {"id": "proj-cd"}

        # Simulate recent request
        _cooldowns["cooldown-tenant"] = time.time()

        msg = _make_message("/longvideo another promo")
        await cmd_longvideo(msg)

        msg.answer.assert_awaited_once()
        reply_text = msg.answer.call_args[0][0]
        assert "wait" in reply_text.lower() or "cooldown" in reply_text.lower()

        # Cleanup
        _cooldowns.pop("cooldown-tenant", None)

    @patch("bot.handlers.long_video.generate_script", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.load_brand_profile", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.create_video_project", new_callable=AsyncMock)
    @patch(
        "bot.handlers.long_video.check_tenant_long_video_in_progress",
        new_callable=AsyncMock,
    )
    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    async def test_cooldown_allows_after_expiry(
        self,
        mock_get_tenant,
        mock_in_progress,
        mock_create_project,
        mock_load_profile,
        mock_gen_script,
    ) -> None:
        from bot.handlers.long_video import COOLDOWN_SECONDS, _cooldowns, cmd_longvideo

        mock_get_tenant.return_value = {"tenant_id": "expired-tenant"}
        mock_in_progress.return_value = False
        mock_load_profile.return_value = _make_profile()
        mock_gen_script.return_value = _make_script()
        mock_create_project.return_value = {"id": "proj-ex"}

        # Set cooldown in the past
        _cooldowns["expired-tenant"] = time.time() - COOLDOWN_SECONDS - 10

        msg = _make_message("/longvideo after cooldown")
        await cmd_longvideo(msg)

        # Should have called generate_script (not blocked)
        mock_gen_script.assert_awaited_once()

        # Cleanup
        _cooldowns.pop("expired-tenant", None)


# ---------------------------------------------------------------------------
# Test: Script preview formatting
# ---------------------------------------------------------------------------

class TestScriptPreviewFormat:
    """Test _format_script_preview output."""

    def test_format_includes_all_scenes(self) -> None:
        from bot.handlers.long_video import _format_script_preview

        script = _make_script(4)
        preview = _format_script_preview(script)

        assert "Scene 1:" in preview
        assert "Scene 2:" in preview
        assert "Scene 3:" in preview
        assert "Scene 4:" in preview

    def test_format_includes_visual_and_camera(self) -> None:
        from bot.handlers.long_video import _format_script_preview

        script = _make_script(2)
        preview = _format_script_preview(script)

        assert "Visual desc 0" in preview
        assert "camera move 0" in preview

    def test_format_includes_voiceover_preview(self) -> None:
        from bot.handlers.long_video import _format_script_preview

        script = _make_script(4)
        preview = _format_script_preview(script)

        # Should include first scene's voiceover
        assert "Voiceover for scene 0" in preview

    def test_format_includes_scene_count_and_duration(self) -> None:
        from bot.handlers.long_video import _format_script_preview

        script = _make_script(4)
        preview = _format_script_preview(script)

        assert "4 scenes" in preview
        assert "30s" in preview


# ---------------------------------------------------------------------------
# Test: Approve callback
# ---------------------------------------------------------------------------

class TestApproveCallback:
    """Test longvideo_approve callback enqueues job."""

    @patch("bot.handlers.long_video.enqueue_job", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.update_video_project_status", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.get_video_project", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    async def test_approve_enqueues_generation_job(
        self,
        mock_get_tenant,
        mock_get_project,
        mock_update_status,
        mock_enqueue,
    ) -> None:
        from bot.handlers.long_video import cb_longvideo_approve

        mock_get_tenant.return_value = {"tenant_id": "t1"}
        mock_get_project.return_value = {
            "id": "proj-1",
            "tenant_id": "t1",
            "status": "scripting",
        }

        cb = _make_callback("longvideo_approve:proj-1")
        await cb_longvideo_approve(cb)

        mock_enqueue.assert_awaited_once()
        call_kwargs = mock_enqueue.call_args.kwargs
        assert call_kwargs["queue_name"] == "content_generation"
        assert call_kwargs["job_type"] == "generate_long_video"
        assert call_kwargs["payload"]["project_id"] == "proj-1"

    @patch("bot.handlers.long_video.get_video_project", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    async def test_approve_wrong_tenant_blocked(
        self, mock_get_tenant, mock_get_project
    ) -> None:
        from bot.handlers.long_video import cb_longvideo_approve

        mock_get_tenant.return_value = {"tenant_id": "other-tenant"}
        mock_get_project.return_value = {
            "id": "proj-1",
            "tenant_id": "t1",
            "status": "scripting",
        }

        cb = _make_callback("longvideo_approve:proj-1")
        await cb_longvideo_approve(cb)

        cb.answer.assert_awaited_once()
        reply_text = cb.answer.call_args[0][0]
        assert "access" in reply_text.lower() or "don't" in reply_text.lower()


# ---------------------------------------------------------------------------
# Test: Cancel callback
# ---------------------------------------------------------------------------

class TestCancelCallback:
    """Test longvideo_cancel callback updates status."""

    @patch("bot.handlers.long_video.update_video_project_status", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.get_video_project", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    async def test_cancel_updates_status_to_failed(
        self, mock_get_tenant, mock_get_project, mock_update_status
    ) -> None:
        from bot.handlers.long_video import cb_longvideo_cancel

        mock_get_tenant.return_value = {"tenant_id": "t1"}
        mock_get_project.return_value = {
            "id": "proj-1",
            "tenant_id": "t1",
            "status": "scripting",
        }

        cb = _make_callback("longvideo_cancel:proj-1")
        await cb_longvideo_cancel(cb)

        mock_update_status.assert_awaited_once_with("proj-1", "failed")

    @patch("bot.handlers.long_video.update_video_project_status", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.get_video_project", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    async def test_cancel_replies_cancelled(
        self, mock_get_tenant, mock_get_project, mock_update_status
    ) -> None:
        from bot.handlers.long_video import cb_longvideo_cancel

        mock_get_tenant.return_value = {"tenant_id": "t1"}
        mock_get_project.return_value = {
            "id": "proj-1",
            "tenant_id": "t1",
            "status": "scripting",
        }

        cb = _make_callback("longvideo_cancel:proj-1")
        await cb_longvideo_cancel(cb)

        cb.answer.assert_awaited_once()
        reply_text = cb.answer.call_args[0][0]
        assert "cancel" in reply_text.lower()


# ---------------------------------------------------------------------------
# Test: Rescript callback
# ---------------------------------------------------------------------------

class TestRescriptCallback:
    """Test longvideo_rescript regenerates script."""

    @patch("bot.handlers.long_video.generate_script", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.load_brand_profile", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.update_video_project_script", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.get_video_project", new_callable=AsyncMock)
    @patch("bot.handlers.long_video.get_tenant_by_telegram_user", new_callable=AsyncMock)
    async def test_rescript_generates_new_script(
        self,
        mock_get_tenant,
        mock_get_project,
        mock_update_script,
        mock_load_profile,
        mock_gen_script,
    ) -> None:
        from bot.handlers.long_video import cb_longvideo_rescript

        mock_get_tenant.return_value = {"tenant_id": "t1"}
        mock_get_project.return_value = {
            "id": "proj-1",
            "tenant_id": "t1",
            "status": "scripting",
            "intent": "showcase our shrimp sauce",
        }
        mock_load_profile.return_value = _make_profile()
        new_script = _make_script()
        mock_gen_script.return_value = new_script

        cb = _make_callback("longvideo_rescript:proj-1")
        await cb_longvideo_rescript(cb)

        mock_gen_script.assert_awaited_once()
        mock_update_script.assert_awaited_once()
