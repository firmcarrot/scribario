"""Tests for Meta Data Deletion Callback endpoint."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

import pytest


def _make_signed_request(payload: dict, secret: str) -> str:
    """Create a Meta-style signed_request for testing."""
    payload_json = json.dumps(payload).encode()
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode().rstrip("=")

    sig = hmac.new(
        secret.encode(), payload_b64.encode(), hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")

    return f"{sig_b64}.{payload_b64}"


class TestSignedRequestParsing:
    """parse_signed_request verifies HMAC and extracts payload."""

    def test_valid_signed_request(self):
        from scripts.meta_data_deletion import parse_signed_request

        payload = {"user_id": "12345", "issued_at": int(time.time()), "algorithm": "HMAC-SHA256"}
        signed = _make_signed_request(payload, "test_secret")

        result = parse_signed_request(signed, "test_secret")
        assert result is not None
        assert result["user_id"] == "12345"

    def test_invalid_signature_returns_none(self):
        from scripts.meta_data_deletion import parse_signed_request

        payload = {"user_id": "12345", "algorithm": "HMAC-SHA256"}
        signed = _make_signed_request(payload, "correct_secret")

        result = parse_signed_request(signed, "wrong_secret")
        assert result is None

    def test_malformed_request_returns_none(self):
        from scripts.meta_data_deletion import parse_signed_request

        result = parse_signed_request("not.valid.format", "secret")
        assert result is None

    def test_empty_string_returns_none(self):
        from scripts.meta_data_deletion import parse_signed_request

        result = parse_signed_request("", "secret")
        assert result is None


class TestGenerateConfirmationCode:
    """generate_confirmation_code returns deterministic, URL-safe codes."""

    def test_returns_string(self):
        from scripts.meta_data_deletion import generate_confirmation_code

        code = generate_confirmation_code("12345")
        assert isinstance(code, str)
        assert len(code) > 0

    def test_deterministic(self):
        from scripts.meta_data_deletion import generate_confirmation_code

        code1 = generate_confirmation_code("12345")
        code2 = generate_confirmation_code("12345")
        assert code1 == code2

    def test_different_users_different_codes(self):
        from scripts.meta_data_deletion import generate_confirmation_code

        code1 = generate_confirmation_code("111")
        code2 = generate_confirmation_code("222")
        assert code1 != code2


class TestBuildDeletionResponse:
    """build_deletion_response returns correct JSON structure."""

    def test_response_shape(self):
        from scripts.meta_data_deletion import build_deletion_response

        resp = build_deletion_response("12345")
        assert "url" in resp
        assert "confirmation_code" in resp
        assert "scribario.com/data-deletion-status" in resp["url"]
        assert resp["confirmation_code"] in resp["url"]

    def test_contains_code_in_url(self):
        from scripts.meta_data_deletion import build_deletion_response

        resp = build_deletion_response("12345")
        assert f"code={resp['confirmation_code']}" in resp["url"]
