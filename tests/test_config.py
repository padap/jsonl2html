"""
    Test cases for the configuration loading and handling in jsonl2html package.
"""
import json
import tempfile
import os
from pathlib import Path
import pytest
from jsonl2html.config import load_config, Config
from jsonl2html.convert import JSONLToHTMLConverter


def test_load_config_missing_file():
    """Test that load_config raises exception when config file doesn't exist"""
    # Temporarily rename the config file if it exists
    config_path = Path(__file__).parent.parent / "jsonl2html" / "config.json"
    backup_path = config_path.with_suffix(".json.bak")

    config_existed = config_path.exists()
    if config_existed:
        config_path.rename(backup_path)

    try:
        with pytest.raises(FileNotFoundError):
            load_config()
    finally:
        # Restore the config file if it existed
        if config_existed:
            backup_path.rename(config_path)


def test_load_config_valid():
    """Test loading valid configuration"""
    config = load_config()
    assert isinstance(config, Config)
    assert config.max_lines == 10000
    assert config.file_size_warning_mb == 50
    assert config.logging_level == "INFO"
    assert "question" in config.auto_index_columns


def test_config_dataclass():
    """Test that Config is a proper dataclass"""
    config = Config(
        auto_index_columns=["title", "name"],
        max_lines=5000,
        file_size_warning_mb=25,
        logging_level="DEBUG"
    )

    assert config.auto_index_columns == ["title", "name"]
    assert config.max_lines == 5000
    assert config.file_size_warning_mb == 25
    assert config.logging_level == "DEBUG"


def test_converter_with_config():
    """Test that converter properly loads and uses configuration"""
    test_data = [{"title": "Test Title", "content": "Test Content"}]

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.json', delete=False
    ) as f:
        json.dump(test_data, f)
        temp_input_path = f.name

    try:
        converter = JSONLToHTMLConverter(temp_input_path, unicode_stats=False)
        assert hasattr(converter, 'config')
        assert isinstance(converter.config, Config)
        assert hasattr(converter.config, 'auto_index_columns')
        assert hasattr(converter.config, 'max_lines')
    finally:
        os.unlink(temp_input_path)


def test_auto_index_detection():
    """Test auto index column detection from config"""
    test_data = [{"title": "Test Title", "description": "Test Description"}]

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.json', delete=False
    ) as f:
        json.dump(test_data, f)
        temp_input_path = f.name

    try:
        converter = JSONLToHTMLConverter(temp_input_path, unicode_stats=False)
        detected_column = converter.get_auto_index_column(test_data[0])
        # Since "title" is in the default auto_index_columns,
        # it should be detected
        assert detected_column == "title"
    finally:
        os.unlink(temp_input_path)


if __name__ == "__main__":
    test_load_config_missing_file()
    test_load_config_valid()
    test_config_dataclass()
    test_converter_with_config()
    test_auto_index_detection()
    print("All tests passed!")
