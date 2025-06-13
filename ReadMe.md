
# JSONL to HTML Converter

A simple command-line tool to convert JSONL (JSON Lines) and JSON files into HTML format. This tool is designed to facilitate the visualization of structured data stored in JSONL or JSON format.

# Usage
### Bash
`jsonl2html some_file.jsonl`
Will create `some_file.html` visualization

`jsonl2html some_file.json`
Will create `some_file.html` visualization from JSON file

`jsonl2html --help`
Read the documentation

`jsonl2html some_file.jsonl --index_column=some_column`
Will create visualization indexed by `some_column`

### Python
```python
from jsonl2html import convert_jsonl_to_html

# Convert JSONL file
convert_jsonl_to_html(fn_input = "examples/small.jsonl",
index_column = 'auto', 
fn_output = "auto", 
additional_table_content = {"content": "value"}
)

# Convert JSON file
convert_jsonl_to_html(fn_input = "examples/test.json",
index_column = 'auto', 
fn_output = "auto"
)
```

## Features

- Convert JSONL and JSON files to HTML format using a customizable template.
- Supports JSON arrays and single JSON objects (with automatic conversion to array format).
- Optionally add an index based on a specified column in the data.
- Easy to use with a command-line interface.

## Installation

You can install the package locally using pip. Clone this repository and run:

```bash
pip install -e .
```

## Build from sources

```bash
python setup.py sdist bdist_wheel
pip install {path_to_package}
```

## Issues
 - add list normal vizualization
 - fix problem with double click at some line
 - add UnicodeParser invert index and aggregated statistic
 - add search


## ToDo
- fix logger redirect to stdout other's logs
- ✅ add .json as input format
- load to pip registry
- add normal examples
- add enable/disable markdown hint for some field
