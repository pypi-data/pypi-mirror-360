# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

textgrid-convert is a Python tool that converts audio transcripts (sbv, srt, json/rev formats) to Praat and DARLA compatible TextGrids. It supports both command-line usage and Python library usage.

## Commands

### Development Setup
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev

# Activate virtual environment
source .venv/bin/activate
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_main.py

# Run with coverage
uv run pytest --cov=textgrid_convert
```

### Building and Publishing
```bash
# Build package
uv build -o ./dist

# Upload to PyPI
uv run twine upload dist/* --verbose
```

### Running the Tool
```bash
# As module
python -m textgrid_convert -i input.srt -o output.TextGrid

# Using installed script
textgrid-convert -i input.srt -o output.TextGrid
```

## Architecture

### Core Components

1. **Parser System**: Abstract base class `ParserABC` with format-specific implementations:
   - `sbvParser`: Handles Google SBV files
   - `srtParser`: Handles SRT subtitle files  
   - `revParser`: Handles Rev.com JSON transcripts

2. **Main Processing**: `ttextgrid_convert.py` contains the main conversion logic:
   - `convert_to_txtgrid()`: Standard Praat TextGrid output
   - `convert_to_darla()`: DARLA-compatible TextGrid output
   - `main()`: CLI entry point with file/folder processing

3. **TextGrid Tools**: `textgridtools.py` handles TextGrid format generation:
   - `to_long_textgrid()`: Creates long-form TextGrid format
   - `ms_to_textgrid()`: Converts milliseconds to TextGrid time format

4. **Support Modules**:
   - `ArgParser.py`: Command-line argument parsing
   - `iotools.py`: File I/O operations
   - `preproctools.py`: Preprocessing utilities

### Data Flow

1. Input files are parsed by format-specific parsers into a standardized dictionary format:
   ```python
   {chunk_id: {"start": int, "end": int, "text": str, "speaker": str}}
   ```

2. The dictionary is processed through `textgridtools` to generate TextGrid format

3. Output is written to file via `iotools.filewriter()`

### Key Design Patterns

- **Abstract Base Class**: All parsers inherit from `ParserABC` ensuring consistent interface
- **Factory Pattern**: Format detection and parser selection in `main()`
- **Timestamp Handling**: Consistent millisecond-based internal representation

## File Structure

- `src/textgrid_convert/`: New package structure (modern Python packaging)
- `textgrid_convert/`: Legacy package structure (being phased out)
- `tests/`: Comprehensive test suite with sample files in `tests/resources/`

## Testing

The test suite includes:
- Unit tests for each parser (`test_*parser.py`)
- Integration tests (`test_main.py`, `test_cli.py`)
- Sample files in `tests/resources/` for validation

## Dependencies

- **Runtime**: numpy, pandas
- **Development**: pytest, pytest-cov, twine, build
- **Build system**: hatchling (via pyproject.toml)