""" Validate System Arguments into usable InputData.
"""
from treescript_diff.input.input_data import InputData


def _validate_name(argument) -> bool:
    """ Determine whether an argument is a non-empty string.
 - Does not count whitespace.
 - Uses the strip method to remove empty space.

**Parameters:**
 - argument (str): The given argument.

**Returns:**
 bool - True if the argument qualifies as valid.
    """
    if argument is None or not isinstance(argument, str):
        return False
    elif len(argument.strip()) < 1 or not argument.isascii():
        return False
    return True


def validate_arguments(args: list[str]) -> InputData:
    """ Validate Command Line Arguments into usable InputData.
    """
    from treescript_diff.input.argument_parser import parse_arguments
    from treescript_diff.input.file_validation import validate_input_file
    arg_data = parse_arguments(args)
    return InputData(
        original_tree=validate_input_file(arg_data.original),
        updated_tree=validate_input_file(arg_data.updated),
        diff_output=arg_data.diff_output,
    )
