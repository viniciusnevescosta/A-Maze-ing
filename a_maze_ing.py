import sys

if len(sys.argv) != 2:
    print("Usage: python a_maze_ing.py <filename>")
    sys.exit(1)

print(sys.argv[1])
sys.exit(0)
