"""
Test cases for the create_table_of_content module.
"""
# pylint: disable=line-too-long
import json
import tempfile
import os
import pytest
import pandas as pd

from jsonl2html.create_table_of_content import list_of_str_to_links, create_table_of_content_unicode_stats
from jsonl2html.convert import JSONLToHTMLConverter, convert_jsonl_to_html

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


# def test_get_unicode_small_stats():
#     """Test get_unicode_small_stats function."""
#     result = get_unicode_small_stats(sample_dataframe)
#     assert "Bad Rows:" in result
#     assert "Bad Symbols:" in result
# Check if unicode_stats is available
UNICODE_STATS_AVALIABLE = True
try:
    import unicode_stats  # noqa: F401 WO611
except ImportError:
    UNICODE_STATS_AVALIABLE = False


@pytest.mark.skipif(not UNICODE_STATS_AVALIABLE, reason="unicode_stats library not available")
def test_create_table_of_content_unicode_stats_avaliable():
    """Test create_table_of_content_unicode_stats function."""
    create_table_of_content_unicode_stats("examples/small.jsonl")


@pytest.mark.skipif(UNICODE_STATS_AVALIABLE, reason="unicode_stats library available")
def test_create_table_of_content_unicode_stats_not_avaliable():
    """Test create_table_of_content_unicode_stats function."""
    try:
        create_table_of_content_unicode_stats("examples/small.jsonl")
    except ModuleNotFoundError:
        print("Ok, unicode_stats library not available, skipping unicode_stats=True test")
        return

    raise ValueError("unicode_stats library should be available for this test")


def test_converter_unicode_stats_false():
    """Test converter with unicode_stats=False (should always work)"""
    test_data = [{"title": "Test Title", "content": "Test Content"}]

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.json', delete=False
    ) as f:
        json.dump(test_data, f)
        temp_input_path = f.name

    try:
        converter = JSONLToHTMLConverter(temp_input_path, unicode_stats=False)
        assert converter.unicode_stats is False
        # Should work even if unicode_stats library is not available
        converter.run()
        assert os.path.exists(converter.fn_output)
    finally:
        os.unlink(temp_input_path)
        if os.path.exists(converter.fn_output):
            os.unlink(converter.fn_output)

# def test_converter_unicode_stats_true_default():
#     """Test converter with unicode_stats=True (default behavior)"""
#     test_data = [{"title": "Test Title", "content": "Test Content"}]

#     with tempfile.NamedTemporaryFile(
#         mode='w', suffix='.json', delete=False
#     ) as f:
#         json.dump(test_data, f)
#         temp_input_path = f.name

#     try:
#         converter = JSONLToHTMLConverter(temp_input_path, unicode_stats=False)  # Default is True
#         assert converter.unicode_stats is True
#         # Should handle gracefully even if unicode_stats library is not available
#         converter.run()
#         assert os.path.exists(converter.fn_output)
#     finally:
#         os.unlink(temp_input_path)
#         if os.path.exists(converter.fn_output):
#             os.unlink(converter.fn_output)


@pytest.mark.skipif(not UNICODE_STATS_AVALIABLE, reason="unicode_stats library not available")
def test_converter_unicode_stats_true_with_library():
    """Test converter with unicode_stats=True when unicode_stats library is available"""
    test_data = [{"title": "Test Title", "content": "Test Content"}]

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.json', delete=False
    ) as f:
        json.dump(test_data, f)
        temp_input_path = f.name

    try:
        converter = JSONLToHTMLConverter(temp_input_path, unicode_stats=True)
        assert converter.unicode_stats is True
        converter.run()
        assert os.path.exists(converter.fn_output)

        # Read the generated HTML and check if it contains unicode stats
        with open(converter.fn_output, 'r', encoding='utf-8') as f:
            html_content = f.read()
        # The HTML should contain base64 encoded data that includes unicode stats
        assert 'BASE64STRING' not in html_content  # Should be replaced

    finally:
        os.unlink(temp_input_path)
        if os.path.exists(converter.fn_output):
            os.unlink(converter.fn_output)


def test_convert_function_unicode_stats_parameter():
    """Test that convert_jsonl_to_html function accepts unicode_stats parameter"""
    test_data = [{"title": "Test Title", "content": "Test Content"}]

    # Create temp input file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_input_path = f.name

    temp_output_path = temp_input_path.replace('.json', '.html')

    try:
        # Test with unicode_stats=False
        convert_jsonl_to_html(
            fn_input=temp_input_path,
            fn_output=temp_output_path,
            unicode_stats=False
        )
        assert os.path.exists(temp_output_path)
        os.unlink(temp_output_path)

        # Conditional test for unicode_stats=True
        try:
            from jsonl2html import UNICODE_STATS_AVALIABLE
        except ImportError:
            UNICODE_STATS_AVALIABLE = False

        if UNICODE_STATS_AVALIABLE:
            convert_jsonl_to_html(
                fn_input=temp_input_path,
                fn_output=temp_output_path,
                unicode_stats=True
            )
            assert os.path.exists(temp_output_path)
            os.unlink(temp_output_path)
        else:
            print("unicode_stats library not available, skipping unicode_stats=True test")

    finally:
        os.unlink(temp_input_path)
        if os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
