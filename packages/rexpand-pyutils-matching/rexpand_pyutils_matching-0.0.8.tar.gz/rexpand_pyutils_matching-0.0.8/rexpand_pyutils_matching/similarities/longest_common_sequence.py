"""
Sequence-based similarity scoring using longest common subsequence.
"""

from rexpand_pyutils_matching.utils.string import IGNORED_CHARS, normalize_string


def get_longest_common_sequence_similarity(
    s1: str,
    s2: str,
    normalize: bool = True,
    ignored_chars: list[str] | None = IGNORED_CHARS,
) -> float:
    """
    Calculate similarity score based on longest common subsequence.
    Returns both the similarity score and the longest common subsequence.
    Score is normalized between 0 (no common subsequence) and 1 (identical sequence).

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

    lcs_str = get_longest_common_sequence(s1, s2)
    max_length = max(len(s1), len(s2))
    similarity = len(lcs_str) / max_length if max_length > 0 else 1.0

    return similarity


def get_longest_common_sequence(s1: str, s2: str) -> str:
    """
    Calculate the longest common subsequence between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        str: The longest common subsequence
    """
    # Handle empty strings
    if not s1 and not s2:
        return ""
    if not s1 or not s2:
        return ""

    # Get string lengths
    m, n = len(s1), len(s2)

    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill the dp table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Reconstruct the LCS
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            lcs.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return "".join(reversed(lcs))
