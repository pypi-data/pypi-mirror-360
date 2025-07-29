# rexpand-pyutils-matching

A Python library providing various string matching utilities including exact matching, fuzzy matching, and LLM-powered search capabilities.

## Installation

```bash
pip install rexpand-pyutils-matching
```

## Features

- Exact string matching
- Fuzzy string matching with customizable threshold
- Levenshtein distance calculation
- Longest common subsequence finding
- LLM-powered search with exact matching and value suggestion
- Multiple similarity measures for string comparison

## Usage

```python
from rexpand_pyutils_matching import (
    exact_match,
    fuzzy_match,
    fuzzy_search,
    search,  # Main search function with LLM capabilities
    SimilarityMeasure,  # Enum for different similarity measures
    SIMILARITY_FUNCTIONS,  # Dictionary of available similarity functions
)

# Basic string matching
exact_match("hello", "hello")  # True
exact_match("hello", "world")  # False

# Fuzzy matching
fuzzy_match("hello", "helo", threshold=0.6)  # True
fuzzy_match("hello", "world", threshold=0.6)  # False

# Fuzzy search with multiple candidates
fuzzy_search(
    search_key="Stanford",
    standard_values=["Stanford University", "Stanford", "Harvard University"],
    threshold=None,
    candidate_count=3,
    similarity_measure=SimilarityMeasure.COMMON_PREFIX
) # [('Stanford', 1), ('Stanford University', 0.6481481481481481), ('Harvard University', 0.0)]

# Advanced search with LLM capabilities
search(
    search_key="Stanford University",
    standard_values=["Stanford University", "Stanford", "Harvard University"],
    threshold=0.8,
    candidate_count=3,
    use_llm_for_exact_match=True,  # Enable LLM for exact matching
    use_llm_for_suggestion=True,   # Enable LLM for suggesting new values
    chatgpt_api_key="your-api-key" # Required for LLM features
) # {"candidate": "Stanford University", "is_suggested": False}
```

## Requirements

- Python >= 3.11
- OpenAI API key (for LLM features)

## Development

The project includes a Makefile with common development commands. First, set up your development environment:

```bash
# Create virtual environment
make venv

# Activate virtual environment (you need to do this every time you start a new shell)
source .venv/bin/activate

# Install development dependencies (this will also create venv if it doesn't exist)
make install
```

Other available commands:

```bash
# Run tests
make test

# Run linting checks
make lint

# Format code
make format

# Clean build artifacts
make clean

# Clean everything including virtual environment
make clean-all

# Build package
make build

# Upload to PyPI
make publish

# Run all checks before commit
make pre-commit
```

To deactivate the virtual environment when you're done:

```bash
deactivate
```

## Publishing to PyPI

To publish to PyPI while excluding local test files, create or update your `.gitignore` file to include:

```
# Local test files
some_file.txt
```

Then follow these steps:

1. Update your `setup.py` or `pyproject.toml` to exclude these files from the package distribution
2. Build the package: `make build`
3. Upload to PyPI: `make publish`

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
