""" The Difference between Trees.
"""
from typing import Generator

from .dictionary_files_diff import load_original, compare_files


def diff_trees_additions(a: str, b: str) -> Generator[str, None, None]:
    """ The TreeScript files that were added from a to b.

**Parameters:**
 - a (str) : The original TreeScript.
 - b (str) : The updated TreeScript.

**Yields:**
 str - yields elements of the diff.
    """
    # Use Dictionary-based Algorithm
    files = load_original(a)
    yield from compare_files(files, b)


def diff_trees_removals(a: str, b: str) -> Generator[str, None, None]:
    """ The TreeScript files that were removed from a to b.

**Parameters:**
 - a (str) : The original TreeScript.
 - b (str) : The updated TreeScript.

**Yields:**
 Generator[str] - yields elements of the diff.
    """
    yield from diff_trees_additions(b, a)


def diff_trees_double(a: str, b: str) -> tuple[list[str], list[str]]:
    """ The difference between two TreeScript strings.

**Parameters:**
 - a (str) : The original TreeScript.
 - b (str) : The updated TreeScript.

**Returns:**
 tuple[list[str], list[str]] - Container for the additions and removals.
    """
    # Use Dictionary-based Algorithm
    files = load_original(a)
    additions = []
    for n in compare_files(files, b):
        additions.append(n)
    removals = []
    for n in files.keys():
        removals.append(n)
    return additions, removals
