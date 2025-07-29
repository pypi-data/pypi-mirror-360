"""
Core string matching utilities providing various string comparison and pattern matching algorithms.
"""

from enum import Enum

from .utils.string import normalize_string, IGNORED_CHARS
from .similarities.levenshtein import get_levenshtein_similarity
from .similarities.longest_common_sequence import (
    get_longest_common_sequence_similarity,
)
from .similarities.longest_consecutive_common_sequence import (
    get_longest_consecutive_common_sequence_similarity,
)
from .similarities.common_prefix import get_common_prefix_similarity
from .similarities.starts_with import get_starts_with_similarity
from .similarities.bert_score import get_bert_score_similarity


class SimilarityMeasure(Enum):
    """Enum for different similarity measures."""

    LEVENSHTEIN = "levenshtein"
    LONGEST_COMMON_SEQUENCE = "longest_common_sequence"
    LONGEST_CONSECUTIVE_COMMON_SEQUENCE = "longest_consecutive_common_sequence"
    COMMON_PREFIX = "common_prefix"
    STARTS_WITH = "starts_with"
    BERT_SCORE = "bert_score"


SIMILARITY_FUNCTIONS = {
    SimilarityMeasure.LEVENSHTEIN: get_levenshtein_similarity,
    SimilarityMeasure.LONGEST_COMMON_SEQUENCE: get_longest_common_sequence_similarity,
    SimilarityMeasure.LONGEST_CONSECUTIVE_COMMON_SEQUENCE: get_longest_consecutive_common_sequence_similarity,
    SimilarityMeasure.COMMON_PREFIX: get_common_prefix_similarity,
    SimilarityMeasure.STARTS_WITH: get_starts_with_similarity,
    SimilarityMeasure.BERT_SCORE: get_bert_score_similarity,
}


def exact_match(text: str, pattern: str, normalize: bool = True) -> bool:
    """
    Perform exact string matching.

    Args:
        text: The text to search in
        pattern: The pattern to search for
        normalize: Whether to normalize strings before comparison, default is True
    Returns:
        bool: True if pattern exactly matches text, False otherwise

    Examples:
        >>> exact_match("hello", "hello")
        True
        >>> exact_match("hello", "Hello")
        False
    """
    if normalize:
        text = normalize_string(text)
        pattern = normalize_string(pattern)

    return text == pattern


def fuzzy_match(
    text: str,
    pattern: str,
    threshold: float = 0.95,
    similarity_measure: SimilarityMeasure = SimilarityMeasure.COMMON_PREFIX,
    normalize: bool = True,
    ignored_chars: list[str] = IGNORED_CHARS,
    extra_params: dict = {},
) -> bool:
    """
    Perform fuzzy string matching using various similarity measures.

    Args:
        text: The text to search in
        pattern: The pattern to search for
        threshold: Similarity threshold (0.0 to 1.0), default is 0.8
        similarity_measure: The similarity measure to use, default is COMMON_PREFIX
        normalize: Whether to normalize strings before comparison, default is True
        ignored_chars: Characters to ignore when comparing strings
        extra_params: Additional parameters for the similarity measure

    Returns:
        bool: True if similarity >= threshold, False otherwise

    Examples:
        >>> fuzzy_match("hello", "helo", 0.8)
        True
        >>> fuzzy_match("python", "javascript", 0.8)
        False
        >>> fuzzy_match("hello world", "hello", 0.8, SimilarityMeasure.STARTS_WITH)
        True
    """

    similarity_func = SIMILARITY_FUNCTIONS[similarity_measure]
    similarity = similarity_func(
        text,
        pattern,
        normalize=normalize,
        ignored_chars=ignored_chars,
        **extra_params,
    )
    return similarity >= threshold
