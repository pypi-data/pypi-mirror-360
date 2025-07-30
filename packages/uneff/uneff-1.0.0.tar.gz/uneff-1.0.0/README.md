# Uneff

A versatile tool to remove BOM (Byte Order Mark) and problematic Unicode characters from text files and streams.

## Overview

Uneff is designed to clean text files by removing BOM markers and other invisible Unicode characters that can cause issues when processing data files. It's especially useful for:

- Cleaning CSV files before data processing
- Fixing encoding issues in text files
- Removing invisible control characters that break parsers
- Normalizing text data from various sources

I created this for use in my own personal project(s) and am including it here in case someone may find it useful as a starting point for their own data processing pipeline issues and challenges.

## ⚠️ Warning and Disclaimer

### Risk of Unintended Consequences

**IMPORTANT**: Modifying text data by removing or replacing characters can have unintended consequences. While Uneff is designed to help with common data cleaning challenges, improper use may introduce new issues into your data.

- **Always create backups** of your original files before processing
- **Always validate** the results after processing to ensure data integrity
- **Never use** on production data without thorough testing
- **Be especially cautious** when working with:
  - Internationalized text
  - Complex data formats (like JSON, XML)
  - Files with custom encoding
  - Critical data where character precision matters

### No Warranty

This tool is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

### Recommended Workflow

1. **Analyze first**: Use the `--analyze` flag to identify issues without modifying files
2. **Test on samples**: Process a small sample before running on large datasets
3. **Verify results**: Implement verification checks after processing
4. **Document changes**: Keep records of what was processed and why
5. **Limit scope**: Only process the specific characters you know are problematic

## Features

- Removes UTF-8, UTF-16, and UTF-32 BOM markers
- Handles invisible and problematic Unicode characters
- Supports replacing characters instead of just removing them
- Works with in-memory content (no direct file I/O required)
- Configurable via a simple CSV file - no code changes needed
- Can be used as a command-line tool or as a library in your projects
- Available in both Python and JavaScript versions
- Preserves original files by creating clean copies
- Detailed reporting of changes made
- Precise location reporting of problematic characters (line, column, and absolute position)

## Installation

### Python Version

1. Download `uneff.py` to your project directory
2. Make it executable (optional, for Unix-like systems):
   ```
   chmod +x uneff.py
   ```

### JavaScript Version

1. Download `uneff.js` to your project directory
2. Ensure you have Node.js installed

## Usage

### Command Line

#### Python Version

```bash
python uneff.py myfile.csv
```

Options:
```
python uneff.py myfile.csv [--mapping mappings.csv] [--output output.csv] [--quiet] [--analyze]
```

#### JavaScript Version

```bash
node uneff.js myfile.csv
```

Options:
```
node uneff.js myfile.csv [-m|--mapping mappings.csv] [-o|--output output.csv] [-q|--quiet] [-a|--analyze]
```

### In Your Code

#### Python Version

```python
import uneff

# Clean a file
uneff.clean_file('myfile.csv')

# Clean text directly without file I/O
dirty_text = '﻿Hello�World with invisible\u200bspaces'
clean_text = uneff.clean_text(dirty_text)

# Use with custom options
uneff.clean_file(
    file_path='myfile.csv',
    mapping_file='custom_mappings.csv',
    output_path='cleaned.csv',
    verbose=False
)

# Working with in-memory content (storage-agnostic)
content_bytes = get_content_from_your_system()  # Your custom storage API
cleaned_content, char_counts = uneff.clean_content(content_bytes)
save_content_to_your_system(cleaned_content)  # Your custom storage API

# Analyze file without modifying it
analysis = uneff.analyze_file('myfile.csv')
print(f"Found {analysis['problematic_char_count']} problematic characters")
```

#### JavaScript Version

