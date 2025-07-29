# splitpo

A Python utility for splitting gettext .po files into smaller chunks by entry count and later merging them back together.

## Features

- Split large .po files into manageable chunks of a specified number of entries
- Merge previously split .po files back into the original format
- Maintain .po file structure and metadata during split/merge operations
- Preserve comments, flags, references, and other po file attributes
- Support for both command-line interface and module execution

## Installation

```bash
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Split a .po file into chunks
python main.py split-po input.po --output-dir=./splitted --entries 100

# Join split .po files back together
python main.py join-po splitted/input_part_*.po --output=input.po
```

### Module Execution

```bash
# Run split command directly
splitpo input.po --output-dir=./splitted --entries 100

# Run join command directly
joinpo splitted/input_part_*.po --output=input.po
```

### Options

#### split-po command

- `input_file`: Input .po file to split (required)
- `--output-dir`: Output directory for split files (default: ./splitted)
- `--entries`: Number of entries per split file (default: 100)

#### join-po command

- `input_files`: Input .po files to join, supports wildcards (required)
- `--output`: Output .po file (required)

## Requirements

- Python 3.13+
- No external dependencies

## File Structure

Split files are named with the pattern `{original_name}_part_{number}.po`:
- `input.po` → `input_part_000.po`, `input_part_001.po`, etc.
- Number of digits adjusts to file count (minimum 3 digits)
- Numbering starts from 0

## License

MIT License - see LICENSE file for details.