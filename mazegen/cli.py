import sys
from collections.abc import Sequence

from mazegen.config.parser import filter_valid_lines, parse_config_lines
from mazegen.config.reader import read_config_file
from mazegen.config.validator import (
    MissingRequiredKeysError,
    UnknownConfigKeysError,
    convert_dimensions,
    validate_required_keys,
    validate_unknown_keys,
)

USAGE = "Usage: python3 a_maze_ing.py <config_file>"


def main(argv: Sequence[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv

    if len(arguments) < 1:
        print(f"Missing config file argument.\n{USAGE}", file=sys.stderr)
        return 1

    if len(arguments) > 1:
        print(f"Too many arguments.\n{USAGE}", file=sys.stderr)
        return 1

    config_path = arguments[0]

    try:
        config_lines = read_config_file(config_path)
    except FileNotFoundError:
        print(
            f"Error: The file '{config_path}' was not found.", file=sys.stderr
        )
        return 1
    except PermissionError:
        print(
            f"Error: Permission denied while reading "
            f"the file '{config_path}'.",
            file=sys.stderr,
        )
        return 1
    except OSError as error:
        print(
            f"Unexpected error while reading the file: "
            f"'{config_path}': {error}",
            file=sys.stderr,
        )
        return 1

    filtered_lines = filter_valid_lines(config_lines)
    try:
        parsed_config = parse_config_lines(filtered_lines)
    except ValueError as error:
        print(f"Config error: {error}", file=sys.stderr)
        return 1

    try:
        validate_required_keys(parsed_config)
    except MissingRequiredKeysError as error:
        print(f"Config error: {error}", file=sys.stderr)
        return 1

    try:
        validate_unknown_keys(parsed_config)
    except UnknownConfigKeysError as error:
        print(f"Config error: {error}", file=sys.stderr)
        return 1

    try:
        converted_config = convert_dimensions(parsed_config)
    except ValueError as error:
        print(f"Config error: {error}", file=sys.stderr)
        return 1

    print(converted_config)
    return 0
