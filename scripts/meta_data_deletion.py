"""Meta Data Deletion Callback — parse, verify, and respond.

Used by connect_server.py to handle POST /meta/data-deletion.
Meta sends a signed_request when a user deauthorizes the app.
We verify the HMAC, log the request, and return a confirmation.

Spec: https://developers.facebook.com/docs/development/create-an-app/app-dashboard/data-deletion-callback
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import uuid

logger = logging.getLogger(__name__)


def parse_signed_request(signed_request: str, app_secret: str) -> dict | None:
    """Parse and verify a Meta signed_request.

    Returns the payload dict if valid, None if verification fails.
    """
    try:
        parts = signed_request.split(".", 1)
        if len(parts) != 2:
            return None

        encoded_sig, payload_b64 = parts

        # Verify HMAC-SHA256
        expected_sig = hmac.new(
            app_secret.encode(), payload_b64.encode(), hashlib.sha256
        ).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")

        if not hmac.compare_digest(encoded_sig, expected_sig_b64):
            logger.warning("Meta signed_request signature mismatch")
            return None

        # Decode payload (add padding back)
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding

        payload_json = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_json)

    except Exception:
        logger.exception("Failed to parse Meta signed_request")
        return None


def generate_confirmation_code() -> str:
    """Generate a random, URL-safe confirmation code."""
    return uuid.uuid4().hex[:12]


def build_deletion_response(confirmation_code: str) -> dict:
    """Build the JSON response Meta expects from a data deletion callback.

    Returns: {"url": "https://scribario.com/data-deletion-status?code=XXX", "confirmation_code": "XXX"}
    """
    return {
        "url": f"https://scribario.com/data-deletion-status?code={confirmation_code}",
        "confirmation_code": confirmation_code,
    }
