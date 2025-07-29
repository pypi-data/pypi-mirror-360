#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
String formatting filewise module.

This module provides functions to handle different types of string formatting:
- F-strings using Python's format method
- %-strings (percent-strings) using old-style string formatting

Additionally, it contains simple tools to beautify the output format of strings

Functions
---------
- format_string(string2format, arg_obj):
    Formats a given string using Python's format method based on the type of arg_obj.
    
- print_format_string(string2format, arg_obj, end="\n"):
    Formats and prints a given string using Python's format method, optionally specifying an end character.
    
- print_percent_string(string2format, arg_obj):
    Formats and prints a string using old-style percent formatting (%-strings).
    
- string_underliner(string, underline_char):
    Underlines a single- or multiple-line string, using the given character.
"""

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_type_str
from pygenutils.arrays_and_lists.data_manipulation import flatten_list
from pygenutils.strings.string_handler import find_substring_index

#-------------------------#
# Define custom functions #
#-------------------------#

# %%

# String format management #
#--------------------------#

# F-strings #
def format_string(string2format, arg_obj):
    """
    Format a string using Python's format method.

    Args
    ----
    string2format : str
        The string to be formatted.
    arg_obj : list | tuple | np.ndarray
        The object used to fill in the placeholders in 'string2format'.

    Returns
    -------
    str: Formatted string.

    Raises
    ------
    TypeError: If arg_obj is not of the expected type.
    IndexError: If there are not enough indices referenced in the string to format.
    SyntaxError: If there are syntax errors in the formatting object.
    """
    bracket_index_list = find_substring_index(string2format, "{}",
                                              advanced_search=True,
                                              all_matches=True)
    
    # Ensure bracket_index_list is always a list
    if not isinstance(bracket_index_list, list):
        bracket_index_list = [bracket_index_list]
    
    num_brackets = len(bracket_index_list)
    
    try:               
        if (get_type_str(arg_obj) in MAIN_INPUT_DTYPE_LIST_STRFMT\
            and num_brackets >= 2):
            formatted_string = string2format.format(*arg_obj)
            
        elif ((get_type_str(arg_obj) in MAIN_INPUT_DTYPE_LIST_STRFMT and num_brackets < 2)\
            or (get_type_str(arg_obj) not in MAIN_INPUT_DTYPE_LIST_STRFMT\
            and not isinstance(arg_obj, dict))):
            formatted_string = string2format.format(arg_obj)
        
        elif isinstance(arg_obj, dict):
            formatted_string = string2format.format(**arg_obj)
           
        return formatted_string
    
    except (TypeError, UnboundLocalError):
        raise TypeError(TYPE_ERROR_STR1)
    
    except IndexError:
        raise IndexError(INDEX_ERROR_STR)
    
    except SyntaxError:
        raise SyntaxError(SYNTAX_ERROR_STR)
        
        
def print_format_string(string2format, arg_obj, end="\n"):
    """
    Format and print a string using Python's format method.

    Args
    ----
    string2format : str
        The string to be formatted and printed.
    arg_obj : list | tuple | np.ndarray
        The object used to fill in the placeholders in string2format.
    end : str, optional
        String appended after the last value, default is "\n".

    Raises
    ------
    TypeError: If arg_obj is not of the expected type.
    IndexError: If there are not enough indices referenced in the string to format.
    SyntaxError: If there are syntax errors in the formatting object.
    """
    try:
        formatted_string = format_string(string2format, arg_obj)
    except Exception as e:
        raise Exception(f"An error occurred: {e}") from e
    else:
        print(formatted_string, end=end)

    
# %-strings (percent-strings) #
def print_percent_string(string2format, arg_obj):
    """
    Format and print a string using old-style percent formatting (%-strings).

    Args
    ----
    string2format : str
        The string to be formatted and printed.
    arg_obj : str
        The string object to be formatted using the % operator.

    Raises
    ------
    TypeError: If arg_obj is not of type 'str'.
    IndexError: If there are not enough indices referenced in the string to format.
    """
    try:
        if isinstance(arg_obj, str):
            print(string2format % (arg_obj))
        else:
            raise TypeError(TYPE_ERROR_STR2)
            
    except TypeError:
        raise TypeError(TYPE_ERROR_STR1)
                
    except IndexError:
        raise IndexError(INDEX_ERROR_STR)
        
    except SyntaxError:
        raise SyntaxError(SYNTAX_ERROR_STR)
        
# %%

# String font effects #
#---------------------#

def string_underliner(string, underline_char="-"):
    """
    Underlines a given string with the specified character.
    
    If the string contains multiple lines, each line will be underlined
    individually with the same character, keeping the length of the underline
    consistent with each line's length.
    
    Parameters
    ----------
    string : str
        The string to be underlined. It can be single or multiline.
        
    underline_char : str, optional
        The character used to underline the string.
        Defaults to a dash ("-").
    
    Returns
    -------
    str_underlined : str
        The original string with an underline applied to each line. 
        For multiline strings, each line is individually underlined.
    
    Example
    -------
    For a single-line string:
    
    >>> string_underliner("Hello", "*")
    'Hello\n*****'
    
    For a multiline string:
    
    >>> string_underliner("Hello\nWorld", "*")
    'Hello\n*****\nWorld\n*****'
    """
    
    # Check if the string contains newlines, indicating a multiline string
    newline_char = "\n"
    multiline = newline_char in string
    
    if multiline:
        # Split the string into individual lines
        word_list = string.split(newline_char)
        
        # Build the underlined string by iterating over each line
        str_underlined = ""
        for word in word_list:
            len_word = len(word)
            # Underline each word with the specified character repeated to match the word's length
            str_underlined += f"{word}\n{underline_char * len_word}\n"
        
        # Remove the last newline character to avoid an extra empty line
        str_underlined = str_underlined.rstrip(newline_char)
        
    else:
        # For a single-line string, simply apply the underline
        len_string = len(string)
        str_underlined = f"{string}\n{underline_char * len_string}"

    return str_underlined

# %%

# Table Formatters #
#------------------#

def format_table(nested_dict,
                 keys=None, 
                 display_index=True,
                 index_header='Index',
                 column_delimiter="|"):
    """
    Format a nested dictionary into a table string with specific formatting rules.
    
    Note
    ----
    The keys in every subdictionary must represent a value in a generic scope.
    For example, use {'flora': 'grass', 'fruit': 'apple'} 
    instead of {'grass': 'green', 'apple': 'red'}
    to avoid long headers and ensure a clean table format.
    
    If the `keys` argument is None, the keys of the first subdictionary
    in the nested dictionary will be used as the column names. 
    This is to avoid long headers and maintain a consistent table structure.
    However, if the subdictionaries contain specific keys, this mechanism 
    will cause those specific keys to be lost in favour of the generic keys 
    from the first subdictionary.
    
    The key list corresponding to every subdictionary must be of the same length,
    otherwise a ValueError is raised.
    A tip to avoid this error would be to set the value to None for any of the keys, 
    if that key is not going to be used.

    Parameters
    ----------
    nested_dict : dict[str, dict]
        A nested dictionary to format.
    keys : list[str] | None, optional
        An optional list of keys to use as column names.
    display_index : bool, optional
        Whether to display the index column. Default is True.
    index_header : str, optional
        If display_index= True, use this name for the column that contains indices.
        Default name is 'Index'.
    column_delimiter : str
        Character to delimit the columns, applying both for the header and the content.
    
    Raises
    ------
    ValueError
        If subdictionaries have different lengths or if the keys list length does not match.
    
    Returns
    -------
    table : str
        The formatted table string.
    """
    if not nested_dict:
        raise ValueError("The nested dictionary is empty.")
    
    # Ensure all subdictionaries are of the same length
    first_len = len(next(iter(nested_dict.values())))
    if not all(len(subdict) == first_len for subdict in nested_dict.values()):
        raise ValueError("All subdictionaries in the nested dictionary must be "
                         "of the same length.")
    
    # Use the keys from the first subdictionary if not provided
    if keys is None:
        keys = list(next(iter(nested_dict.values())).keys())
    else:
        # Ensure the provided keys list length matches the subdictionaries' keys length
        if len(keys) != first_len:
            raise ValueError("The length of the keys list must match the length "
                             "of the subdictionaries' keys.")
    
    # Calculate max width for each column
    column_widths = {key: len(key) for key in keys}
    for subdict in nested_dict.values():
        for idx, key in enumerate(keys):
            original_key = list(subdict.keys())[idx]
            value = subdict.get(original_key, "")
            column_widths[key] = max(column_widths[key], len(str(value)))

    # Create the header row
    if display_index:
        max_index_width = max(len(str(idx)) for idx in nested_dict.keys())
        column_widths[index_header] = max(len(index_header), max_index_width)
        headers = [index_header] + keys
    else:
        headers = keys
    
    # Build the header string
    header_row = column_delimiter + \
                 column_delimiter.join(f"{header:^{column_widths[header]}}" 
                                       for header in headers) + \
                 column_delimiter
    
    # Build the header underline string
    underline_row = column_delimiter + \
                    column_delimiter.join('=' * column_widths[header]
                                          for header in headers) + \
                    column_delimiter
    
    # Build the content rows
    content_rows = []
    for idx, subdict in nested_dict.items():
        if display_index:
            row = [f"{idx:^{column_widths[index_header]}}"]
        else:
            row = []
        for key in keys:
            original_key = list(subdict.keys())[keys.index(key)]
            value = subdict.get(original_key, "")
            row.append(f"{str(value):^{column_widths[key]}}")
        content_rows.append(column_delimiter + column_delimiter.join(row) + column_delimiter)
    
    # Combine all parts
    table = '\n'.join([header_row, underline_row] + content_rows)
    return table

# # Example usage
# nested_dict = {
#     1: {'key1': 'val11', 'key2': 'val12'},
#     2: {'key1': 'val21', 'key2': 'val22'},
#     3: {'key1': 'val31', 'key2': 'val32'}
# }

# # Print the table with the index
# print(format_table(nested_dict, display_index=True))

# # Print the table without the index
# print(format_table(nested_dict, display_index=False))

# # Print the table with custom headers
# custom_keys = ['Column1', 'Column2']
# print(format_table(nested_dict, keys=custom_keys, display_index=True))


def format_table_from_list(dict_list,
                           keys=None,
                           display_index=True,
                           index_header='Index',
                           custom_start_index=1,
                           column_delimiter="|"):
    """
    Format a list of dictionaries into a table string with specific formatting rules.
    
    Note
    ----
    The keys in every dictionary must represent a value in a generic scope.
    For example, use {'flora': 'grass', 'fruit': 'apple'}
    instead of {'grass': 'green', 'apple': 'red'}
    to avoid long headers and ensure a clean table format.
    
    If the `keys` argument is None, the keys of the first dictionary in the list
    will be used as the column names.
    This is to avoid long headers and maintain a consistent table structure.
    However, if the dictionaries contain specific keys, this mechanism will cause
    those specific keys to be lost in favour of the generic keys from the
    first dictionary.
    
    The key list corresponding to every dictionary must be of the same length,
    otherwise a ValueError is raised.
    A tip to avoid this error would be to set the value to None for any of the keys, 
    if that key is not going to be used.

    Parameters
    ----------
    dict_list : list[dict]
        A list of dictionaries to format.
    keys : list[str] | None, optional
        An optional list of keys to use as column names.
    display_index : bool, optional
        Whether to display the index column. Default is True.
    index_header : str, optional
        If display_index= True, use this name for the column that contains indices.
        Default name is 'Index'.
    custom_start_index : int
        If display_index = True, set the number for the index to start from.
        Default value is 1.
    column_delimiter : str
        Character to delimit the columns, applying both for the header and the content.    
        
    
    Raises
    ------
    ValueError
        If dictionaries have different lengths or if the keys list length does not match.
    
    Returns
    -------
    table : str
        The formatted table string.
    """
    if not dict_list:
        raise ValueError("The dictionary list is empty.")
    else:
        if isinstance(dict_list, dict):
            dict_list = [dict_list]
    
    # Handle nested lists by flattening them first
    if isinstance(dict_list, list) and any(isinstance(item, list) for item in dict_list):
        dict_list = flatten_list(dict_list)
    
    # Ensure all dictionaries are of the same length
    first_len = len(dict_list[0])
    if not all(len(d) == first_len for d in dict_list):
        raise ValueError("All dictionaries in the list must be of the same length.")
    
    # Use the keys from the first dictionary if not provided
    if keys is None:
        keys = list(dict_list[0].keys())
    else:
        # Ensure the provided keys list length matches the dictionaries' keys length
        if len(keys) != first_len:
            raise ValueError("The length of the keys list must match the length "
                             "of the dictionaries' keys.")
    
    # Calculate max width for each column
    column_widths = {key: len(key) for key in keys}
    for subdict in dict_list:
        for idx, key in enumerate(keys):
            original_key = list(subdict.keys())[idx]
            value = subdict.get(original_key, "")
            column_widths[key] = max(column_widths[key], len(str(value)))

    # Create the header row
    if display_index:
        max_index_width = max(len(str(idx)) for idx in range(1, len(dict_list) + 1))
        column_widths[index_header] = max(len(index_header), max_index_width)
        headers = [index_header] + keys
    else:
        headers = keys
    
    # Build the header string
    header_row = column_delimiter + \
                 column_delimiter.join(f"{header:^{column_widths[header]}}" 
                                       for header in headers) + \
                 column_delimiter
    
    # Build the header underline string
    underline_row = column_delimiter + \
                    column_delimiter.join('=' * column_widths[header] 
                                          for header in headers) + \
                    column_delimiter
    
    
    # Build the content rows
    content_rows = []
    for idx, subdict in enumerate(dict_list, start=custom_start_index):
        if display_index:
            row = [f"{idx:^{column_widths[index_header]}}"]
        else:
            row = []
        for key in keys:
            original_key = list(subdict.keys())[keys.index(key)]
            value = subdict.get(original_key, "")
            row.append(f"{str(value):^{column_widths[key]}}")
        content_rows.append(column_delimiter + column_delimiter.join(row) + column_delimiter)
    
    # Combine all parts
    table = '\n'.join([header_row, underline_row] + content_rows)
    return table

# # Example usage
# # dict_list = [
# #     {'key1': 'val11', 'key2': 'val12'},
# #     {'key1': 'val21', 'key2': 'val22'},
# #     {'key1': 'val31', 'key2': 'val32'}
# # ]

# dict_list = [
#     {'bayern': 'alemania', 'leipzig': 'alemania'},
#     {'olaizola': 'aimar', 'irujo': 'juan'},
#     {'ziskar II': 'karlos', 'lujan': 'vladimir'}
# ]

# # Print the table with the index
# print(format_table_from_list(dict_list, display_index=True))
# print(2*"\n")

# # Print the table without the index
# print(format_table_from_list(dict_list, display_index=False))
# print(2*"\n")

# # Print the table with custom headers
# custom_keys = ['Futbola', 'Esku pilota edo pala']
# print(format_table_from_list(dict_list, keys=custom_keys, display_index=True))


def format_table_from_lists(keys, values,
                            display_index=True, 
                            index_header='Index',
                            custom_start_index=1,
                            column_delimiter="|"):
    """
    Format a list of keys and corresponding list of values into a neatly aligned table.
    
    Parameters
    ----------
    keys : list[str]
        A list of column headers for the table.
    values : list | list[list]
        A list containing the row values. If each element of `values` is a list,
        then it is treated as a row; otherwise, `values` is treated as a single row.
    display_index : bool, optional
        Whether to display an index column in the table. Default is True.
    index_header : str, optional
        The header name for the index column, if `display_index` is True.
        Default is 'Index'.
    custom_start_index : int, optional
        The starting number for the index column, if `display_index` is True.
        Default is 1.
    column_delimiter : str
        Character to delimit the columns, applying both for the header and the content.
            
    Raises
    ------
    ValueError
        If the number of keys does not match the number of elements in any row of `values`.
    
    Returns
    -------
    table : str
        The formatted table as a string.
    
    Examples
    --------
    Single row:
    >>> format_table_from_lists(['Key1', 'Key2'], ['Value1', 'Value2'])
    | Key1 | Key2 |
    |======|======|
    |Value1|Value2|
    
    Multiple rows:
    >>> format_table_from_lists(['Key1', 'Key2'], [['Value1', 'Value2'], ['Value3', 'Value4']])
    | Key1 | Key2 |
    |======|======|
    |Value1|Value2|
    |Value3|Value4|
    """
    
    # Determine if values contain multiple rows or just one
    if all(isinstance(v, list) for v in values):
        rows = values
        # Check if all rows have the same length as keys
        for i, row in enumerate(rows):
            if len(row) != len(keys):
                raise ValueError(f"Length of keys and values row at index {i} do not match.")
    else:
        if len(values) != len(keys):
            raise ValueError("Length of keys and values do not match. "
                             "If values contain multiple rows, ensure "
                             "all components are lists.")
        rows = [values]

    # Calculate max width for each column
    column_widths = {key: len(key) for key in keys}
    for row in rows:
        for key, value in zip(keys, row):
            column_widths[key] = max(column_widths[key], len(str(value)))

    # Create the header row
    if display_index:
        max_index_width = len(str(len(rows)))
        column_widths[index_header] = max(len(index_header), max_index_width)
        headers = [index_header] + keys
    else:
        headers = keys
    
    # Build the header string
    header_row = column_delimiter + column_delimiter.join(f"{header:^{column_widths[header]}}" 
                                                          for header in headers) + column_delimiter
    
    # Build the header underline string
    underline_row = column_delimiter + \
                    column_delimiter.join('=' * column_widths[header]
                                          for header in headers) + \
                    column_delimiter
    
    # Build the content rows
    content_rows = []
    for idx, row in enumerate(rows, start=custom_start_index):
        if display_index:
            row_content = [f"{idx:^{column_widths[index_header]}}"]
        else:
            row_content = []
        for key, value in zip(keys, row):
            row_content.append(f"{str(value):^{column_widths[key]}}")
        content_rows.append(column_delimiter + column_delimiter.join(row_content) + column_delimiter)
    
    # Combine all parts
    table = '\n'.join([header_row, underline_row] + content_rows)
    return table


# # Example usage
# keys = ['Key1', 'Key2']
# values = [['Value1', 'Value2'], ['Value3', 'Value4']]

# # Print the table with the index
# print(format_table_from_lists(keys, values, display_index=True))
# print(2*"\n")

# # Print the table without the index
# print(format_table_from_lists(keys, values, display_index=False))

# %%

#--------------------------#
# Parameters and constants #
#--------------------------#

# Frequent input data types for string formatting #
MAIN_INPUT_DTYPE_LIST_STRFMT = ["list", "ndarray", "tuple"]

# Error strings #
TYPE_ERROR_STR1 = "Check the iterable type passed to the instance."
TYPE_ERROR_STR2 = "Argument must be of type 'str' only."

INDEX_ERROR_STR = "Not all indices were referenced in the string to format."

SYNTAX_ERROR_STR = "One or more arguments in the formatting object "\
                    "has strings with unclosed quotes."
