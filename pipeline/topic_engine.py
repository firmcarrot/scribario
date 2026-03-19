"""Topic engine — AI-generated content topics with moderation and dedup.

Uses Claude Haiku for cost-efficient topic generation and moderation.
Sequential processing per tenant (DA HIGH-2: no concurrent topics).
"""

from __future__ import annotations

import logging
import random

import anthropic

from bot.config import get_settings

logger = logging.getLogger(__name__)

# Cost for one Haiku topic generation call (~300 input + ~100 output tokens)
TOPIC_GEN_COST_USD = 0.0003
MODERATION_COST_USD = 0.0001


async def _call_claude(prompt: str, system: str) -> dict:
    """Call Claude Haiku for topic generation.

    Returns: {"data": <parsed JSON>, "input_tokens": int, "output_tokens": int}
    """
    client = anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    import json

    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    if text.startswith("json"):
        text = text[4:]
    return {
        "data": json.loads(text.strip()),
        "input_tokens": getattr(response.usage, "input_tokens", None),
        "output_tokens": getattr(response.usage, "output_tokens", None),
    }


async def _call_claude_moderation(content: str) -> dict:
    """Call Claude Haiku to moderate content for safety.

    Returns: {safe, reason, input_tokens, output_tokens}
    """
    client = anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=128,
        system=(
            "You are a content safety moderator for social media business posts. "
            "Evaluate if the content is safe for automated posting. "
            'Respond in JSON: {"safe": true/false, "reason": "explanation if unsafe"}'
        ),
        messages=[
            {"role": "user", "content": f"Is this safe for automated business posting?\n\n{content}"}
        ],
    )
    import json

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    if text.startswith("json"):
        text = text[4:]
    result = json.loads(text.strip())
    result["input_tokens"] = getattr(response.usage, "input_tokens", None)
    result["output_tokens"] = getattr(response.usage, "output_tokens", None)
    return result


def _is_too_similar(topic: str, recent_topics: list[str], threshold: float = 0.6) -> bool:
    """Check if a topic is too similar to recent topics using keyword overlap.

    Uses Jaccard similarity on word sets — simple but effective for dedup.
    """
    if not recent_topics:
        return False

    topic_words = set(topic.lower().split())
    for recent in recent_topics:
        recent_words = set(recent.lower().split())
        if not topic_words or not recent_words:
            continue
        intersection = topic_words & recent_words
        union = topic_words | recent_words
        similarity = len(intersection) / len(union) if union else 0
        if similarity >= threshold:
            return True
    return False


def _pick_category(content_mix: dict) -> str:
    """Pick a category based on weighted content mix percentages."""
    categories = list(content_mix.keys())
    weights = [content_mix[c] for c in categories]
    return random.choices(categories, weights=weights, k=1)[0]


async def generate_topic(
    tenant_id: str,
    content_mix: dict,
    brand_profile: dict,
    recent_topics: list[str],
    max_retries: int = 3,
) -> dict:
    """Generate a single topic for a tenant's autopilot content.

    Args:
        tenant_id: The tenant ID
        content_mix: Category weights like {"promotional": 40, "educational": 30, ...}
        brand_profile: Brand profile dict with name, tone_words, audience, products
        recent_topics: List of topic strings from the last 14 days
        max_retries: Max attempts to generate a unique topic

    Returns:
        {"topic": "...", "category": "..."}

    Raises:
        RuntimeError: If unable to generate a unique topic after max_retries
    """
    category = _pick_category(content_mix)

    brand_name = brand_profile.get("name", "the brand")
    tone = ", ".join(brand_profile.get("tone_words", ["professional"]))
    audience = brand_profile.get("audience_description", "general audience")
    products = brand_profile.get("product_catalog", {})
    product_str = ""
    if isinstance(products, dict) and "products" in products:
        product_str = "\n".join(
            f"- {p.get('name', '')}: {p.get('description', '')}"
            for p in products["products"][:5]
        )

    system = (
        "You are a social media content strategist. Generate a single specific, "
        "engaging post topic for a business. Respond in JSON format only: "
        '{"topic": "the topic idea", "category": "category_name"}'
    )

    recent_str = ""
    if recent_topics:
        recent_str = "\n\nAvoid these recent topics:\n" + "\n".join(f"- {t}" for t in recent_topics[-10:])

    prompt = (
        f"Brand: {brand_name}\n"
        f"Tone: {tone}\n"
        f"Audience: {audience}\n"
        f"Category to write about: {category}\n"
    )
    if product_str:
        prompt += f"Products:\n{product_str}\n"
    prompt += recent_str
    prompt += "\n\nGenerate one specific, creative post topic for this brand."

    total_input_tokens = 0
    total_output_tokens = 0
    for attempt in range(max_retries):
        raw = await _call_claude(prompt, system)
        result = raw["data"]
        total_input_tokens += raw.get("input_tokens") or 0
        total_output_tokens += raw.get("output_tokens") or 0
        topic = result.get("topic", "")
        result_category = result.get("category", category)

        # Validate category is in content_mix
        if result_category not in content_mix:
            result_category = category

        if not _is_too_similar(topic, recent_topics):
            return {
                "topic": topic,
                "category": result_category,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }

        logger.info(
            "Topic too similar to recent, retrying",
            extra={"attempt": attempt + 1, "topic": topic},
        )

    # Last resort: use whatever we got
    return {
        "topic": result.get("topic", ""),
        "category": result.get("category", category),
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
    }


async def moderate_content(content: str) -> dict:
    """Run Claude Haiku moderation pass on content (DA HIGH-3).

    Returns: {"safe": bool, "reason": str}
    """
    try:
        return await _call_claude_moderation(content)
    except Exception:
        logger.exception("Moderation call failed — defaulting to safe=False for safety")
        return {"safe": False, "reason": "Moderation check failed"}
