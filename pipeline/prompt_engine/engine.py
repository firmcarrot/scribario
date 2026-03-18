"""Prompt Engine core — generates a complete GenerationPlan via Claude tool_use."""

from __future__ import annotations

import logging

import anthropic

from bot.config import get_settings
from pipeline.brand_voice import BrandProfile, FewShotExample
from pipeline.prompt_engine.asset_resolver import AssetManifest
from pipeline.prompt_engine.models import (
    AnimationPrompt,
    CompositeInstruction,
    ContentFormat,
    FramePrompt,
    GenerationPlan,
    RefImageAssignment,
    RefSlotType,
    ScenePlan,
    VeoMode,
)
from pipeline.prompt_engine.system_prompt import build_system_prompt

logger = logging.getLogger(__name__)

ENGINE_COST_USD = 0.04  # Approximate per-call cost for Sonnet

# The tool definition that forces Claude to return structured output.
_TOOL_SCHEMA = {
    "name": "create_generation_plan",
    "description": (
        "Create a complete content generation plan. This tool MUST be called "
        "with the full plan — do not return text instead."
    ),
    "input_schema": {
        "type": "object",
        "required": [
            "content_format", "title", "concept_summary", "scenes", "captions",
        ],
        "properties": {
            "content_format": {
                "type": "string",
                "enum": ["image_post", "short_video", "long_video"],
            },
            "title": {"type": "string"},
            "concept_summary": {"type": "string"},
            "voice_style": {"type": ["string", "null"]},
            "aspect_ratio": {"type": "string", "default": "16:9"},
            "transition_style": {"type": "string", "default": "fade"},
            "scenes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["index", "scene_type", "duration_seconds", "start_frame"],
                    "properties": {
                        "index": {"type": "integer"},
                        "scene_type": {"type": "string"},
                        "duration_seconds": {"type": "number"},
                        "start_frame": {"$ref": "#/$defs/frame_prompt"},
                        "end_frame": {
                            "oneOf": [{"$ref": "#/$defs/frame_prompt"}, {"type": "null"}],
                        },
                        "animation": {
                            "oneOf": [{"$ref": "#/$defs/animation_prompt"}, {"type": "null"}],
                        },
                        "voiceover_text": {"type": ["string", "null"]},
                        "sfx_description": {"type": ["string", "null"]},
                        "camera_direction": {"type": ["string", "null"]},
                        "composite": {"$ref": "#/$defs/composite_instruction"},
                        "character_seed_scene": {"type": "boolean", "default": False},
                    },
                },
            },
            "captions": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "required": ["text", "platform_variant", "formula"],
                    "properties": {
                        "text": {"type": "string"},
                        "platform_variant": {"type": "string"},
                        "formula": {
                            "type": "string",
                            "enum": [
                                "hook_story_offer",
                                "problem_agitate_solution",
                                "punchy_one_liner",
                                "story_lesson",
                                "list_value_drop",
                            ],
                            "description": "Which copywriting formula was used. Each caption MUST use a different formula.",
                        },
                    },
                },
            },
        },
        "$defs": {
            "frame_prompt": {
                "type": "object",
                "required": ["prompt", "aspect_ratio", "reference_images"],
                "properties": {
                    "prompt": {"type": "string"},
                    "aspect_ratio": {"type": "string"},
                    "reference_images": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["asset_url", "slot_type"],
                            "properties": {
                                "asset_url": {"type": "string"},
                                "slot_type": {
                                    "type": "string",
                                    "enum": ["object_fidelity", "character_consistency"],
                                },
                            },
                        },
                    },
                },
            },
            "animation_prompt": {
                "type": "object",
                "required": ["prompt", "veo_mode"],
                "properties": {
                    "prompt": {"type": "string"},
                    "veo_mode": {
                        "type": "string",
                        "enum": [
                            "TEXT_2_VIDEO",
                            "FIRST_AND_LAST_FRAMES_2_VIDEO",
                            "REFERENCE_2_VIDEO",
                        ],
                    },
                    "aspect_ratio": {"type": "string", "default": "16:9"},
                },
            },
            "composite_instruction": {
                "type": "object",
                "properties": {
                    "logo_overlay": {"type": "boolean", "default": False},
                    "logo_position": {"type": "string", "default": "bottom_right"},
                    "logo_opacity": {"type": "number", "default": 0.7},
                    "text_overlay": {"type": ["string", "null"]},
                    "text_position": {"type": "string", "default": "bottom_center"},
                },
            },
        },
    },
}


