import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import json
from jsonl2html.create_table_of_content import list_of_str_to_links, get_unicode_small_stats, create_table_of_content_unicode_stats

sample_dataframe = pd.DataFrame({
    'rows': ['[1, 2]', '[3]', '[4, 5]'],
    'block': ['good_block', 'bad_block', 'good_block'],
    'n_symbols': [5, 10, 15]
})

@pytest.mark.parametrize("input_str, expected_output", [
    ('[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]', 
     "[1](#index=1) [2](#index=2) [3](#index=3) [4](#index=4) [5](#index=5) [6](#index=6) [7](#index=7) [8](#index=8) [9](#index=9) [10](#index=10)"),
    (json.dumps([0, 1, 2, 3, 4, 5]), "[1](#index=1) [2](#index=2) [3](#index=3) [4](#index=4) [5](#index=5) [6](#index=6)"),
])
def test_list_of_str_to_links(input_str, expected_output):
    """Test list_of_str_to_links function."""
    assert list_of_str_to_links(input_str) == expected_output

def test_get_unicode_small_stats():
    """Test get_unicode_small_stats function."""
    result = get_unicode_small_stats(sample_dataframe)
    assert "Bad Rows:" in result
    assert "Bad Symbols:" in result

def test_create_table_of_content_unicode_stats():
    """Test create_table_of_content_unicode_stats function."""
    create_table_of_content_unicode_stats("examples/small.jsonl")
    