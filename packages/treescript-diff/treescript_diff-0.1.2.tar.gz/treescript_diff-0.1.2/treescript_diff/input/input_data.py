""" Input Data for the TreeScript-Diff.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class InputData:
    """ Dataclass container for TreeScript-Diff program input.

**Fields:**
 - original_tree (str): The "before" TreeScript.
 - updated_tree (str): The "after" TreeScript.
 - diff_output (bool?): Whether to output additions or subtractions. Default: None, prints one after the other, separated by additional newline.
    """
    original_tree: str
    updated_tree: str
    diff_output: bool | None = None