def _parse_tool_response(response: object) -> GenerationPlan:
    """Parse Claude's tool_use response into a validated GenerationPlan.

    Raises:
        ValueError: If response has no tool_use block or validation fails.
    """
    tool_input = None
    for block in response.content:
        if block.type == "tool_use" and block.name == "create_generation_plan":
            tool_input = block.input
            break

    if tool_input is None:
        raise ValueError(
            "Claude did not return a tool_use block. "
            f"Stop reason: {response.stop_reason}"
        )

    # Parse scenes
    scenes: list[ScenePlan] = []
    for s in tool_input["scenes"]:
        start_frame = _parse_frame(s["start_frame"])
        end_frame = _parse_frame(s["end_frame"]) if s.get("end_frame") else None
        animation = _parse_animation(s["animation"]) if s.get("animation") else None
        composite = _parse_composite(s.get("composite"))

        scenes.append(ScenePlan(
            index=s["index"],
            scene_type=s["scene_type"],
            duration_seconds=s["duration_seconds"],
            start_frame=start_frame,
            end_frame=end_frame,
            animation=animation,
            voiceover_text=s.get("voiceover_text"),
            sfx_description=s.get("sfx_description"),
            camera_direction=s.get("camera_direction"),
            composite=composite,
            character_seed_scene=s.get("character_seed_scene", False),
        ))

    plan = GenerationPlan(
        content_format=ContentFormat(tool_input["content_format"]),
        title=tool_input["title"],
        concept_summary=tool_input["concept_summary"],
        scenes=scenes,
        captions=tool_input.get("captions", []),
        voice_style=tool_input.get("voice_style"),
        aspect_ratio=tool_input.get("aspect_ratio", "16:9"),
        transition_style=tool_input.get("transition_style", "fade"),
    )

    # Validate
    errors = plan.validate()
    if errors:
        raise ValueError(f"GenerationPlan validation failed: {'; '.join(errors)}")

    return plan


def _parse_frame(data: dict) -> FramePrompt:
    refs = [
        RefImageAssignment(
            asset_url=r["asset_url"],
            slot_type=RefSlotType(r["slot_type"]),
        )
        for r in data.get("reference_images", [])
    ]
    return FramePrompt(
        prompt=data["prompt"],
        aspect_ratio=data.get("aspect_ratio", "16:9"),
        reference_images=refs,
    )


def _parse_animation(data: dict) -> AnimationPrompt:
    return AnimationPrompt(
        prompt=data["prompt"],
        veo_mode=VeoMode(data["veo_mode"]),
        aspect_ratio=data.get("aspect_ratio", "16:9"),
    )


def _parse_composite(data: dict | None) -> CompositeInstruction:
    if not data:
        return CompositeInstruction()
    return CompositeInstruction(
        logo_overlay=data.get("logo_overlay", False),
        logo_position=data.get("logo_position", "bottom_right"),
        logo_opacity=data.get("logo_opacity", 0.7),
        text_overlay=data.get("text_overlay"),
        text_position=data.get("text_position", "bottom_center"),
    )


