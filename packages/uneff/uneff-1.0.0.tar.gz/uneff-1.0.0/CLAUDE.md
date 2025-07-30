# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Uneff is a text cleaning utility that removes BOM (Byte Order Mark) and problematic Unicode characters from files and streams. It's designed for data processing pipelines where invisible or control characters cause parsing failures or data corruption.

The project implements the same core functionality in both Python (`uneff.py`) and JavaScript (`uneff.js`) versions, providing flexibility for different environments.

## Architecture

### Core Components

- **Character Mapping System**: Uses `uneff_mappings.csv` to define which Unicode characters to process and how to handle them (remove or replace)
- **Content Processing Engine**: Handles both file-based and in-memory content cleaning
- **Analysis Engine**: Provides detailed reports on problematic characters with line/column locations
- **BOM Detection**: Automatically detects and handles UTF-8, UTF-16, and UTF-32 BOMs

### Key Design Patterns

- **Storage Agnostic**: Core functions (`clean_content`, `analyze_content`) work with in-memory content, allowing integration with custom storage systems
- **Configuration-Driven**: Character processing rules are externalized to CSV configuration file
- **Dual Implementation**: Python and JavaScript versions share the same API design and behavior

## Common Commands

### Python Version

```bash
# Basic cleaning
python uneff.py input.csv

# Custom output path
python uneff.py input.csv --output cleaned.csv

# Custom mappings
python uneff.py input.csv --mapping custom_mappings.csv

# Analyze without modifying
python uneff.py input.csv --analyze

# Quiet mode
python uneff.py input.csv --quiet
```

### JavaScript Version

```bash
# Basic cleaning
node uneff.js input.csv

# Custom output path
node uneff.js input.csv -o cleaned.csv

# Custom mappings
node uneff.js input.csv -m custom_mappings.csv

# Analyze without modifying
node uneff.js input.csv -a

# Quiet mode
node uneff.js input.csv -q
```

### Testing

No formal test framework is configured. Testing should be done by:
1. Running analysis mode first: `python uneff.py --analyze sample.csv`
2. Processing test files and validating output manually
3. Comparing before/after file sizes and content samples

## Character Mappings Configuration

The `uneff_mappings.csv` file controls character processing behavior:

- **Character**: The actual Unicode character (may be invisible)
- **Unicode**: Unicode escape sequence (e.g., `\u200b`)
- **Name**: Human-readable description
- **Remove**: `True` to process this character, `False` to skip
- **Replacement**: What to replace the character with (empty = remove entirely)

When first run, the tool automatically creates a default mappings file with common problematic characters.

## Integration Patterns

### File-Based Usage
```python
# Direct file processing
uneff.clean_file('input.csv', output_path='output.csv')
```

### Storage-Agnostic Usage
```python
# For custom storage systems
content = your_storage.read_file(file_id)
cleaned_content, char_counts = uneff.clean_content(content)
your_storage.write_file(file_id, cleaned_content)
```

## Important Behaviors

- **First Run**: Automatically creates `uneff_mappings.csv` with defaults if it doesn't exist
- **BOM Handling**: Automatically detects and removes BOMs from file start
- **Encoding**: Handles UTF-8 with fallback to latin-1 for problem files
- **Output Naming**: Default output adds `uneffd_` prefix to original filename
- **Non-Destructive**: Always preserves original files