"""
Convert JSONL or JSON files to HTML with an optional index column.
"""
# noqa: E501
# pylint: disable=line-too-long
import json
import sys
import base64
from typing import Optional, List, Dict
from pathlib import Path
import logging
import fire
from .create_table_of_content import create_table_of_content_unicode_stats
from .config import load_config, Config

# Get logger instance
logger = logging.getLogger("jsonl2html")


class ExceptionFileInput(Exception):
    """Something wrong with input json file"""


class JSONLToHTMLConverter:
    """
    A class to convert JSONL or JSON files to HTML format with an optional index column.
    It reads the input file, processes the data,
    and generates an HTML file with a table of contents.
    The HTML file is generated using a predefined template
    and can include an index based on a specified column.
    """
    fn_template = Path(__file__).parent / "html_template.html"

    def __init__(self, fn_input: str, fn_output: str = "auto",
                 index_column: Optional[str] = 'auto',
                 additional_table_content: Optional[str] = None,
                 unicode_stats: bool = False
                 ) -> None:
        """
        Initialize the JsonlToHTML class,
        setting up input/output file names and optional index column.

        Parameters:
        fn_input (str): The input file path (must end with '.jsonl' or '.json').
        fn_output (str): The output HTML file path. Defaults to 'auto',
            which creates an HTML file with the same base name as the input.
            index_column (Optional[str]): Column name to use for indexing.
            If None, no index is added.
        additional_table_content (Optional[str]):
            Add additional table of content to the HTML file. None to disable
        unicode_stats (bool): Whether to include unicode statistics in the output.
        """
        # Load configuration
        self.config: Config = load_config()

        if not fn_input.endswith((".jsonl", ".json")):
            raise ExceptionFileInput("Input file must be a .jsonl or .json file")

        self.fn_input = fn_input
        self.index_column = index_column
        self.unicode_stats = unicode_stats

        # Check file size and warn if too large
        try:
            file_size_mb = Path(fn_input).stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.file_size_warning_mb:
                logger.warning(
                    "File size (%.1fMB) is larger than recommended (%dMB)",
                    file_size_mb,
                    self.config.file_size_warning_mb
                )
        except OSError:
            pass  # File doesn't exist yet, will be caught later

        # Auto-generate the output file name if not provided
        if fn_output == 'auto':
            if fn_input.endswith(".jsonl"):
                self.fn_output = Path(fn_input).name[:-len(".jsonl")] + '.html'
            elif fn_input.endswith(".json"):
                self.fn_output = Path(fn_input).name[:-len(".json")] + '.html'
            else:
                # Fallback - this shouldn't happen due to earlier assertion
                self.fn_output = Path(fn_input).stem + '.html'
        else:
            self.fn_output = fn_output
        self.title = Path(fn_input).name  # Extract the file name for title
        self.additional_table_content = additional_table_content

    def run(self) -> None:
        """
        The main method that reads the JSONL or JSON file, processes the data
        (adds an index if needed), and renders the HTML output file.
        """
        # Auto-detect file type and read accordingly
        if self.fn_input.endswith(".jsonl"):
            data = self.read_jsonl(self.fn_input)
        elif self.fn_input.endswith(".json"):
            data = self.read_json(self.fn_input)
        else:
            message = f"Unsupported file format. Input file must be .jsonl or .json, got: {self.fn_input}"
            logger.error(message)
            raise ExceptionFileInput(message)

        if self.index_column == 'auto':
            self.index_column = self.get_auto_index_column(data[0])
            logger.info("change index column to %s", self.index_column)

        # If an index column is specified, add an index to each entry in the data
        if self.index_column:
            self.add_index(data, self.index_column)

        table_of_content = {"__index__": f"**Table of content** <br> ({len(data)} documents )"}

        if self.additional_table_content:
            for key, value in self.additional_table_content.items():
                table_of_content[key] = value
            logger.info("Added additional table content %s",
                        list(self.additional_table_content.keys())
                        )

        if self.unicode_stats:
            try:
                unicode_statistics_markdown = create_table_of_content_unicode_stats(self.fn_input)
                table_of_content['unicode'] = unicode_statistics_markdown
                logger.info("Added table of content")
            except ModuleNotFoundError:
                logger.warning("Please install unicode_stats lib to get unicode table of content")
            except Exception as e:
                logger.error(e, exc_info=True)
                raise e

        data = [table_of_content] + data
        # Convert the data to a JSON string and then encode it in base64
        json_data = json.dumps(data)
        base64_encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')

        # Read the HTML template from a file
        with open(self.fn_template, "r", encoding='utf-8') as file:
            txt = file.read()

        # Ensure the placeholder 'BASE64STRING' is present exactly once in the template
        assert txt.count('BASE64STRING') == 1, "'BASE64STRING' placeholder not found exactly once."
        # Replace the placeholder with the base64 encoded data
        txt = txt.replace('BASE64STRING', base64_encoded_data)

        # Ensure the placeholder 'JSONL VISUALIZER' is present exactly once in the template
        assert txt.count("JSONL VISUALIZER") == 1, "'JSONL VISUALIZER' placeholder not found exactly once."
        # Replace the placeholder with the given title
        txt = txt.replace("JSONL VISUALIZER", self.title)

        # Write the modified HTML content to the output file
        with open(self.fn_output, "w", encoding='utf-8') as file:
            file.write(txt)

        logger.info("OK. Save results to %s", self.fn_output)

    def read_jsonl(self, fn: str) -> List[Dict]:
        """
        Reads a JSONL (JSON Lines) file and returns a list of dictionaries.
        Each line in the file is parsed as a separate JSON object.

        Parameters:
        fn (str): The filename of the JSONL file.

        Returns:
        List[Dict]: A list of dictionaries representing the parsed JSON data.
        """
        try:
            data = []
            max_lines = self.config.max_lines
            with open(fn, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        data.append(json.loads(line))
                    if len(data) >= max_lines:
                        logger.warning("Reached max_lines limit (%d). Stopping read.", max_lines)
                        break
            return data
        except (FileNotFoundError, IOError) as e:
            message = f"Error reading file {fn}: {e}"
            logger.error(message)
            raise ExceptionFileInput(message) from e
        except json.JSONDecodeError as e:
            message = f"Error parsing JSON in file {fn}: {e}"
            logger.error(message)
            raise ExceptionFileInput(message) from e

    def read_json(self, fn: str) -> List[Dict]:
        """
        Reads a JSON file and returns a list of dictionaries.
        If the JSON contains a single object, wraps it in a list with a warning.
        If the JSON contains an array, returns it directly.

        Parameters:
        fn (str): The filename of the JSON file.

        Returns:
        List[Dict]: A list of dictionaries representing the parsed JSON data.
        """
        try:
            with open(fn, 'r', encoding='utf-8') as file:
                data = json.load(file)

            max_lines = self.config.max_lines

            if isinstance(data, dict):
                logger.warning("JSON file contains a single object, converting to list with one element")
                return [data]
            elif isinstance(data, list):
                if len(data) > max_lines:
                    logger.warning("JSON file has %s items. Limiting to %s",
                                   len(data),
                                   max_lines
                                   )
                return data[:max_lines]  # Respect max_lines limit like read_jsonl
            else:
                message = f"JSON file must contain an object or array, got {type(data)}"
                logger.error(message)
                raise ExceptionFileInput(message)

        except (FileNotFoundError, IOError) as e:
            message = f"Error reading file {fn}: {e}"
            logger.error(message)
            raise ExceptionFileInput(message) from e
        except json.JSONDecodeError as e:
            message = f"Error parsing JSON in file {fn}: {e}"
            logger.error(message)
            raise ExceptionFileInput(message) from e

    def get_auto_index_column(self, first_row: Dict) -> Optional[str]:
        """Get auto index column from configuration"""
        auto_index_columns = self.config.auto_index_columns
        for column in auto_index_columns:
            if column in first_row:
                return column
        return None

    @staticmethod
    def add_index(data: List[Dict], index_column: str = "question") -> None:
        """
        Adds an index field '__index__' to each entry in the data based on a specified column.

        Parameters:
        data (List[Dict]): A list of dictionaries containing the data.
        index_column (str): The key to use as the base for the '__index__' field (default is 'question').
        """
        error_count = 0
        # Iterate through each item in the data
        for row_number, entry in enumerate(data):
            entry['__index__'] = ""
            # Check if the index_column exists in the entry, else leave the index blank
            if index_column not in entry:
                error_count += 1
            else:
                if isinstance(entry[index_column], str):
                    # Extract the first line of the specified column
                    # after stripping leading newlines
                    entry['__index__'] = entry[index_column].lstrip('\n').split('\n')[0]
                else:
                    logger.error("at row=%d column=%s is not string, disable/change index_colum",
                                 row_number,
                                 index_column
                                 )

        if error_count > 0:
            logger.error("There are missing %s fields in %s entries\n",
                         index_column,
                         error_count
                         )


def convert_jsonl_to_html(fn_input: str,
                          index_column: Optional[str] = 'auto',
                          fn_output: str = "auto",
                          additional_table_content: Optional[str] = None,
                          unicode_stats: bool = True
                          ) -> None:
    """
    Convert jsonl or json to html

    Parameters:
    fn_input (str): The input JSONL or JSON file.
    index_column (Optional[str]): The column to use for indexing (default is 'auto' look at first row for ['qustion', 'prompts], None to disable).
    fn_output (str): The output HTML file (default is 'auto', creates HTML file with same base name as input)
    unicode_stats (bool): Whether to include unicode statistics in the output (default is True)
    """
    if fn_input is None:
        logger.error("Error: 'fn_input' argument is required.")
        logger.error("Usage: jsonl2html <input_file.jsonl|input_file.json> [--index_column=<column>] [--fn_output=<output.html>]")
        sys.exit(1)

    converter = JSONLToHTMLConverter(fn_input,
                                     fn_output,
                                     index_column,
                                     additional_table_content=additional_table_content,
                                     unicode_stats=unicode_stats
                                     )
    converter.run()


def main_bash_entry_point():
    """
    Main entry point for the command line interface.
    !There are a bug inside fire NAME COULD'T BE main
    if you are build package with setuptools
    """
    fire.Fire(convert_jsonl_to_html)


if __name__ == "__main__":
    main_bash_entry_point()
