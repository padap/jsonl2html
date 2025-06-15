"""
Create a table of contents for Unicode statistics from a JSONL input file.
"""
# pylint: disable=line-too-long
import json
from typing import Dict
from pandas import DataFrame


def list_of_str_to_links(s: str, n_max_links: int = 50) -> str:

    """
    Convert a JSON string representation of a list of integers into markdown links.

    Parameters
    ----------
    s : str
        A JSON string representation of a list of integers.
    n_max_links : int, optional
        The maximum number of links to display (default is 50).

    Returns
    -------
    str
        A string containing markdown links for the integers in the input list. If the number of links exceeds
        `n_max_links`, only the first and last segments will be displayed, separated by ellipses.

    Notes
    -----
    The returned links are formatted as [item](#index=item), where item is the integer incremented by 1.
    The indexing starts from 1 for display purposes.
    """
    def format_pattern(item: str) -> str:
        return f"[{item}](#index={item})"

    lst = json.loads(s)
    lst.sort()
    lst = [i + 1 for i in lst]  # Increment indices for 1-based index

    if len(lst) > n_max_links:
        l = n_max_links // 2  # noqa: E741
        r = len(lst) - n_max_links // 2
        str_l = ' '.join(format_pattern(item) for item in lst[:l])
        str_r = ' '.join(format_pattern(item) for item in lst[r:])
        return f"{str_l}...{str_r}"
    else:
        return ' '.join(format_pattern(item) for item in lst)


def get_unicode_small_stats(df: DataFrame) -> str:
    """
    Calculate statistics related to bad rows and symbols in a DataFrame.

    Parameters
    ----------
    df : DataFrame
        A pandas DataFrame containing Unicode statistics with columns 'rows', 'block', and 'n_symbols'.

    Returns
    -------
    str
        An HTML-formatted string reporting the percentage of bad rows and symbols.

    Notes
    -----
    Bad rows are defined as those that do not belong to good Unicode blocks.
    The function calculates the total number of bad rows and symbols, as well as their rates compared to all rows and symbols.
    """
    from unicode_stats.block_rules import list_block_good
    bad_rows = set()
    n_bad_symbols = 0

    for row_list, n_symbols in df[~df['block'].isin(list_block_good)][['rows', 'n_symbols']].to_numpy():
        for row_id in json.loads(row_list):
            bad_rows.add(row_id)
            n_bad_symbols += n_symbols

    n_bad_rows = len(bad_rows)
    n_all_rows = df['rows'].apply(json.loads).apply(max).max()
    rate_bad_rows = n_bad_rows / n_all_rows * 100.0

    n_all_symbols = df['n_symbols'].sum()
    rate_bad_symbols = n_bad_symbols / n_all_symbols * 100.0

    return (f"<h1> Bad Rows: {rate_bad_rows:.4f}% </h1> ({n_bad_rows} out of {n_all_rows}) <br>"
            f"<h1> Bad Symbols: {rate_bad_symbols:.4f}% </h1> ({n_bad_symbols} out of {n_all_symbols}) <br>")


def create_table_of_content_unicode_stats(fn_input_jsonl: str) -> Dict[str, str]:
    """
    Create a table of contents for Unicode statistics from a JSONL input file.

    Parameters
    ----------
    fn_input_jsonl : str
        The filename of the JSONL file containing Unicode statistics.

    Returns
    -------
    dict
        A dictionary containing formatted markdown statistics, including bad row and symbol statistics,
        and links for each Unicode block.

    Raises
    ------
    ModuleNotFoundError
        If the unicode_stats module cannot be found.

    Notes
    -----
    This function processes the data to provide a summarized view of Unicode statistics,
    dropping unnecessary columns and organizing the results into a markdown format.
    """

    # pylint: disable=all
    try:
        from unicode_stats.block_rules import list_block_good
        from unicode_stats.aggregation import AggregatedUnicodeBlockParser
        agregated_parser = AggregatedUnicodeBlockParser(columns=None)
        df = agregated_parser.get_stats(fn_input_jsonl)
    except ModuleNotFoundError:
        raise ModuleNotFoundError("unicode_stats module is not installed.")
    # pylint: enable=all

    df['url'] = df['rows'].apply(list_of_str_to_links)
    df.drop(columns=['example_first', 'example_last'], errors='ignore', inplace=True)

    df.sort_values(["column", "block"], inplace=True)

    res = {
        'unicode_stats': get_unicode_small_stats(df),
        'CONCERNS': df[~df['block'].isin(list_block_good)].drop("rows", axis=1).to_markdown(index=False)
    }

    for column_name, df_small in df.groupby('column'):
        res[column_name] = df_small.drop("rows", axis=1).to_markdown(index=False)

    df['url'] = df['rows'].apply(lambda x: list_of_str_to_links(x, n_max_links=1_000_000))
    res['ALL_LINKS'] = df.drop("rows", axis=1).to_markdown(index=False)

    return res
