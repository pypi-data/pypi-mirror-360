""" Defines and Validates Argument Syntax.
- Encapsulates Argument Parser.
- Returns Argument Data, the args provided by the User.
"""
from argparse import ArgumentParser
from sys import exit

from treescript_diff.input import _validate_name
from treescript_diff.input.argument_data import ArgumentData


def parse_arguments(args: list[str]) -> ArgumentData:
    """ Parse command line arguments.

**Parameters:**
 - args: A list of argument strings.

**Returns:**
 ArgumentData : Container for Valid Argument Data.
    """
    try:
        parsed_args = _define_arguments().parse_args(args)
    except SystemExit:
        exit("Unable to Parse Arguments. 2 TreeScript filenames are required.")
    return _validate_arguments(parsed_args)


def _validate_arguments(
    parsed_arguments
) -> ArgumentData:
    """ Checks the values received from the ArgParser.
 - Uses Validate Name method from StringValidation.

**Parameters:**
 - parsed_arguments : The object returned by the ArgumentParser.

**Returns:**
 ArgumentData - A DataClass of syntactically correct arguments.
    """
    if not _validate_name(original := parsed_arguments.original):
        exit("First TreeScript argument was invalid.")
    if not _validate_name(updated := parsed_arguments.updated):
        exit("Second TreeScript argument was invalid.")
    if parsed_arguments.added and parsed_arguments.removed:
        exit("Added and Removed files are printed by default, separated by a blank line.")
    return ArgumentData(
        original=original,
        updated=updated,
        # Output is Added, Removed, or Both.
        diff_output=parsed_arguments.added if parsed_arguments.added or parsed_arguments.removed else None,
    )


def _define_arguments() -> ArgumentParser:
    """ Initializes and Defines Argument Parser.
 - Sets Required/Optional Arguments and Flags.

**Returns:**
 argparse.ArgumentParser - An instance with all supported Arguments.
    """
    parser = ArgumentParser(
        description="Computes the difference between two TreeScript."
    )
    # Required arguments
    parser.add_argument(
        'original',
        type=str,
        help='The original TreeScript.',
    )
    parser.add_argument(
        'updated',
        type=str,
        help='The updated TreeScript.',
    )
    # Optional Arguments
    parser.add_argument(
        "--added", '-a',
        action='store_true',
        default=False,
        help='Whether to show added files.',
    )
    parser.add_argument(
        "--removed", '-r',
        action='store_true',
        default=False,
        help='Whether to show deleted files.',
    )
    return parser
