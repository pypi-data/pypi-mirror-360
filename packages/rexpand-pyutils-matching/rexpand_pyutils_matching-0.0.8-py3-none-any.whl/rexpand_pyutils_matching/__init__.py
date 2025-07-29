"""
rexpand-pyutils-matching - Python utilities for string matching and pattern recognition
"""

__version__ = "0.0.8"

from .matchers import (
    exact_match,
    fuzzy_match,
    SimilarityMeasure,
    SIMILARITY_FUNCTIONS,
)
from .searcher import (
    fuzzy_search,
    search,
)

__all__ = [
    "exact_match",
    "fuzzy_match",
    "SimilarityMeasure",
    "SIMILARITY_FUNCTIONS",
    "fuzzy_search",
    "search",
]
