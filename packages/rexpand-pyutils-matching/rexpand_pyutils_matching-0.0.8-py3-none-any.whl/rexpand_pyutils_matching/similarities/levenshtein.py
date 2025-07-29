"""
Levenshtein (edit) distance based similarity scoring.
"""

from rexpand_pyutils_matching.utils.string import IGNORED_CHARS, normalize_string


def get_levenshtein_similarity(
    s1: str,
    s2: str,
    normalize: bool = True,
    ignored_chars: list[str] | None = IGNORED_CHARS,
) -> float:
    """
    Calculate similarity score based on Levenshtein distance.
    Score is normalized between 0 (completely different) and 1 (identical).

    Args:
        s1: First string
        s2: Second string
        normalize: Whether to normalize the strings before comparison
        ignored_chars: Characters to ignore when normalizing strings

    Returns:
        float: Similarity score between 0 and 1
    """
    if normalize:
        s1 = normalize_string(s1, ignored_chars)
        s2 = normalize_string(s2, ignored_chars)

    # Handle empty strings
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    # Calculate Levenshtein distance
    distance = get_levenshtein_distance(s1, s2)
    max_length = max(len(s1), len(s2))

    # Convert distance to similarity score
    return 1 - (distance / max_length)


def get_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein (edit) distance between two strings.
    The Levenshtein distance is the minimum number of single-character edits
    (insertions, deletions, or substitutions) required to change one string into another.
    """
    # Optimize for common cases
    if s1 == s2:
        return 0
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)

    # Ensure s1 is the shorter string for optimization
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    # Previous row of distances
    previous_row = range(len(s2) + 1)

    # Calculate current row distances from the previous row
    for i, c1 in enumerate(s1):
        # Initialize current row
        current_row = [i + 1]

        # Calculate new distances
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))

        # Set previous row to current row for next iteration
        previous_row = current_row

    return previous_row[-1]
