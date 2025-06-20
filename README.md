# Project Resonant Rabbit - Unidiff Example

This project demonstrates parsing git patches using the Python unidiff library, with special attention to handling empty line additions and deletions.

## Features

- Parse git patch/diff files using unidiff
- Analyze patch statistics (added/removed lines, files, hunks)
- Detect empty line changes (additions and removals)
- Comprehensive patch analysis with detailed output
- Integration tests with git apply to validate parsed patches

## Structure

```
.
├── main.py                    # Main demonstration script
├── test_unidiff_parsing.py    # Pytest test suite
├── testdata/                  # Test patch files
│   ├── empty_lines.patch      # Patch with empty line changes
│   └── simple.patch           # Simple patch for basic tests
├── pyproject.toml             # Project configuration and dependencies
└── README.md                  # This file
```

## Usage

### Install dependencies
```bash
uv sync
```

### Run the main demonstration
```bash
uv run python main.py
```

### Run tests
```bash
uv run pytest test_unidiff_parsing.py -v
```

## Test Features

The test suite includes:
- **Basic patch parsing**: Verifies unidiff can parse patch files
- **Empty line detection**: Specifically tests detection of empty line additions/removals
- **Git apply integration**: Creates real git repos, applies patches, and verifies results
- **Patch reconstruction**: Tests that parsed patches can be reconstructed to original format

## Sample Output

The example processes patches that include:
- Adding empty lines to files
- Removing empty lines from files
- Regular code changes
- New file creation

The parser identifies and reports on these different types of changes, with special focus on empty line modifications.
```
