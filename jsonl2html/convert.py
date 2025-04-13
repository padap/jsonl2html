import json
import sys
import base64
from typing import Union, Optional, List, Dict
import fire
from pathlib import Path
import logging
from .create_table_of_content import create_table_of_content_unicode_stats

logging.basicConfig(level=logging.DEBUG)

class ExceptionFileInput(Exception):
    """Something wrong with input json file"""
    pass

class JSONLToHTMLConverter:
    fn_template = Path(__file__).parent / "html_template.html"
    list_auto_columns = ['question', 'quesitions', 'prompt', 'prompts']
    max_lines = 10000
    
    def __init__(self, fn_input: str, fn_output: str = "auto", index_column: Optional[str] = 'auto', 
                 additional_table_content: Optional[str] = None) -> None:
        """
        Initialize the JsonlToHTML class, setting up input/output file names and optional index column.

        Parameters:
        fn_input (str): The input JSONL file path (must end with '.jsonl').
        fn_output (str): The output HTML file path. Defaults to 'auto', which creates an HTML file with the same base name as the input.
        index_column (Optional[str]): Column name to use for indexing. If None, no index is added.
        additional_table_content (Optional[str]): Add adtitional table of content to the HTML file. None to disable
        """
        assert fn_input.endswith(".jsonl"), "Input file must be a .jsonl file"
        
        self.fn_input = fn_input
        self.index_column = index_column
        
        # Auto-generate the output file name if not provided
        if fn_output == 'auto':
            self.fn_output = Path(fn_input).name[:-len(".jsonl")] + '.html'
        else:
            self.fn_output = fn_output
        self.title = Path(fn_input).name # Extract the file name for title
        self.additional_table_content = additional_table_content
    
    def run(self) -> None:
        """
        The main method that reads the JSONL file, processes the data (adds an index if needed), 
        and renders the HTML output file.
        """
        # Read the JSONL data from the input file
        data = self.read_jsonl(self.fn_input)
        
        if self.index_column == 'auto':
            self.index_column = self.get_auto_index_column(data[0])
            logging.info(f"change index column to {self.index_column}")
        
        # If an index column is specified, add an index to each entry in the data
        if self.index_column:
            self.add_index(data, self.index_column)
        
        table_of_content = {"__index__": f"**Table of content** <br> ({len(data)} documents )"
                           }

        if self.additional_table_content:
            for key, value in self.additional_table_content.items():
                table_of_content[key] = value
            logging.info(f"Added additional table content {list(self.additional_table_content.keys())}")

        try:
            unicode_statistics_markdown = create_table_of_content_unicode_stats(self.fn_input)
            table_of_content['unicode'] = unicode_statistics_markdown
            logging.info("Added table of content")
        except ModuleNotFoundError:
            logging.warning("Please install unicode_stats lib to get unicode table of content")
        except Exception as e:
            logging.error(e, exc_info=True)
        
        data = [table_of_content] + data
        # Convert the data to a JSON string and then encode it in base64
        json_data = json.dumps(data)
        base64_encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')

        # Read the HTML template from a file
        with open(self.fn_template, "r") as file:
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
        with open(self.fn_output, "w") as file:
            file.write(txt)
        
        logging.info(f"OK. Save results to {self.fn_output}")
    
    @classmethod
    def read_jsonl(cls, fn: str) -> List[Dict]:
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
            with open(fn, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        data.append(json.loads(line))
                    if len(data) >= cls.max_lines:
                        break
            return data
        except (FileNotFoundError, IOError) as e:
            message = f"Error reading file {fn}: {e}"
            logging.error(message)
            raise ExceptionFileInput(message)
        except json.JSONDecodeError as e:
            message = f"Error parsing JSON in file {fn}: {e}"
            logging.error(message)
            raise ExceptionFileInput(message)
    
    @classmethod
    def get_auto_index_column(cls, first_row: Dict) -> Optional[str]:
        index_column = None
        for column in cls.list_auto_columns:
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
                    # Extract the first line of the specified column after stripping leading newlines            
                    entry['__index__'] = entry[index_column].lstrip('\n').split('\n')[0]
                else:
                    logging.error(f"at row={row_number} column={index_column} is not string, disable/change index_colum")

        if error_count > 0:
            logging.error(f"There are missing {index_column} fields in {error_count} entries\n")


def convert_jsonl_to_html(fn_input: str, index_column: Optional[str] = 'auto', fn_output: str = "auto", additional_table_content: Optional[str] = None) -> None:
    """
    Convert jsonl to html

    Parameters:
    fn_input (str): The input JSONL file.
    index_column (Union[str, None]): The column to use for indexing (default is 'auto' look at first row for ['qustion', 'prompts], None to disable).
    fn_output (str): The output HTML file (default is 'auto', PATH(fn_input).name[:-len(".jsonl")] + '.html')
    """
    if fn_input is None:
        logging.error("Error: 'fn_input' argument is required.")
        logging.error("Usage: jsonl2html <input_file.jsonl> [--index_column=<column>] [--fn_output=<output.html>]")
        sys.exit(1)
        
    converter = JSONLToHTMLConverter(fn_input, fn_output, index_column, additional_table_content = additional_table_content)
    converter.run()

def main_bash_entry_point():
    #There are a bug inside fire NAME COULD'T BE main
    fire.Fire(convert_jsonl_to_html)

if __name__ == "__main__":
    main_bash_entry_point()