```javascript
const uneff = require('./uneff');

// Clean a file
uneff.cleanFile('myfile.csv');

// Clean text directly without file I/O
const dirtyText = '﻿Hello�World with invisible\u200bspaces';
const cleanText = uneff.cleanText(dirtyText);

// Use with custom options
uneff.cleanFile(
    'myfile.csv',
    'custom_mappings.csv',
    'cleaned.csv',
    false  // verbose mode off
);

// Working with in-memory content (storage-agnostic)
const contentBytes = getContentFromYourSystem();  // Your custom storage API
const [cleanedContent, charCounts] = uneff.cleanContent(contentBytes);
saveContentToYourSystem(cleanedContent);  // Your custom storage API

// Analyze file without modifying it
const analysis = uneff.analyzeFile('myfile.csv');
console.log(`Found ${analysis.problematic_char_count} problematic characters`);
```

## Configuring Problematic Characters

On first run, Uneff creates a default `uneff_mappings.csv` file with common problematic characters. You can edit this file to customize how characters are handled:

| Character | Unicode  | Name                     | Remove | Replacement |
|-----------|----------|--------------------------|--------|-------------|
| �         | \ufffd   | Replacement Character    | True   |             |
| [empty]   | \u0000   | NULL                     | True   |             |
| [empty]   | \u2028   | Line Separator           | True   | " "         |
| [empty]   | \u2029   | Paragraph Separator      | True   | "\n"        |
| [empty]   | \u200b   | Zero Width Space         | True   |             |
| ﻿          | \ufeff    | BOM (in middle of file)   | True   |             |
| ...       | ...      | ...                      | ...    | ...         |

- To stop processing a specific character, change `True` to `False`
- To add new characters, add a new row with the appropriate Unicode escape sequence
- Add a replacement character in the "Replacement" column to replace instead of remove
- If "Remove" is True and "Replacement" is empty, the character is removed completely

### Notes on the Replacement Field

- **Do not add quotes** around replacement values in the CSV file unless they contain special characters
- Leave empty to remove the character completely
- For whitespace characters:
  - Use `\n` for newline
  - Use `\t` for tab
  - Use a space character for space
- For multiple characters, simply type them as-is (e.g., `-->`)

#### Special Characters in Replacements

When your replacement contains special characters like commas, you must use quotes in the CSV:

| Character | Unicode  | Name              | Remove | Replacement |
|-----------|----------|-------------------|--------|-------------|
| [empty]   | \u2063   | Invisible Separator | True  | ","         |

The CSV should look like this in a text editor:
```
Character,Unicode,Name,Remove,Replacement
,\u2063,Invisible Separator,True,","
```

Without the quotes, the comma would be interpreted as a new field separator.

#### Additional Examples

