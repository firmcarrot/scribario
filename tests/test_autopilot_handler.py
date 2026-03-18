"""Tests for autopilot Telegram command handler."""

from __future__ import annotations

import asyncio

import pytest


class TestAutopilotHandlerImports:
    """Verify autopilot handler module can be imported."""

    def test_router_exists(self):
        from bot.handlers.autopilot import router
        assert router is not None
        assert router.name == "autopilot"

    def test_handler_functions_exist(self):
        from bot.handlers import autopilot
        assert hasattr(autopilot, "handle_autopilot_command")
        assert hasattr(autopilot, "handle_setup_mode")
        assert hasattr(autopilot, "handle_setup_schedule")
        assert hasattr(autopilot, "handle_setup_platforms")
        assert hasattr(autopilot, "handle_pause")
        assert hasattr(autopilot, "handle_resume")
