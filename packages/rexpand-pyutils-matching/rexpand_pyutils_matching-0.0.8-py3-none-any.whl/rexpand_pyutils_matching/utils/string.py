import re


def normalize_spaces(text: str) -> str:
    """
    Removes extra spaces between words and trims the string.

    Args:
        text (str): The input string to normalize

    Returns:
        str: The string with normalized spacing
    """
    return re.sub(r"\s+", " ", text.strip())


# Define common special_s to be replaced with spaces
IGNORED_CHARS = [
    "/",
    ",",
    ";",
    "-",
    "_",
    "|",
    "\\",
    "+",
    "&",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    "?",
    "!",
    ".",
    " ",
]


# Normalize both strings by replacing special_s with spaces and converting to lowercase
def normalize_string(text: str, ignored_chars=IGNORED_CHARS) -> str:
    text = text.lower()
    for special_char in ignored_chars:
        text = text.replace(special_char, " ")
    return normalize_spaces(text)
