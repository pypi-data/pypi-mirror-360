"""The methods of a dictionary-files based diff algorithm.
"""
from typing import Generator

from treescript_files.input_data import InputData
from treescript_files.tree_reader import process_input_data


def load_original(original_tree: str) -> dict:
    """ Convert Original TreeScript into Files, and add them to a dictionary.

**Parameters:**
 - original_tree (str): The original TreeScript.

**Returns:**
 dict - A map containing files as keys.
    """
    files = dict()
    # This is InputData to the TreeScript Files external Package
    files_input_data = InputData(
        tree_input=original_tree,
        parent_path=None
    )
    for node in process_input_data(files_input_data):
        files[node] = ''
    return files


def compare_files(
    original_files: dict,
    updated_tree: str
) -> Generator[str, None, None]:
    """ Compare a dictionary of the original files with the updated TreeScript.

**Parameters:**
 - original_files (dict) : The Dictionary containing the original TreeScript files.
 - updated_tree (str) : The updated TreeScript to be compared for additions.

**Yields:**
 str - The file paths.
    """
    files_input_data = InputData(
        tree_input=updated_tree,
        parent_path=None
    )
    for node in process_input_data(files_input_data):
        if node in original_files:
            del original_files[node]
        else:
            yield node
