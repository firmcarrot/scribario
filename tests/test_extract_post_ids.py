"""Tests for _extract_post_ids with actual Postiz response shapes."""

from __future__ import annotations

from pipeline.posting import _extract_post_ids


class TestExtractPostIdsPostizFormat:
    """Tests based on confirmed Postiz API response shape.

    Each post in the response has:
    - i: Postiz internal ID
    - u: platform URL (e.g., https://www.facebook.com/.../posts/...)
    - ri: platform native post ID
    - s: status
    - n.pi: platform identifier (nested in 'n' dict)
    """

    def test_single_post_dict_with_postiz_fields(self):
        """Postiz returns a dict with nested post data."""
        data = {
            "id": "post-group-123",
            "posts": [
                {
                    "i": "abc123",
                    "u": "https://www.facebook.com/12345/posts/67890",
                    "ri": "67890",
                    "s": "published",
                    "n": {"pi": "facebook", "id": "int-fb-456"},
                }
            ],
        }
        result = _extract_post_ids(data)
        assert result["facebook"] == "abc123"

    def test_multiple_posts_different_platforms(self):
        data = {
            "id": "post-group-456",
            "posts": [
                {
                    "i": "aaa111",
                    "u": "https://www.facebook.com/page/posts/111",
                    "ri": "111",
                    "s": "published",
                    "n": {"pi": "facebook"},
                },
                {
                    "i": "bbb222",
                    "u": "https://www.instagram.com/p/ABC123/",
                    "ri": "222",
                    "s": "published",
                    "n": {"pi": "instagram"},
                },
            ],
        }
        result = _extract_post_ids(data)
        assert result["facebook"] == "aaa111"
        assert result["instagram"] == "bbb222"

    def test_extracts_platform_urls(self):
        data = {
            "posts": [
                {
                    "i": "abc123",
                    "u": "https://www.facebook.com/page/posts/67890",
                    "ri": "67890",
                    "s": "published",
                    "n": {"pi": "facebook"},
                }
            ],
        }
        result = _extract_post_ids(data)
        assert result.get("facebook_url") == "https://www.facebook.com/page/posts/67890"

    def test_extracts_native_post_id(self):
        data = {
            "posts": [
                {
                    "i": "abc123",
                    "u": "https://www.facebook.com/page/posts/67890",
                    "ri": "67890",
                    "s": "published",
                    "n": {"pi": "facebook"},
                }
            ],
        }
        result = _extract_post_ids(data)
        assert result.get("facebook_native") == "67890"

    def test_post_missing_n_field(self):
        """Post without platform info still extracts by index."""
        data = {
            "posts": [
                {"i": "abc123", "u": "https://example.com/post/1", "ri": "1", "s": "published"}
            ],
        }
        result = _extract_post_ids(data)
        assert result["0"] == "abc123"

    def test_empty_posts_list(self):
        data = {"posts": []}
        result = _extract_post_ids(data)
        assert result == {}

    def test_post_missing_i_field(self):
        """If no 'i' field, try 'id' fallback."""
        data = {
            "posts": [
                {
                    "id": "fallback-id",
                    "u": "https://example.com/post/1",
                    "n": {"pi": "facebook"},
                }
            ],
        }
        result = _extract_post_ids(data)
        assert result.get("facebook") == "fallback-id"

    def test_array_response_with_postiz_fields(self):
        """Sometimes Postiz returns a flat array."""
        data = [
            {
                "i": "abc123",
                "u": "https://www.facebook.com/page/posts/67890",
                "ri": "67890",
                "s": "published",
                "n": {"pi": "facebook"},
            },
        ]
        result = _extract_post_ids(data)
        assert result["facebook"] == "abc123"

    def test_empty_dict(self):
        assert _extract_post_ids({}) == {}

    def test_empty_list(self):
        assert _extract_post_ids([]) == {}

    def test_none_input(self):
        assert _extract_post_ids(None) == {}
