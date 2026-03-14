"""Tests for the long-form video job handler."""

from __future__ import annotations

from dataclasses import dataclass, field
from unittest.mock import AsyncMock, patch

from worker.jobs.generate_long_video import handle_generate_long_video

TENANT_ID = "52590da5-bc80-4161-ac13-62e9bcd75424"
PROJECT_ID = "aaaaaaaa-1111-2222-3333-444444444444"
CHAT_ID = 7560539974


def _base_message() -> dict:
    return {
        "project_id": PROJECT_ID,
        "tenant_id": TENANT_ID,
        "telegram_chat_id": CHAT_ID,
    }


def _mock_project() -> dict:
    return {
        "id": PROJECT_ID,
        "tenant_id": TENANT_ID,
        "intent": "Make a video about shrimp",
        "aspect_ratio": "16:9",
        "status": "scripting",
    }


@dataclass
class _FakePipelineResult:
    project_id: str = PROJECT_ID
    video_path: str = "/tmp/scribario/final.mp4"
    duration_seconds: float = 45.0
    total_cost_usd: float = 2.50
    script: object = None
    scene_count: int = 3
    scenes_completed: int = 3
    captions: list = field(
        default_factory=lambda: [{"platform": "facebook", "text": "Generated caption"}]
    )


class TestHandleGenerateLongVideoHappyPath:
    @patch("worker.jobs.generate_long_video._send_video_preview", new_callable=AsyncMock)
    @patch("worker.jobs.generate_long_video._upload_to_storage")
    @patch("worker.jobs.generate_long_video.log_usage_event", new_callable=AsyncMock)
    @patch("worker.jobs.generate_long_video.update_video_project_status", new_callable=AsyncMock)
    @patch("worker.jobs.generate_long_video.get_video_project", new_callable=AsyncMock)
    @patch("worker.jobs.generate_long_video.run_pipeline", new_callable=AsyncMock)
    async def test_happy_path_calls_pipeline_and_uploads(
        self,
        mock_pipeline,
        mock_get_project,
        mock_update_status,
        mock_log_usage,
        mock_upload,
        mock_send_preview,
    ):
        mock_get_project.return_value = _mock_project()
        mock_pipeline.return_value = _FakePipelineResult()
        mock_upload.return_value = "https://storage.example.com/video.mp4"

        await handle_generate_long_video(_base_message())

        # Pipeline was called with correct params
        mock_pipeline.assert_called_once()
        call_kwargs = mock_pipeline.call_args[1]
        assert call_kwargs["project_id"] == PROJECT_ID
        assert call_kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs["intent"] == "Make a video about shrimp"
        assert call_kwargs["aspect_ratio"] == "16:9"
        assert call_kwargs["status_callback"] is not None

        # Video was uploaded to storage
        mock_upload.assert_called_once()

        # Project was updated to preview_ready with final URL
        update_calls = mock_update_status.call_args_list
        statuses = [c[0][1] for c in update_calls]
        assert "preview_ready" in statuses

        # Usage event was logged
        mock_log_usage.assert_called_once()

        # Preview was sent to Telegram
        mock_send_preview.assert_called_once()


class TestHandleGenerateLongVideoFailure:
    @patch("worker.jobs.generate_long_video._send_error_message", new_callable=AsyncMock)
    @patch("worker.jobs.generate_long_video.update_video_project_status", new_callable=AsyncMock)
    @patch("worker.jobs.generate_long_video.get_video_project", new_callable=AsyncMock)
    @patch("worker.jobs.generate_long_video.run_pipeline", new_callable=AsyncMock)
    async def test_failure_updates_project_and_notifies(
        self,
        mock_pipeline,
        mock_get_project,
        mock_update_status,
        mock_send_error,
    ):
        mock_get_project.return_value = _mock_project()
        mock_pipeline.side_effect = RuntimeError("Kie.ai API down")

        await handle_generate_long_video(_base_message())

        # Project was marked as failed with error message
        mock_update_status.assert_called_with(
            PROJECT_ID, "failed", error_message="Kie.ai API down"
        )

        # Error message was sent to Telegram
        mock_send_error.assert_called_once()
        error_call_args = mock_send_error.call_args
        assert error_call_args[1]["chat_id"] == CHAT_ID


class TestStatusCallback:
    @patch("worker.jobs.generate_long_video.log_usage_event", new_callable=AsyncMock)
    @patch("worker.jobs.generate_long_video.update_video_project_status", new_callable=AsyncMock)
    @patch("worker.jobs.generate_long_video.get_video_project", new_callable=AsyncMock)
    @patch("worker.jobs.generate_long_video.run_pipeline", new_callable=AsyncMock)
    async def test_status_callback_updates_db(
        self,
        mock_pipeline,
        mock_get_project,
        mock_update_status,
        mock_log_usage,
    ):
        """The status_callback passed to run_pipeline should update DB status."""
        mock_get_project.return_value = _mock_project()

        # Capture the status_callback that gets passed to run_pipeline
        captured_callback = None

        async def capture_pipeline(**kwargs):
            nonlocal captured_callback
            captured_callback = kwargs.get("status_callback")
            # Simulate calling the callback with (status, message)
            if captured_callback:
                await captured_callback("generating_clips", "Generating clips...")
            return _FakePipelineResult()

        mock_pipeline.side_effect = capture_pipeline

        with (
            patch(
                "worker.jobs.generate_long_video._upload_to_storage",
                return_value="https://example.com/v.mp4",
            ),
            patch(
                "worker.jobs.generate_long_video._send_video_preview",
                new_callable=AsyncMock,
            ),
        ):
            await handle_generate_long_video(_base_message())

        assert captured_callback is not None
        # The callback should have triggered an update_video_project_status call
        status_calls = [c[0][1] for c in mock_update_status.call_args_list]
        assert "generating_clips" in status_calls
