"""Write hexadecimal maze rows to an output file."""

from mazegen.maze.encoding import maze_to_hex
from mazegen.maze.grid import MazeGrid


def write_maze(maze: MazeGrid, output_file: str) -> None:
    """Write hexadecimal rows, replacing existing file contents.

    Raises:
        OSError: If the output file cannot be opened or written.
    """
    rows = maze_to_hex(maze)

    with open(output_file, "w", encoding="utf-8", newline="\n") as file:
        for row in rows:
            file.write(row + "\n")
