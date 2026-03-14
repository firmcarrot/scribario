"""Tests for long-form video DB CRUD functions."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from bot.db import (
    check_tenant_long_video_in_progress,
    create_video_project,
    create_video_scenes,
    get_tenant_daily_video_cost,
    get_video_project,
    get_video_scenes,
    update_video_project_status,
    update_video_scene,
)

TENANT_ID = "52590da5-bc80-4161-ac13-62e9bcd75424"
PROJECT_ID = "aaaaaaaa-1111-2222-3333-444444444444"
SCENE_ID = "bbbbbbbb-1111-2222-3333-444444444444"
REQUEST_ID = "cccccccc-1111-2222-3333-444444444444"


def _make_client(return_data: list[dict] | None = None, count: int | None = None):
    """Build a mock Supabase client with full chain support."""
    client = MagicMock()
    chain = MagicMock()
    resp = MagicMock(data=return_data or [], count=count)
    chain.execute.return_value = resp
    client.table.return_value = chain
    chain.insert.return_value = chain
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.in_.return_value = chain
    chain.is_.return_value = chain
    chain.order.return_value = chain
    chain.limit.return_value = chain
    chain.update.return_value = chain
    chain.gte.return_value = chain
    chain.lt.return_value = chain
    chain.single.return_value = chain
    return client


class TestCreateVideoProject:
    async def test_inserts_correct_data(self):
        expected = {
            "id": PROJECT_ID,
            "tenant_id": TENANT_ID,
            "intent": "Make a video about shrimp",
            "aspect_ratio": "16:9",
            "status": "scripting",
        }
        client = _make_client([expected])
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await create_video_project(
                tenant_id=TENANT_ID,
                intent="Make a video about shrimp",
            )
        assert result["id"] == PROJECT_ID
        assert result["tenant_id"] == TENANT_ID
        assert result["status"] == "scripting"
        client.table.assert_called_with("video_projects")

    async def test_with_request_id_and_custom_ratio(self):
        expected = {
            "id": PROJECT_ID,
            "tenant_id": TENANT_ID,
            "intent": "Vertical shrimp video",
            "aspect_ratio": "9:16",
            "request_id": REQUEST_ID,
            "status": "scripting",
        }
        client = _make_client([expected])
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await create_video_project(
                tenant_id=TENANT_ID,
                intent="Vertical shrimp video",
                request_id=REQUEST_ID,
                aspect_ratio="9:16",
            )
        assert result["id"] == PROJECT_ID
        assert result["aspect_ratio"] == "9:16"


class TestUpdateVideoProjectStatus:
    async def test_updates_status(self):
        client = _make_client([])
        with patch("bot.db.get_supabase_client", return_value=client):
            await update_video_project_status(PROJECT_ID, "tts")
        client.table.assert_called_with("video_projects")

    async def test_updates_status_with_kwargs(self):
        client = _make_client([])
        with patch("bot.db.get_supabase_client", return_value=client):
            await update_video_project_status(
                PROJECT_ID,
                "failed",
                error_message="Something went wrong",
            )
        client.table.assert_called_with("video_projects")
        # Verify update was called with both status and error_message
        update_call = client.table.return_value.update.call_args
        update_data = update_call[0][0]
        assert update_data["status"] == "failed"
        assert update_data["error_message"] == "Something went wrong"


class TestGetVideoProject:
    async def test_returns_dict_when_found(self):
        project = {"id": PROJECT_ID, "tenant_id": TENANT_ID, "status": "scripting"}
        client = _make_client([project])
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await get_video_project(PROJECT_ID)
        assert result is not None
        assert result["id"] == PROJECT_ID

    async def test_returns_none_when_not_found(self):
        client = _make_client([])
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await get_video_project(PROJECT_ID)
        assert result is None


class TestCreateVideoScenes:
    async def test_batch_inserts_scenes(self):
        scenes_input = [
            {
                "scene_index": 0,
                "scene_type": "a_roll",
                "voiceover_text": "Hello world",
                "visual_description": "Wide shot",
            },
            {
                "scene_index": 1,
                "scene_type": "b_roll",
                "voiceover_text": "Shrimp cooking",
                "visual_description": "Close-up",
            },
        ]
        expected = [
            {"id": "s1", "project_id": PROJECT_ID, **scenes_input[0]},
            {"id": "s2", "project_id": PROJECT_ID, **scenes_input[1]},
        ]
        client = _make_client(expected)
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await create_video_scenes(
                project_id=PROJECT_ID,
                tenant_id=TENANT_ID,
                scenes=scenes_input,
            )
        assert len(result) == 2
        client.table.assert_called_with("video_scenes")
        # Verify insert was called with project_id and tenant_id on each row
        insert_call = client.table.return_value.insert.call_args
        rows = insert_call[0][0]
        assert all(r["project_id"] == PROJECT_ID for r in rows)
        assert all(r["tenant_id"] == TENANT_ID for r in rows)


class TestUpdateVideoScene:
    async def test_updates_arbitrary_fields(self):
        client = _make_client([])
        with patch("bot.db.get_supabase_client", return_value=client):
            await update_video_scene(
                SCENE_ID,
                voiceover_url="https://storage/vo.mp3",
                video_clip_url="https://storage/clip.mp4",
            )
        client.table.assert_called_with("video_scenes")
        update_data = client.table.return_value.update.call_args[0][0]
        assert update_data["voiceover_url"] == "https://storage/vo.mp3"
        assert update_data["video_clip_url"] == "https://storage/clip.mp4"


class TestGetVideoScenes:
    async def test_returns_ordered_scenes(self):
        scenes = [
            {"id": "s1", "scene_index": 0, "project_id": PROJECT_ID},
            {"id": "s2", "scene_index": 1, "project_id": PROJECT_ID},
        ]
        client = _make_client(scenes)
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await get_video_scenes(PROJECT_ID)
        assert len(result) == 2
        client.table.assert_called_with("video_scenes")

    async def test_returns_empty_list_when_no_scenes(self):
        client = _make_client([])
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await get_video_scenes(PROJECT_ID)
        assert result == []


class TestCheckTenantLongVideoInProgress:
    async def test_returns_true_when_active_project(self):
        client = _make_client([{"id": PROJECT_ID, "status": "scripting"}])
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await check_tenant_long_video_in_progress(TENANT_ID)
        assert result is True

    async def test_returns_false_when_no_active_project(self):
        client = _make_client([])
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await check_tenant_long_video_in_progress(TENANT_ID)
        assert result is False


class TestGetTenantDailyVideoCost:
    async def test_sums_todays_usage(self):
        events = [
            {"cost_usd": 0.50},
            {"cost_usd": 1.25},
            {"cost_usd": 0.75},
        ]
        client = _make_client(events)
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await get_tenant_daily_video_cost(TENANT_ID)
        assert result == pytest.approx(2.50)

    async def test_returns_zero_when_no_usage(self):
        client = _make_client([])
        with patch("bot.db.get_supabase_client", return_value=client):
            result = await get_tenant_daily_video_cost(TENANT_ID)
        assert result == 0.0
