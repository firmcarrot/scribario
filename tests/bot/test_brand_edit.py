"""Tests for brand profile editing flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.dialogs.states import BrandEditSG
from bot.handlers.brand_edit import FIELD_CONFIG, on_brand_edit, on_brand_edit_value


class TestBrandEditCallback:
    """Tests for the edit button callback handler."""

    @pytest.mark.asyncio
    async def test_sets_fsm_state_on_valid_callback(self):
        """Tapping an edit button should set FSM to waiting_for_value."""
        callback = AsyncMock()
        callback.data = "brand_edit:tone:tenant-123"
        callback.message = AsyncMock()
        state = AsyncMock()

        await on_brand_edit(callback, state)

        state.set_state.assert_called_once_with(BrandEditSG.waiting_for_value)
        state.update_data.assert_called_once_with(
            brand_edit_field="tone",
            brand_edit_tenant_id="tenant-123",
        )
        callback.message.answer.assert_called_once()
        assert "tone" in callback.message.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_rejects_unknown_field(self):
        """Unknown field key should not set FSM state."""
        callback = AsyncMock()
        callback.data = "brand_edit:nonexistent:tenant-123"
        state = AsyncMock()

        await on_brand_edit(callback, state)

        state.set_state.assert_not_called()
        callback.answer.assert_called_once_with("Unknown field.")

    @pytest.mark.asyncio
    async def test_all_fields_have_config(self):
        """Every editable field should have a config entry."""
        expected_fields = {"name", "tone", "audience", "dos", "donts"}
        assert set(FIELD_CONFIG.keys()) == expected_fields


class TestBrandEditValue:
    """Tests for receiving the edited value."""

    @pytest.mark.asyncio
    async def test_updates_text_field(self):
        """Text fields (name, audience) should save as plain string."""
        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.text = "Mondo Shrimp"
        state = AsyncMock()
        state.get_data.return_value = {
            "brand_edit_field": "name",
            "brand_edit_tenant_id": "tenant-123",
        }

        mock_client = MagicMock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = None

        with (
            patch("bot.handlers.brand_edit.get_tenant_by_telegram_user", return_value={"tenant_id": "tenant-123"}),
            patch("bot.handlers.brand_edit.get_supabase_client", return_value=mock_client),
        ):
            await on_brand_edit_value(message, state)

        mock_client.table.assert_called_with("brand_profiles")
        update_arg = mock_client.table.return_value.update.call_args[0][0]
        assert update_arg == {"brand_name": "Mondo Shrimp"}
        state.clear.assert_called()

    @pytest.mark.asyncio
    async def test_updates_list_field(self):
        """Comma-separated fields (tone) should save as list."""
        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.text = "bold, witty, warm"
        state = AsyncMock()
        state.get_data.return_value = {
            "brand_edit_field": "tone",
            "brand_edit_tenant_id": "tenant-123",
        }

        mock_client = MagicMock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = None

        with (
            patch("bot.handlers.brand_edit.get_tenant_by_telegram_user", return_value={"tenant_id": "tenant-123"}),
            patch("bot.handlers.brand_edit.get_supabase_client", return_value=mock_client),
        ):
            await on_brand_edit_value(message, state)

        update_arg = mock_client.table.return_value.update.call_args[0][0]
        assert update_arg == {"tone": ["bold", "witty", "warm"]}

    @pytest.mark.asyncio
    async def test_updates_lines_field(self):
        """Multi-line fields (dos, donts) should save as list of lines."""
        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.text = "Always mention the website\nUse casual tone"
        state = AsyncMock()
        state.get_data.return_value = {
            "brand_edit_field": "dos",
            "brand_edit_tenant_id": "tenant-123",
        }

        mock_client = MagicMock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = None

        with (
            patch("bot.handlers.brand_edit.get_tenant_by_telegram_user", return_value={"tenant_id": "tenant-123"}),
            patch("bot.handlers.brand_edit.get_supabase_client", return_value=mock_client),
        ):
            await on_brand_edit_value(message, state)

        update_arg = mock_client.table.return_value.update.call_args[0][0]
        assert update_arg == {"dos": ["Always mention the website", "Use casual tone"]}

    @pytest.mark.asyncio
    async def test_rejects_wrong_tenant(self):
        """User should not be able to edit another tenant's brand."""
        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.text = "New Name"
        state = AsyncMock()
        state.get_data.return_value = {
            "brand_edit_field": "name",
            "brand_edit_tenant_id": "tenant-999",
        }

        with patch(
            "bot.handlers.brand_edit.get_tenant_by_telegram_user",
            return_value={"tenant_id": "tenant-123"},
        ):
            await on_brand_edit_value(message, state)

        state.clear.assert_called()
        message.answer.assert_called_once()
        assert "access" in message.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_rejects_empty_text(self):
        """Empty messages should ask user to try again."""
        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.text = "   "
        state = AsyncMock()
        state.get_data.return_value = {
            "brand_edit_field": "name",
            "brand_edit_tenant_id": "tenant-123",
        }

        with patch(
            "bot.handlers.brand_edit.get_tenant_by_telegram_user",
            return_value={"tenant_id": "tenant-123"},
        ):
            await on_brand_edit_value(message, state)

        # Should NOT clear state — let user retry
        state.clear.assert_not_called()
