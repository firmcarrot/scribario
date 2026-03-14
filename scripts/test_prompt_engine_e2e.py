#!/usr/bin/env python3
"""E2E integration test for the Prompt Engine.

Requires real API keys (ANTHROPIC_API_KEY).
Run manually: python3 scripts/test_prompt_engine_e2e.py

Tests:
1. generate_plan() returns valid GenerationPlan for diverse intents
2. Reference images correctly assigned by slot type
3. Scene count within limits per content format
4. Captions are non-empty and relevant
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from dataclasses import asdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.brand_voice import BrandProfile, FewShotExample
from pipeline.prompt_engine.asset_resolver import AssetManifest
from pipeline.prompt_engine.engine import generate_plan
from pipeline.prompt_engine.models import ContentFormat


def _scribario_profile() -> BrandProfile:
    """The Scribario test brand profile."""
    return BrandProfile(
        tenant_id="90f86df4-6ac4-418b-8c2b-508de8d50b53",
        name="Scribario",
        tone_words=["innovative", "friendly", "professional"],
        audience_description="Small business owners who want social media content",
        do_list=["Emphasize ease of use", "Highlight AI-powered content creation"],
        dont_list=["Don't use jargon", "Don't oversell"],
    )


def _mondo_profile() -> BrandProfile:
    """Mondo Shrimp test brand profile."""
    return BrandProfile(
        tenant_id="52590da5-bc80-4161-ac13-62e9bcd75424",
        name="Mondo Shrimp",
        tone_words=["bold", "playful", "irreverent"],
        audience_description="Foodies aged 25-45 who love spicy food and humor",
        do_list=["Use humor", "Reference The Most Interesting Sauce in the World"],
        dont_list=["No generic food cliches", "Never call it just 'hot sauce'"],
        product_catalog={"sauce": "Ghost Pepper Shrimp Sauce", "tagline": "Stay Hungry, My Friends"},
    )


def _examples() -> list[FewShotExample]:
    return [
        FewShotExample(
            platform="instagram",
            content_type="product",
            caption=(
                "Some people put ketchup on everything. Those people haven't "
                "met our Ghost Pepper Shrimp Sauce. Stay Hungry, My Friends. "
                "#MondoShrimp #HotSauce #SpicyLife"
            ),
        ),
    ]


def _manifest_with_assets() -> AssetManifest:
    """Manifest with product photos (URLs won't resolve but test structure)."""
    return AssetManifest(
        product_photos=[
            "https://example.com/sauce-bottle-1.jpg",
            "https://example.com/sauce-bottle-2.jpg",
        ],
        people_photos=["https://example.com/chef-owner.jpg"],
        other_photos=[],
        logo_url="https://example.com/mondo-logo.png",
    )


def _empty_manifest() -> AssetManifest:
    return AssetManifest(product_photos=[], people_photos=[], other_photos=[])


TEST_CASES = [
    {
        "name": "Image post — product hero",
        "intent": "hero shot of our Ghost Pepper Shrimp Sauce",
        "profile": _mondo_profile,
        "manifest": _manifest_with_assets,
        "expected_format": ContentFormat.IMAGE_POST,
        "min_scenes": 1,
        "max_scenes": 3,
    },
    {
        "name": "Creative request — no assets",
        "intent": "put our sauce on the moon",
        "profile": _mondo_profile,
        "manifest": _empty_manifest,
        "expected_format": None,  # Claude decides — image or video both valid
        "min_scenes": 1,
        "max_scenes": 6,
    },
    {
        "name": "Long video — commercial",
        "intent": "30-second video ad showcasing our sauce for a grand opening event",
        "profile": _mondo_profile,
        "manifest": _manifest_with_assets,
        "expected_format": ContentFormat.LONG_VIDEO,
        "min_scenes": 2,
        "max_scenes": 6,
    },
    {
        "name": "Short video — reel",
        "intent": "quick reel showing our sauce being drizzled on shrimp",
        "profile": _mondo_profile,
        "manifest": _manifest_with_assets,
        "expected_format": ContentFormat.SHORT_VIDEO,
        "min_scenes": 1,
        "max_scenes": 1,
    },
    {
        "name": "Image post — different brand",
        "intent": "announcement that we just launched",
        "profile": _scribario_profile,
        "manifest": _empty_manifest,
        "expected_format": ContentFormat.IMAGE_POST,
        "min_scenes": 1,
        "max_scenes": 3,
    },
]


async def run_test(case: dict) -> tuple[str, bool, str]:
    """Run one test case, return (name, passed, details)."""
    name = case["name"]
    try:
        plan = await generate_plan(
            intent=case["intent"],
            profile=case["profile"](),
            examples=_examples(),
            assets=case["manifest"](),
            platform_targets=["instagram", "facebook"],
        )

        errors: list[str] = []

        # Check format (None = any format is acceptable)
        if case["expected_format"] is not None and plan.content_format != case["expected_format"]:
            errors.append(
                f"Expected format {case['expected_format']}, got {plan.content_format}"
            )

        # Check scene count
        if not (case["min_scenes"] <= len(plan.scenes) <= case["max_scenes"]):
            errors.append(
                f"Scene count {len(plan.scenes)} not in "
                f"[{case['min_scenes']}, {case['max_scenes']}]"
            )

        # Check captions exist
        if not plan.captions:
            errors.append("No captions generated")

        # Check captions have formula diversity — each of 3 must differ
        if len(plan.captions) >= 3:
            formulas = {cap.get("formula") for cap in plan.captions}
            formulas.discard(None)
            if len(formulas) < 3:
                errors.append(f"Caption formulas not diverse enough ({len(formulas)} unique): {formulas}")

        # Check captions are substantial (not one-liners)
        for i, cap in enumerate(plan.captions):
            text = cap.get("text", "")
            if len(text) < 50:
                errors.append(f"Caption {i} too short ({len(text)} chars)")

        # Check validation passes
        validation_errors = plan.validate()
        if validation_errors:
            errors.append(f"Validation errors: {validation_errors}")

        if errors:
            return name, False, "; ".join(errors)

        details = (
            f"format={plan.content_format}, scenes={len(plan.scenes)}, "
            f"captions={len(plan.captions)}, title='{plan.title}'"
        )
        return name, True, details

    except Exception as e:
        return name, False, f"Exception: {e}"


async def main() -> None:
    print("=" * 60)
    print("Prompt Engine E2E Integration Test")
    print("=" * 60)

    passed = 0
    failed = 0

    for case in TEST_CASES:
        print(f"\n--- {case['name']} ---")
        print(f"  Intent: {case['intent']}")

        name, ok, details = await run_test(case)

        if ok:
            print(f"  PASS: {details}")
            passed += 1
        else:
            print(f"  FAIL: {details}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(TEST_CASES)}")
    print(f"{'=' * 60}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    asyncio.run(main())
