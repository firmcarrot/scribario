from __future__ import annotations

import re
from dataclasses import dataclass

_EMOJI_PATTERN = re.compile(
    "[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff"
    "\U0001f1e0-\U0001f1ff\U00002702-\U000027b0\U0001f900-\U0001f9ff"
    "\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff\U00002600-\U000026ff]"
)

_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s|$)")


@dataclass
class CaptionFeatures:
    word_count: int
    char_count: int
    formula: str  # from caption_variants[].formula
    has_emoji: bool
    emoji_count: int
    exclamation_count: int
    question_mark_count: int
    hashtag_count: int
    sentence_count: int
    avg_sentence_length: float


def extract_features(caption: dict) -> CaptionFeatures:
    """Extract structural features from a caption variant dict.

    caption dict has keys: text, formula, platform_variant, possibly visual_prompt
    """
    text = caption.get("text", "")
    formula = caption.get("formula", "unknown")

    words = text.split()
    word_count = len(words)

    emojis = _EMOJI_PATTERN.findall(text)

    # Sentence counting: split on .!? followed by space or end
    sentences = _SENTENCE_SPLIT.split(text.strip())
    sentences = [s for s in sentences if s.strip()]
    sentence_count = max(len(sentences), 1)

    return CaptionFeatures(
        word_count=word_count,
        char_count=len(text),
        formula=formula,
        has_emoji=len(emojis) > 0,
        emoji_count=len(emojis),
        exclamation_count=text.count("!"),
        question_mark_count=text.count("?"),
        hashtag_count=text.count("#"),
        sentence_count=sentence_count,
        avg_sentence_length=round(word_count / sentence_count, 1) if sentence_count else 0.0,
    )


def _bucket_word_count(count: int) -> str:
    """Bucket word count into categories."""
    if count <= 30:
        return "short"
    elif count <= 80:
        return "medium"
    else:
        return "long"


def compute_pairwise_diff(
    chosen: CaptionFeatures,
    rejected: list[CaptionFeatures],
) -> dict[str, str]:
    """Compare chosen caption against all rejected ones.

    Returns dict of feature dimensions where the chosen option was
    DIFFERENT from ALL rejected options. If chosen matches any rejected
    on a dimension, that dimension is not discriminating.

    Example: {"word_count_bucket": "short", "formula": "hook_story_offer"}
    """
    if not rejected:
        return {}

    diffs: dict[str, str] = {}

    # Word count bucket
    chosen_bucket = _bucket_word_count(chosen.word_count)
    rejected_buckets = [_bucket_word_count(r.word_count) for r in rejected]
    if all(b != chosen_bucket for b in rejected_buckets):
        diffs["word_count_bucket"] = chosen_bucket

    # Formula
    rejected_formulas = [r.formula for r in rejected]
    if all(f != chosen.formula for f in rejected_formulas):
        diffs["formula"] = chosen.formula

    # Emoji presence
    rejected_emoji = [r.has_emoji for r in rejected]
    if all(e != chosen.has_emoji for e in rejected_emoji):
        diffs["emoji"] = "has_emoji" if chosen.has_emoji else "no_emoji"

    # Question marks (hook type proxy)
    chosen_has_q = chosen.question_mark_count > 0
    rejected_has_q = [r.question_mark_count > 0 for r in rejected]
    if all(q != chosen_has_q for q in rejected_has_q):
        diffs["question_hook"] = "uses_question" if chosen_has_q else "no_question"

    # Exclamation marks
    chosen_has_excl = chosen.exclamation_count > 0
    rejected_has_excl = [r.exclamation_count > 0 for r in rejected]
    if all(e != chosen_has_excl for e in rejected_has_excl):
        diffs["exclamation"] = "has_exclamation" if chosen_has_excl else "no_exclamation"

    # Hashtag density
    chosen_has_tags = chosen.hashtag_count > 3
    rejected_has_tags = [r.hashtag_count > 3 for r in rejected]
    if all(t != chosen_has_tags for t in rejected_has_tags):
        diffs["hashtag_density"] = "many_hashtags" if chosen_has_tags else "few_hashtags"

    return diffs
