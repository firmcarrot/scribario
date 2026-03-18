"""Tests for pipeline.learning.structural_diff module."""

from __future__ import annotations

from pipeline.learning.structural_diff import (
    CaptionFeatures,
    _bucket_word_count,
    compute_pairwise_diff,
    extract_features,
)


class TestExtractFeatures:
    def test_basic_text(self):
        caption = {"text": "Hello world! How are you?", "formula": "hook_story_offer"}
        f = extract_features(caption)
        assert f.word_count == 5
        assert f.char_count == len("Hello world! How are you?")
        assert f.formula == "hook_story_offer"
        assert f.exclamation_count == 1
        assert f.question_mark_count == 1
        assert f.hashtag_count == 0
        assert f.has_emoji is False
        assert f.emoji_count == 0

    def test_empty_caption(self):
        caption = {"text": "", "formula": "punchy_one_liner"}
        f = extract_features(caption)
        assert f.word_count == 0
        assert f.char_count == 0
        assert f.sentence_count == 1  # max(0, 1) = 1
        assert f.avg_sentence_length == 0.0

    def test_caption_with_emojis(self):
        caption = {"text": "Fire sale today! \U0001f525\U0001f525\U0001f389", "formula": "test"}
        f = extract_features(caption)
        assert f.has_emoji is True
        assert f.emoji_count == 3

    def test_no_formula_defaults_to_unknown(self):
        caption = {"text": "Just some text."}
        f = extract_features(caption)
        assert f.formula == "unknown"

    def test_hashtag_counting(self):
        caption = {"text": "Big sale! #deals #hot #summer #fun #sale", "formula": "test"}
        f = extract_features(caption)
        assert f.hashtag_count == 5

    def test_sentence_counting(self):
        caption = {
            "text": "First sentence. Second sentence! Third sentence?",
            "formula": "test",
        }
        f = extract_features(caption)
        assert f.sentence_count == 3

    def test_avg_sentence_length(self):
        caption = {"text": "Hello world. Foo bar baz.", "formula": "test"}
        f = extract_features(caption)
        # 5 words, 2 sentences => 2.5
        assert f.avg_sentence_length == 2.5

    def test_missing_text_key(self):
        caption = {"formula": "test"}
        f = extract_features(caption)
        assert f.word_count == 0
        assert f.char_count == 0


class TestBucketWordCount:
    def test_short(self):
        assert _bucket_word_count(0) == "short"
        assert _bucket_word_count(30) == "short"

    def test_medium(self):
        assert _bucket_word_count(31) == "medium"
        assert _bucket_word_count(80) == "medium"

    def test_long(self):
        assert _bucket_word_count(81) == "long"
        assert _bucket_word_count(200) == "long"


class TestComputePairwiseDiff:
    def _make_features(self, **overrides: object) -> CaptionFeatures:
        defaults = {
            "word_count": 50,
            "char_count": 250,
            "formula": "hook_story_offer",
            "has_emoji": True,
            "emoji_count": 2,
            "exclamation_count": 1,
            "question_mark_count": 0,
            "hashtag_count": 1,
            "sentence_count": 3,
            "avg_sentence_length": 16.7,
        }
        defaults.update(overrides)
        return CaptionFeatures(**defaults)  # type: ignore[arg-type]

    def test_empty_rejected_returns_empty(self):
        chosen = self._make_features()
        assert compute_pairwise_diff(chosen, []) == {}

    def test_different_formula_appears_in_diff(self):
        chosen = self._make_features(formula="hook_story_offer")
        rejected = [
            self._make_features(formula="punchy_one_liner"),
            self._make_features(formula="problem_agitate_solution"),
        ]
        diffs = compute_pairwise_diff(chosen, rejected)
        assert diffs["formula"] == "hook_story_offer"

    def test_matching_formula_not_in_diff(self):
        chosen = self._make_features(formula="hook_story_offer")
        rejected = [
            self._make_features(formula="hook_story_offer"),  # same!
            self._make_features(formula="punchy_one_liner"),
        ]
        diffs = compute_pairwise_diff(chosen, rejected)
        assert "formula" not in diffs

    def test_word_count_bucket_diff(self):
        chosen = self._make_features(word_count=20)  # short
        rejected = [
            self._make_features(word_count=50),  # medium
            self._make_features(word_count=90),  # long
        ]
        diffs = compute_pairwise_diff(chosen, rejected)
        assert diffs["word_count_bucket"] == "short"

    def test_word_count_bucket_same_not_in_diff(self):
        chosen = self._make_features(word_count=20)  # short
        rejected = [
            self._make_features(word_count=25),  # also short
        ]
        diffs = compute_pairwise_diff(chosen, rejected)
        assert "word_count_bucket" not in diffs

    def test_emoji_diff(self):
        chosen = self._make_features(has_emoji=True)
        rejected = [self._make_features(has_emoji=False)]
        diffs = compute_pairwise_diff(chosen, rejected)
        assert diffs["emoji"] == "has_emoji"

    def test_no_emoji_diff(self):
        chosen = self._make_features(has_emoji=False)
        rejected = [self._make_features(has_emoji=True)]
        diffs = compute_pairwise_diff(chosen, rejected)
        assert diffs["emoji"] == "no_emoji"

    def test_question_hook_diff(self):
        chosen = self._make_features(question_mark_count=2)
        rejected = [self._make_features(question_mark_count=0)]
        diffs = compute_pairwise_diff(chosen, rejected)
        assert diffs["question_hook"] == "uses_question"

    def test_exclamation_diff(self):
        chosen = self._make_features(exclamation_count=3)
        rejected = [
            self._make_features(exclamation_count=0),
            self._make_features(exclamation_count=0),
        ]
        diffs = compute_pairwise_diff(chosen, rejected)
        assert diffs["exclamation"] == "has_exclamation"

    def test_hashtag_density_diff(self):
        chosen = self._make_features(hashtag_count=5)  # > 3 = many
        rejected = [self._make_features(hashtag_count=1)]  # <= 3 = few
        diffs = compute_pairwise_diff(chosen, rejected)
        assert diffs["hashtag_density"] == "many_hashtags"

    def test_multiple_diffs_at_once(self):
        chosen = self._make_features(
            word_count=10,
            formula="punchy_one_liner",
            has_emoji=False,
            question_mark_count=0,
            exclamation_count=0,
            hashtag_count=0,
        )
        rejected = [
            self._make_features(
                word_count=90,
                formula="hook_story_offer",
                has_emoji=True,
                question_mark_count=2,
                exclamation_count=3,
                hashtag_count=5,
            ),
        ]
        diffs = compute_pairwise_diff(chosen, rejected)
        assert "word_count_bucket" in diffs
        assert "formula" in diffs
        assert "emoji" in diffs
        assert "question_hook" in diffs
        assert "exclamation" in diffs
        assert "hashtag_density" in diffs
