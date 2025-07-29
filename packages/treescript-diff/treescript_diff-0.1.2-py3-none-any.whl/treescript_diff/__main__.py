#!/usr/bin/python
from pathlib import Path


def main():
    # Author: DK96-OS 2024 - 2025
    from sys import argv
    from treescript_diff import ts_diff, input
    #
    input_data = input.validate_arguments(argv[1:])
    output_data = ts_diff(input_data)
    print(output_data)


if __name__ == "__main__":
    from sys import path
    # Get the directory of the current file (__file__ is the path to the script being executed)
    # Add the directory to sys.path
    path.append(str(Path(__file__).resolve().parent.parent))
    main()