async def _build_formula_performance_block(tenant_id: str) -> tuple[str, list[str] | None]:
    """Build formula performance prompt block and wildcard formula assignments.

    Returns:
        (prompt_block, formula_assignments) where formula_assignments is
        [formula1, formula2, wildcard_formula] or None if insufficient data.
    """
    try:
        from pipeline.learning.formula_tracker import get_formula_stats
        import random

        stats = await get_formula_stats(tenant_id)
        if not stats:
            return "", None

        # Sort by engagement (if available) then approval rate
        def sort_key(fs):  # noqa: ANN001, ANN202
            eng = fs.avg_engagement if fs.avg_engagement is not None else 0.0
            return (eng, fs.approval_rate)

        sorted_stats = sorted(stats.values(), key=sort_key, reverse=True)

        # Build prompt block
        parts = ["## Formula Performance (from your history):"]
        for i, fs in enumerate(sorted_stats, 1):
            eng_str = f"{fs.avg_engagement}/10" if fs.avg_engagement else "n/a"
            parts.append(
                f"{i}. {fs.formula} — {eng_str} audience engagement, "
                f"{fs.approval_rate:.0%} approval ({fs.sample_size} posts)"
            )

        # Wildcard enforcement (Phase 5C / DA fix I5): pre-assign formulas
        all_formulas = [
            "hook_story_offer", "problem_agitate_solution",
            "punchy_one_liner", "story_lesson", "list_value_drop",
        ]
        top_formulas = [fs.formula for fs in sorted_stats[:2]]

        if len(top_formulas) >= 2:
            wildcard_pool = [f for f in all_formulas if f not in top_formulas]
            wildcard = random.choice(wildcard_pool) if wildcard_pool else all_formulas[-1]
            assignments = [top_formulas[0], top_formulas[1], wildcard]

            parts.append("\nGenerate the 3 captions as follows:")
            parts.append(f"- Option 1: Use {top_formulas[0]}")
            parts.append(f"- Option 2: Use {top_formulas[1]}")
            parts.append(
                f"- Option 3: WILDCARD — use {wildcard} "
                "(break from the usual pattern)"
            )
            return "\n".join(parts), assignments

        return "\n".join(parts), None
    except Exception:
        logger.exception("Failed to build formula performance block")
        return "", None


async def generate_plan(
    intent: str,
    profile: BrandProfile,
    examples: list[FewShotExample],
    assets: AssetManifest,
    platform_targets: list[str] | None = None,
) -> GenerationPlan:
    """Generate a complete content plan using Claude Sonnet with tool_use.

    Args:
        intent: The user's content request.
        profile: Brand identity and voice rules.
        examples: Few-shot examples for brand voice.
        assets: Categorized reference assets for this tenant.
        platform_targets: Target platforms (or None for all).

    Returns:
        A validated GenerationPlan ready for pipeline consumption.

    Raises:
        ValueError: If Claude's response fails parsing or validation.
        anthropic.APIError: If the API call fails.
    """
    # Phase 3: Load learned preferences for Layer 11
    from pipeline.brand_voice import load_edit_lessons, load_learned_preferences

    learned_preferences = await load_learned_preferences(profile.tenant_id)
    edit_lessons = await load_edit_lessons(profile.tenant_id)
    formula_block, formula_assignments = await _build_formula_performance_block(
        profile.tenant_id
    )

    system_prompt = build_system_prompt(
        profile, examples, assets,
        learned_preferences=learned_preferences,
        edit_lessons=edit_lessons,
        formula_performance=formula_block,
    )
    platforms_str = (
        ", ".join(platform_targets) if platform_targets
        else "all connected platforms"
    )

    user_message = f"Create content for: {intent}\nTarget platforms: {platforms_str}\n\n"

    # Wildcard enforcement: pre-assign formulas in user message (DA fix I5)
    if formula_assignments and len(formula_assignments) == 3:
        user_message += (
            f"Caption 1 MUST use {formula_assignments[0]}. "
            f"Caption 2 MUST use {formula_assignments[1]}. "
            f"Caption 3 MUST use {formula_assignments[2]}.\n\n"
        )

    user_message += "Call the create_generation_plan tool with the complete plan."

    client = anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
        tools=[_TOOL_SCHEMA],
        tool_choice={"type": "tool", "name": "create_generation_plan"},
    )

    plan = _parse_tool_response(response)

    logger.info(
        "Generation plan created",
        extra={
            "title": plan.title,
            "format": plan.content_format,
            "scenes": len(plan.scenes),
            "captions": len(plan.captions),
            "intent": intent[:80],
        },
    )

    return plan
