"""Tests for the system prompt builder."""

from __future__ import annotations

from pipeline.brand_voice import BrandProfile, FewShotExample
from pipeline.prompt_engine.asset_resolver import AssetManifest
from pipeline.prompt_engine.system_prompt import build_system_prompt


def _profile() -> BrandProfile:
    return BrandProfile(
        tenant_id="t1",
        name="Mondo Shrimp",
        tone_words=["bold", "playful", "irreverent"],
        audience_description="Foodies aged 25-45",
        do_list=["Use humor", "Reference signature sauce"],
        dont_list=["No generic food cliches"],
        product_catalog={"sauce": "Ghost Pepper Hot Sauce"},
    )


def _examples() -> list[FewShotExample]:
    return [
        FewShotExample(
            platform="instagram",
            content_type="product",
            caption="Stay Hungry, My Friends. #MondoShrimp",
        ),
    ]


def _manifest() -> AssetManifest:
    return AssetManifest(
        product_photos=["https://a.com/sauce.jpg", "https://a.com/sauce2.jpg"],
        people_photos=["https://a.com/owner.jpg"],
        other_photos=[],
        logo_url="https://a.com/logo.png",
    )


class TestBuildSystemPrompt:
    def test_contains_role_layer(self) -> None:
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "content strategist" in prompt.lower()

    def test_contains_format_rules(self) -> None:
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "IMAGE_POST" in prompt
        assert "SHORT_VIDEO" in prompt
        assert "LONG_VIDEO" in prompt

    def test_contains_scene_count_rules(self) -> None:
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "exactly 3" in prompt  # IMAGE_POST scene range
        assert "2-6" in prompt  # LONG_VIDEO scene range

    def test_contains_reference_image_strategy(self) -> None:
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "object_fidelity" in prompt
        assert "character_consistency" in prompt

    def test_contains_veo_mode_rules(self) -> None:
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "FIRST_AND_LAST_FRAMES" in prompt
        assert "TEXT_2_VIDEO" in prompt

    def test_contains_prompt_quality_rules(self) -> None:
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "cinematic" in prompt.lower()
        assert "text-in-scene" in prompt.lower() or "text in scene" in prompt.lower()

    def test_contains_brand_context(self) -> None:
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "Mondo Shrimp" in prompt
        assert "bold" in prompt
        assert "Stay Hungry" in prompt

    def test_contains_asset_manifest(self) -> None:
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "sauce.jpg" in prompt
        assert "owner.jpg" in prompt

    def test_contains_logo_info(self) -> None:
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "logo" in prompt.lower()

    def test_no_logo_when_none(self) -> None:
        manifest = AssetManifest(product_photos=[], people_photos=[], other_photos=[])
        prompt = build_system_prompt(_profile(), _examples(), manifest)
        assert "logo.png" not in prompt

    def test_empty_manifest(self) -> None:
        manifest = AssetManifest(product_photos=[], people_photos=[], other_photos=[])
        prompt = build_system_prompt(_profile(), _examples(), manifest)
        assert "No product photos" in prompt or "no product" in prompt.lower()

    def test_character_seed_scene_rule(self) -> None:
        """UGC two-pass strategy should be documented in system prompt."""
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "character_seed_scene" in prompt

    def test_contains_caption_quality_rules(self) -> None:
        """Caption rules must include storytelling frameworks."""
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        prompt_lower = prompt.lower()
        # Must have hook-story-offer (Brunson framework)
        assert "hook" in prompt_lower
        assert "story" in prompt_lower
        # Must have CTA guidance
        assert "call to action" in prompt_lower or "cta" in prompt_lower
        # Must explicitly ban corporate tone
        assert "corporate" in prompt_lower
        # Must require conversational/authentic voice
        assert "conversational" in prompt_lower or "authentic" in prompt_lower

    def test_caption_rules_have_hook_types(self) -> None:
        """Caption rules should specify proven hook types."""
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        prompt_lower = prompt.lower()
        # At least some hook archetypes present
        hook_types_found = sum(1 for h in [
            "question", "bold statement", "contrarian", "curiosity",
            "story open", "number", "urgency",
        ] if h in prompt_lower)
        assert hook_types_found >= 3, f"Only {hook_types_found} hook types found"

    def test_caption_rules_apply_to_all_formats(self) -> None:
        """Caption rules must apply to ALL content formats including video."""
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        prompt_lower = prompt.lower()
        assert "video" in prompt_lower and "caption" in prompt_lower

    def test_caption_rules_require_three_options(self) -> None:
        """Must instruct Claude to generate 3 caption options with different formulas."""
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        assert "3 caption" in prompt.lower() or "three caption" in prompt.lower()
        assert "different formula" in prompt.lower() or "unique formula" in prompt.lower()

    def test_contains_voice_style_guidance(self) -> None:
        """System prompt must instruct Claude on voice_style for videos."""
        prompt = build_system_prompt(_profile(), _examples(), _manifest())
        prompt_lower = prompt.lower()
        assert "voice_style" in prompt_lower
        assert "male" in prompt_lower or "female" in prompt_lower
        assert "gender" in prompt_lower
