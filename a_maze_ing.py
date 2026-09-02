import sys


def read_config_file(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as file:
            return [line.rstrip("\r\n") for line in file]
    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(
            f"Error: Permission denied while reading the file '{path}'.",
            file=sys.stderr,
        )
        sys.exit(1)
    except OSError as e:
        print(
            f"Unexpected error while reading the file: '{path}': {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def filter_valid_lines(lines: list[str]) -> list[str]:
    valid_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        valid_lines.append(line)

    return valid_lines


if len(sys.argv) < 2:
    print(
        "Missing config file argument.\n"
        "Usage: python3 a_maze_ing.py <config_file>",
        file=sys.stderr,
    )
    sys.exit(1)

if len(sys.argv) > 2:
    print(
        "Too many arguments.\nUsage: python3 a_maze_ing.py <config_file>",
        file=sys.stderr,
    )
    sys.exit(1)

config_path = sys.argv[1]

config_lines = filter_valid_lines(read_config_file(config_path))

print(config_lines)
sys.exit(0)
