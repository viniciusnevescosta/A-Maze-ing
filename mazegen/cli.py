import sys
from collections.abc import Sequence

from mazegen.config.parser import filter_valid_lines
from mazegen.config.reader import read_config_file

USAGE = "Usage: python3 a_maze_ing.py <config_file>"


def main(argv: Sequence[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv

    if len(arguments) < 1:
        print(
            f"Missing config file argument.\n{USAGE}",
            file=sys.stderr,
        )
        return 1

    if len(arguments) > 1:
        print(
            f"Too many arguments.\n{USAGE}",
            file=sys.stderr,
        )
        return 1

    config_path = arguments[0]

    try:
        config_lines = read_config_file(config_path)
    except FileNotFoundError:
        print(
            f"Error: The file '{config_path}' was not found.",
            file=sys.stderr
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

    valid_lines = filter_valid_lines(config_lines)
    print(valid_lines)
    return 0
