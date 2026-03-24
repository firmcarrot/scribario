"""Tests for /feedback and /ticket commands — support ticket system."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext


# --- DB function tests ---


class TestCreateSupportTicket:
    """create_support_ticket inserts and returns row with ticket_number."""

    @pytest.mark.asyncio
    async def test_creates_ticket_and_returns_row(self):
        row = {
            "id": "uuid-1",
            "tenant_id": "tenant-abc",
            "ticket_number": "SC-00001",
            "category": "bug",
            "description": "Button broken",
            "status": "open",
            "creator_telegram_user_id": 12345,
            "creator_telegram_chat_id": 12345,
        }
        table_mock = MagicMock()
        table_mock.insert.return_value.execute.return_value = MagicMock(data=[row])

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = table_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import create_support_ticket

            result = await create_support_ticket(
                tenant_id="tenant-abc",
                category="bug",
                description="Button broken",
                creator_telegram_user_id=12345,
                creator_telegram_chat_id=12345,
            )

        assert result["ticket_number"] == "SC-00001"
        assert result["category"] == "bug"
        # Verify ticket_number NOT in insert data (Postgres generates it)
        insert_data = table_mock.insert.call_args[0][0]
        assert "ticket_number" not in insert_data

    @pytest.mark.asyncio
    async def test_omits_ticket_number_from_insert(self):
        """ticket_number must NOT be in insert payload — Postgres DEFAULT fills it."""
        table_mock = MagicMock()
        table_mock.insert.return_value.execute.return_value = MagicMock(
            data=[{"ticket_number": "SC-00001"}]
        )

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = table_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import create_support_ticket

            await create_support_ticket(
                tenant_id="t", category="idea", description="x",
                creator_telegram_user_id=1, creator_telegram_chat_id=1,
            )

        insert_data = table_mock.insert.call_args[0][0]
        assert "ticket_number" not in insert_data
        assert insert_data["category"] == "idea"


class TestGetSupportTicketByNumber:
    """get_support_ticket_by_number lookups."""

    @pytest.mark.asyncio
    async def test_returns_ticket_when_found(self):
        row = {"ticket_number": "SC-00001", "status": "open"}
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[row])
        )

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = table_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import get_support_ticket_by_number

            result = await get_support_ticket_by_number("SC-00001")

        assert result is not None
        assert result["ticket_number"] == "SC-00001"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[])
        )

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = table_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import get_support_ticket_by_number

            result = await get_support_ticket_by_number("SC-99999")

        assert result is None

    @pytest.mark.asyncio
    async def test_case_insensitive_lookup(self):
        """Passes uppercased ticket_number to .eq()."""
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[])
        )

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = table_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import get_support_ticket_by_number

            await get_support_ticket_by_number("sc-00001")

        # First .eq() call should have uppercased value
        eq_calls = table_mock.select.return_value.eq.call_args_list
        assert eq_calls[0][0] == ("ticket_number", "SC-00001")

    @pytest.mark.asyncio
    async def test_tenant_id_filter_applied(self):
        """When tenant_id provided, adds .eq('tenant_id', ...) for cross-tenant protection."""
        table_mock = MagicMock()
        # Chain: .select().eq(ticket_number).eq(tenant_id).limit().execute()
        chain = table_mock.select.return_value.eq.return_value.eq.return_value.limit.return_value
        chain.execute.return_value = MagicMock(data=[])

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = table_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import get_support_ticket_by_number

            await get_support_ticket_by_number("SC-00001", tenant_id="tenant-abc")

        # Should have two .eq() calls — ticket_number and tenant_id
        first_eq = table_mock.select.return_value.eq
        assert first_eq.call_args[0] == ("ticket_number", "SC-00001")
        second_eq = first_eq.return_value.eq
        assert second_eq.call_args[0] == ("tenant_id", "tenant-abc")


class TestGetUserTickets:
    """get_user_tickets returns recent tickets for a user."""

    @pytest.mark.asyncio
    async def test_returns_tickets_list(self):
        rows = [
            {"ticket_number": "SC-00002", "status": "open"},
            {"ticket_number": "SC-00001", "status": "resolved"},
        ]
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=rows)
        )

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = table_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import get_user_tickets

            result = await get_user_tickets(12345, limit=5)

        assert len(result) == 2
        assert result[0]["ticket_number"] == "SC-00002"

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_tickets(self):
        table_mock = MagicMock()
        table_mock.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[])
        )

        supabase_mock = MagicMock()
        supabase_mock.table.return_value = table_mock

        with patch("bot.db.get_supabase_client", return_value=supabase_mock):
            from bot.db import get_user_tickets

            result = await get_user_tickets(99999)

        assert result == []


# --- Handler tests ---


def _make_message(user_id: int = 12345, text: str = "/feedback", chat_id: int = 12345) -> AsyncMock:
    """Helper to create a mock Message."""
    msg = AsyncMock()
    msg.from_user = MagicMock(id=user_id, username="testuser")
    msg.chat = MagicMock(id=chat_id)
    msg.text = text
    return msg


def _make_callback(user_id: int = 12345, data: str = "feedback_cat:bug", chat_id: int = 12345) -> AsyncMock:
    """Helper to create a mock CallbackQuery."""
    cb = AsyncMock()
    cb.from_user = MagicMock(id=user_id, username="testuser")
    cb.message = AsyncMock()
    cb.message.chat = MagicMock(id=chat_id)
    cb.data = data
    return cb


class TestFeedbackCommand:
    """Tests for /feedback command handler."""

    @pytest.mark.asyncio
    async def test_shows_category_keyboard(self):
        """/feedback → inline keyboard with Bug + Idea buttons."""
        msg = _make_message()
        membership = {"tenant_id": "tenant-abc", "tenants": {"name": "Test Biz"}}

        with patch(
            "bot.handlers.feedback.get_tenant_by_telegram_user",
            new_callable=AsyncMock,
            return_value=membership,
        ):
            from bot.handlers.feedback import handle_feedback

            await handle_feedback(msg)

        msg.answer.assert_called_once()
        call_kwargs = msg.answer.call_args
        # Should have reply_markup with inline keyboard
        assert "reply_markup" in call_kwargs.kwargs or (
            len(call_kwargs.args) > 1 if call_kwargs.args else False
        )

    @pytest.mark.asyncio
    async def test_requires_auth(self):
        """No tenant → 'not set up' message."""
        msg = _make_message()

        with patch(
            "bot.handlers.feedback.get_tenant_by_telegram_user",
            new_callable=AsyncMock,
            return_value=None,
        ):
            from bot.handlers.feedback import handle_feedback

            await handle_feedback(msg)

        msg.answer.assert_called_once()
        call_text = msg.answer.call_args[0][0]
        assert "not set up" in call_text.lower() or "start" in call_text.lower()


class TestFeedbackCategory:
    """Tests for category selection callback."""

    @pytest.mark.asyncio
    async def test_bug_enters_fsm_state(self):
        """Selecting bug sets FeedbackSG.waiting_for_description."""
        cb = _make_callback(data="feedback_cat:bug")
        state = AsyncMock(spec=FSMContext)
        membership = {"tenant_id": "tenant-abc", "tenants": {"name": "Test Biz"}}

        with patch(
            "bot.handlers.feedback.get_tenant_by_telegram_user",
            new_callable=AsyncMock,
            return_value=membership,
        ):
            from bot.handlers.feedback import handle_feedback_category

            await handle_feedback_category(cb, state)

        state.set_state.assert_called_once()
        state.update_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_stores_category_in_fsm(self):
        """FSM data should contain category, tenant_id, chat_id."""
        cb = _make_callback(data="feedback_cat:idea")
        state = AsyncMock(spec=FSMContext)
        membership = {"tenant_id": "tenant-abc", "tenants": {"name": "Test Biz"}}

        with patch(
            "bot.handlers.feedback.get_tenant_by_telegram_user",
            new_callable=AsyncMock,
            return_value=membership,
        ):
            from bot.handlers.feedback import handle_feedback_category

            await handle_feedback_category(cb, state)

        update_data_kwargs = state.update_data.call_args[1]
        assert update_data_kwargs["category"] == "idea"
        assert update_data_kwargs["tenant_id"] == "tenant-abc"


class TestFeedbackDescription:
    """Tests for description message handler."""

    @pytest.mark.asyncio
    async def test_creates_ticket(self):
        """DB insert called with correct data."""
        msg = _make_message(text="The approve button doesn't work")
        state = AsyncMock(spec=FSMContext)
        state.get_data.return_value = {
            "category": "bug",
            "tenant_id": "tenant-abc",
            "chat_id": 12345,
            "business_name": "Test Biz",
        }

        ticket_row = {
            "ticket_number": "SC-00001",
            "category": "bug",
            "description": "The approve button doesn't work",
        }

        with (
            patch(
                "bot.handlers.feedback.create_support_ticket",
                new_callable=AsyncMock,
                return_value=ticket_row,
            ) as mock_create,
            patch("bot.handlers.feedback.get_settings") as mock_settings,
        ):
            mock_settings.return_value.admin_telegram_user_id = 7560539974
            from bot.handlers.feedback import handle_feedback_description

            await handle_feedback_description(msg, state)

        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["category"] == "bug"
        assert call_kwargs["description"] == "The approve button doesn't work"
        assert call_kwargs["tenant_id"] == "tenant-abc"

    @pytest.mark.asyncio
    async def test_returns_ticket_number(self):
        """Response contains ticket number SC-XXXXX."""
        msg = _make_message(text="Something is wrong")
        state = AsyncMock(spec=FSMContext)
        state.get_data.return_value = {
            "category": "bug",
            "tenant_id": "tenant-abc",
            "chat_id": 12345,
            "business_name": "Test Biz",
        }

        with (
            patch(
                "bot.handlers.feedback.create_support_ticket",
                new_callable=AsyncMock,
                return_value={"ticket_number": "SC-00042"},
            ),
            patch("bot.handlers.feedback.get_settings") as mock_settings,
        ):
            mock_settings.return_value.admin_telegram_user_id = 7560539974
            from bot.handlers.feedback import handle_feedback_description

            await handle_feedback_description(msg, state)

        call_text = msg.answer.call_args[0][0]
        assert "SC-00042" in call_text

    @pytest.mark.asyncio
    async def test_sends_admin_alert(self):
        """bot.send_message called with admin_user_id."""
        msg = _make_message(text="Bug report text")
        msg.bot = AsyncMock()
        state = AsyncMock(spec=FSMContext)
        state.get_data.return_value = {
            "category": "bug",
            "tenant_id": "tenant-abc",
            "chat_id": 12345,
            "business_name": "Test Biz",
        }

        with (
            patch(
                "bot.handlers.feedback.create_support_ticket",
                new_callable=AsyncMock,
                return_value={"ticket_number": "SC-00001"},
            ),
            patch("bot.handlers.feedback.get_settings") as mock_settings,
        ):
            mock_settings.return_value.admin_telegram_user_id = 7560539974
            from bot.handlers.feedback import handle_feedback_description

            await handle_feedback_description(msg, state)

        msg.bot.send_message.assert_called_once()
        admin_call = msg.bot.send_message.call_args
        assert admin_call.kwargs.get("chat_id") == 7560539974 or admin_call.args[0] == 7560539974

    @pytest.mark.asyncio
    async def test_cancel_clears_state(self):
        """/cancel in description state → clean exit."""
        msg = _make_message(text="/cancel")
        state = AsyncMock(spec=FSMContext)

        from bot.handlers.feedback import handle_feedback_cancel

        await handle_feedback_cancel(msg, state)

        state.clear.assert_called_once()
        msg.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_rejected(self):
        """Blank/whitespace text → retry prompt, no ticket created."""
        msg = _make_message(text="   ")
        state = AsyncMock(spec=FSMContext)
        state.get_data.return_value = {"category": "bug"}

        with patch(
            "bot.handlers.feedback.create_support_ticket",
            new_callable=AsyncMock,
        ) as mock_create:
            from bot.handlers.feedback import handle_feedback_description

            await handle_feedback_description(msg, state)

        mock_create.assert_not_called()
        msg.answer.assert_called_once()
        assert "describe" in msg.answer.call_args[0][0].lower() or "empty" in msg.answer.call_args[0][0].lower()


class TestTicketLookup:
    """Tests for /ticket command."""

    @pytest.mark.asyncio
    async def test_shows_status(self):
        """/ticket SC-00001 → status display."""
        msg = _make_message(text="/ticket SC-00001")
        membership = {"tenant_id": "tenant-abc"}
        ticket = {
            "ticket_number": "SC-00001",
            "category": "bug",
            "status": "open",
            "description": "Button broken",
            "admin_response": None,
            "created_at": "2026-03-24T01:00:00Z",
        }

        with (
            patch(
                "bot.handlers.feedback.get_tenant_by_telegram_user",
                new_callable=AsyncMock,
                return_value=membership,
            ),
            patch(
                "bot.handlers.feedback.get_support_ticket_by_number",
                new_callable=AsyncMock,
                return_value=ticket,
            ),
        ):
            from bot.handlers.feedback import handle_ticket

            await handle_ticket(msg)

        msg.answer.assert_called_once()
        text = msg.answer.call_args[0][0]
        assert "SC-00001" in text
        assert "open" in text.lower() or "Open" in text

    @pytest.mark.asyncio
    async def test_not_found(self):
        """Invalid ticket number → 'not found' message."""
        msg = _make_message(text="/ticket SC-99999")
        membership = {"tenant_id": "tenant-abc"}

        with (
            patch(
                "bot.handlers.feedback.get_tenant_by_telegram_user",
                new_callable=AsyncMock,
                return_value=membership,
            ),
            patch(
                "bot.handlers.feedback.get_support_ticket_by_number",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            from bot.handlers.feedback import handle_ticket

            await handle_ticket(msg)

        text = msg.answer.call_args[0][0]
        assert "not found" in text.lower() or "couldn't find" in text.lower()

    @pytest.mark.asyncio
    async def test_no_argument_lists_tickets(self):
        """/ticket alone → list recent tickets."""
        msg = _make_message(text="/ticket")
        membership = {"tenant_id": "tenant-abc"}
        tickets = [
            {"ticket_number": "SC-00002", "category": "idea", "status": "open",
             "description": "Add dark mode", "created_at": "2026-03-24T02:00:00Z"},
            {"ticket_number": "SC-00001", "category": "bug", "status": "resolved",
             "description": "Button broken", "created_at": "2026-03-24T01:00:00Z"},
        ]

        with (
            patch(
                "bot.handlers.feedback.get_tenant_by_telegram_user",
                new_callable=AsyncMock,
                return_value=membership,
            ),
            patch(
                "bot.handlers.feedback.get_user_tickets",
                new_callable=AsyncMock,
                return_value=tickets,
            ),
        ):
            from bot.handlers.feedback import handle_ticket

            await handle_ticket(msg)

        text = msg.answer.call_args[0][0]
        assert "SC-00002" in text
        assert "SC-00001" in text

    @pytest.mark.asyncio
    async def test_cross_tenant_blocked(self):
        """User can't view another tenant's ticket — tenant_id passed to lookup."""
        msg = _make_message(text="/ticket SC-00001")
        membership = {"tenant_id": "tenant-abc"}

        with (
            patch(
                "bot.handlers.feedback.get_tenant_by_telegram_user",
                new_callable=AsyncMock,
                return_value=membership,
            ),
            patch(
                "bot.handlers.feedback.get_support_ticket_by_number",
                new_callable=AsyncMock,
                return_value=None,  # Not found because wrong tenant
            ) as mock_lookup,
        ):
            from bot.handlers.feedback import handle_ticket

            await handle_ticket(msg)

        # Verify tenant_id was passed to scope the lookup
        mock_lookup.assert_called_once_with("SC-00001", tenant_id="tenant-abc")
