"""
jsonl2html - A package for converting JSONL files to HTML format.
"""
__version__ = "0.3.0"
from .config import load_config
from .logger import setup_logger
from .convert import convert_jsonl_to_html

config = load_config()
setup_logger(config)

__all__ = ["convert_jsonl_to_html"]
