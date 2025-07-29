# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python utility for splitting gettext .po files into smaller chunks by entry count and later merging them back together. The project uses modern Python packaging with pyproject.toml.

### Purpose
- Split large .po files into manageable chunks of a specified number of entries
- Merge previously split .po files back into the original format
- Maintain .po file structure and metadata during split/merge operations

## Development Commands

### Running the application
```bash
# Split a .po file into chunks
python main.py split-po input.po --output-dir=./splitted --entries 100

# Join split .po files back together
python main.py join-po splitted/input_part_*.po --output=input.po

# Or run modules directly
python -m splitpo.split input.po --output-dir=./splitted --entries 100
python -m splitpo.join splitted/input_part_*.po --output=input.po
```

### Installing dependencies
Since this uses modern Python packaging, use:
```bash
pip install -e .
```

### Running tests
```bash
# Run all tests
uv run pytest

# Run specific test files
uv run pytest tests/test_cli.py
uv run pytest tests/test_roundtrip.py

# Run with verbose output
uv run pytest -v
```

### GitHub Actions
The project includes automated testing via GitHub Actions:
- Runs on pull requests and pushes to main
- Tests on Python 3.10, 3.11, 3.12, and 3.13
- Uses uv for dependency management
- Runs pytest and CLI command tests

## Code Architecture

- **main.py**: Entry point with CLI argument parsing for both commands
- **splitpo/**: Main package directory
  - **common.py**: Shared utilities for po file parsing and writing
  - **split.py**: Split command implementation (splitpo.split module)
  - **join.py**: Join command implementation (splitpo.join module)
- **pyproject.toml**: Project configuration using modern Python packaging standards
- Requires Python 3.13+
- No external dependencies

## Project Structure

- Modular architecture with separate modules for split and join operations
- Each command can be run independently as a Python module
- Common po file processing utilities shared between commands
- Modern Python packaging setup