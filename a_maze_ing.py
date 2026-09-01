import sys


def read_config_file(path: str) -> list[str]:
    """
        Opens and reads the configuration file safely.
        Returns the content as a list of strings (lines),
        without interpreting the data.
        """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error while reading the file: {e}")
        sys.exit(1)


if len(sys.argv) < 2:
    print(
        "Missing config file argument.\n"
        "Usage: python3 a_maze_ing.py <config_file>"
    )
    sys.exit(1)

if len(sys.argv) > 2:
    print(
        "Too many arguments.\n"
        "Usage: python3 a_maze_ing.py <config_file>"
    )
    sys.exit(1)

config_path = sys.argv[1]
config_lines = read_config_file(config_path)

print(config_lines)
sys.exit(0)
