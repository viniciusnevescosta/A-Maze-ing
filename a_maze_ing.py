import sys

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

print(sys.argv[1])
sys.exit(0)