| Replacement For | Raw Text in CSV | Notes |
|-----------------|-----------------|-------|
| Comma | "," | Must be quoted |
| Quote | """" | Double quotes to escape |
| Tab character | \t | Escape sequence |
| Newline | \n | Escape sequence |
| Comma + text | ",.txt" | Must be quoted |

## What Characters are Processed?

By default, Uneff handles these types of characters:

- BOM (Byte Order Mark) characters
- Replacement Character (�)
- Control characters (NULL, SUB, FS, GS, RS, US)
- Zero-width spaces and joiners
- Bidirectional text control characters
- Line and paragraph separators (now replaced with spaces and newlines by default)
- Other invisible formatting characters

## Advanced Analysis Features

The analysis functions provide detailed information about problematic characters in your text:

```python
# Analyze a file and get detailed report
analysis = uneff.analyze_file('myfile.csv')

# Get total count of problematic characters
print(f"Found {analysis['problematic_char_count']} problematic characters")

# Get information about each type of problematic character
for detail in analysis['character_details']:
    print(f"Character: {detail['name']} [Unicode: {detail['unicode']}]")
    print(f"Count: {detail['count']} instances")
    
    # Print locations of up to 10 instances
    for location in detail['sample_locations']:
        print(f"  Found at Line {location['line']}, Column {location['column']}")
        print(f"  Context: ...{location['context']}...")
```

In JavaScript:

```javascript
// Analyze a file and get detailed report
const analysis = uneff.analyzeFile('myfile.csv');

// Get total count of problematic characters
console.log(`Found ${analysis.problematic_char_count} problematic characters`);

// Get information about each type of problematic character
for (const detail of analysis.character_details) {
    console.log(`Character: ${detail.name} [Unicode: ${detail.unicode}]`);
    console.log(`Count: ${detail.count} instances`);
    
    // Print locations of up to 10 instances
    for (const location of detail.sample_locations) {
        console.log(`  Found at Line ${location.line}, Column ${location.column}`);
        console.log(`  Context: ...${location.context}...`);
    }
}
```

The analysis results include:
- Exact line and column positions of each problematic character
- Absolute position in the file
- Surrounding context to help identify issues
- BOM detection and encoding information
- Character counts and statistics

## First-Run Behavior

When running Uneff for the first time:

1. If a mapping file doesn't exist, Uneff automatically creates one with default settings.
2. This happens seamlessly, allowing you to immediately process files without errors.
3. The default mapping file (`uneff_mappings.csv`) is created in the same directory as the script.

## Why Process These Characters?

### Common Problems Caused by Invisible Characters

1. **Parser Failures**: Many data processing systems and parsers fail when encountering unexpected Unicode characters
2. **Data Processing Errors**: Characters like zero-width spaces break tokenization, field detection, and data extraction
3. **Database Import Issues**: ETL processes often reject data with control characters
4. **Inconsistent Behavior**: The same file might work in one system but fail in another
5. **Hard-to-Debug Problems**: Since these characters are invisible, problems they cause can be extremely difficult to diagnose

### Specific Use Cases

- **CSV Processing**: BOM markers can cause the first column name to be misread
- **Data Analysis**: Invisible characters can cause misalignment in data processing
- **API Integrations**: Data passed between systems can accumulate problematic characters
- **Text Mining**: Control characters can corrupt text analysis
- **Custom Storage Systems**: Applications with their own storage systems can now leverage Uneff's capabilities

## Integration Options

### For Standard File Processing

Use the traditional methods with direct file I/O:

```python
uneff.clean_file('myfile.csv')
```

```javascript
uneff.cleanFile('myfile.csv');
```

### For Custom Storage Systems

Use the storage-agnostic core functions:

```python
# 1. Get content using your storage API
content = your_app.get_file_content(file_id)

# 2. Use Uneff to clean it in memory
cleaned_content, char_counts = uneff.clean_content(content)

# 3. Save using your storage API
your_app.save_file_content(file_id, cleaned_content)
```

```javascript
// 1. Get content using your storage API
const content = your_app.get_file_content(file_id);

// 2. Use Uneff to clean it in memory
const [cleaned_content, char_counts] = uneff.cleanContent(content);

// 3. Save using your storage API
your_app.save_file_content(file_id, cleaned_content);
```

## Safe vs. Unsafe: When to Use Uneff

### When It's Safe to Process These Characters

- **Data Processing Pipelines**: Before feeding data into analysis tools or databases
- **Plain Text Content**: Regular text documents, logs, configuration files
- **Data Exchange**: Files being transferred between different systems
- **CSV Files**: Almost always safe to remove BOM and control characters
- **Legacy Data Cleanup**: Fixing old files with encoding issues

### When to Be Cautious

- **Rich Text Documents**: Some zero-width characters have specific formatting purposes in RTF, HTML, or Word docs
- **Bidirectional Text**: Languages like Arabic or Hebrew sometimes use special Unicode control characters
- **Source Code**: Some IDEs and development tools might use BOM markers intentionally
- **XML/HTML**: These formats sometimes use control characters with specific meanings

### Potential Risks When Processing Characters

- **Text Layout Changes**: Modifying bidirectional controls might affect text rendering in some languages
- **Formatting Loss**: Some invisible characters serve legitimate formatting purposes
- **Semantic Change**: In rare cases, modifying zero-width joiners could change how text is displayed

## License

MIT