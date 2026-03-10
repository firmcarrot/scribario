"""Tests for pipeline.brand_voice module."""

from pipeline.brand_voice import BrandProfile, FewShotExample, format_brand_context


def _make_profile(**overrides) -> BrandProfile:
    defaults = {
        "tenant_id": "test-tenant",
        "name": "Mondo Shrimp",
        "tone_words": ["bold", "fun", "spicy"],
        "audience_description": "Hot sauce enthusiasts aged 25-45",
        "do_list": ["Use fire emojis", "Mention heat levels"],
        "dont_list": ["Never say mild", "No health claims"],
        "product_catalog": {"sauces": ["Ghost Pepper", "Habanero", "Carolina Reaper"]},
        "compliance_notes": "No FDA health claims",
    }
    defaults.update(overrides)
    return BrandProfile(**defaults)


def _make_example(**overrides) -> FewShotExample:
    defaults = {
        "platform": "instagram",
        "content_type": "product_spotlight",
        "caption": "Our Ghost Pepper sauce just dropped! #HotSauce #MondoShrimp",
    }
    defaults.update(overrides)
    return FewShotExample(**defaults)


class TestFormatBrandContext:
    def test_includes_brand_name(self):
        profile = _make_profile()
        result = format_brand_context(profile, [])
        assert "Mondo Shrimp" in result

    def test_includes_tone_words(self):
        profile = _make_profile()
        result = format_brand_context(profile, [])
        assert "bold" in result
        assert "fun" in result
        assert "spicy" in result

    def test_includes_do_list(self):
        profile = _make_profile()
        result = format_brand_context(profile, [])
        assert "Use fire emojis" in result

    def test_includes_dont_list(self):
        profile = _make_profile()
        result = format_brand_context(profile, [])
        assert "Never say mild" in result

    def test_includes_compliance_notes(self):
        profile = _make_profile()
        result = format_brand_context(profile, [])
        assert "No FDA health claims" in result

    def test_includes_few_shot_examples(self):
        profile = _make_profile()
        examples = [_make_example()]
        result = format_brand_context(profile, examples)
        assert "Ghost Pepper sauce just dropped" in result
        assert "Example 1" in result

    def test_empty_examples(self):
        profile = _make_profile()
        result = format_brand_context(profile, [])
        assert "Example" not in result

    def test_empty_do_dont_lists(self):
        profile = _make_profile(do_list=[], dont_list=[])
        result = format_brand_context(profile, [])
        assert "DO:" not in result
        assert "DON'T:" not in result

    def test_no_compliance_notes(self):
        profile = _make_profile(compliance_notes="")
        result = format_brand_context(profile, [])
        assert "Compliance" not in result
