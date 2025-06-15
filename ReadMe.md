# JSONL to HTML Converter

A simple command-line tool to convert JSONL (JSON Lines) and JSON files into HTML format. This tool is designed to facilitate the visualization of structured data stored in JSONL or JSON format.

## Usage

### Command Line
```bash
# Convert JSONL file
jsonl2html some_file.jsonl

# Convert JSON file  
jsonl2html some_file.json

# Get help
jsonl2html --help

# Specify custom index column
jsonl2html some_file.jsonl --index_column=some_column

# Specify custom output file
jsonl2html some_file.jsonl --fn_output=custom_output.html
```

### Python API
```python
from jsonl2html import convert_jsonl_to_html

# Convert JSONL file
convert_jsonl_to_html(
    fn_input="examples/small.jsonl",
    index_column='auto', 
    fn_output="auto", 
    additional_table_content={"content": "value"}
)
```

```python3
# Convert JSON file
convert_jsonl_to_html(
    fn_input="examples/test.json",
    index_column='auto', 
    fn_output="auto"
)
```

## Features

- **Multiple Input Formats**: Convert JSONL and JSON files to HTML format
- **Automatic Index Detection**: Smart detection of index columns (question, prompt, title, etc.)
- **Configurable Settings**: Customize behavior via configuration file
- **File Size Warnings**: Automatic warnings for large files
- **Interactive HTML Output**: Generated HTML includes navigation, search, and expandable content
- **Unicode Statistics**: Optional unicode analysis and statistics (requires `unicode_stats` package)

## Configuration

The tool supports configuration via `jsonl2html/config.json`. Default settings:

```json
{
    "auto_index_columns": ["question", "questions", "prompt", "prompts", "title", "name"],
    "max_lines": 10000,
    "file_size_warning_mb": 50,
    "logging_level": "INFO"
}
```

### Configuration Options

- **auto_index_columns**: List of column names to automatically detect for indexing
- **max_lines**: Maximum number of lines to process from input files
- **file_size_warning_mb**: File size threshold (MB) for showing warnings
- **logging_level**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## Installation

### From Source
```bash
# Clone the repository
git clone <repository-url>
cd jsonl2html

# Install in development mode
pip install -e .
```

### Build from Sources
```bash
# Build distribution packages
python -m build

# Install the built package
pip install dist/jsonl2html-*.whl
```

## Examples

The `examples/` directory contains sample files:

- `examples/test.json`: Simple JSON array with questions and answers
- `examples/single_object.json`: Single JSON object example
- `examples/small.jsonl`: JSONL file with complex programming problems

Try them out:
```bash
jsonl2html examples/test.json
```

```bash
jsonl2html examples/small.jsonl
```

## Output

The tool generates an interactive HTML file with:

- **Navigation Panel**: Browse through all entries with search functionality
- **Content Area**: Display selected entries with expandable sections
- **Table of Contents**: Overview and statistics about the dataset
- **Responsive Design**: Works on desktop and mobile devices

## Error Handling

The tool provides helpful error messages for:
- Invalid file formats
- Missing files
- JSON parsing errors
- Configuration issues
- Large file warnings

## Requirements

- Python >= 3.6
- Dependencies: `fire`, `tabulate`
- Optional: `unicode_stats` (for unicode analysis)

## Version History

### v0.2.0
- ✅ Added JSON file support
- ✅ Added configuration file support
- ✅ Improved logging system
- ✅ Added file size warnings
- ✅ Better error handling

## Known Issues

- Double-click navigation issues in some browsers
- Limited search functionality
- Basic list visualization for arrays

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

MIT License - see LICENSE file for details.
