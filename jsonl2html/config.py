"""
jsonl2html configuration module
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Config:
    """Configuration dataclass for jsonl2html"""
    auto_index_columns: List[str]
    max_lines: int
    file_size_warning_mb: int
    logging_level: str


def load_config() -> Config:
    """Load configuration from config.json file"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r', encoding="utf-8") as f:
        config_dict = json.load(f)
    return Config(**config_dict)
