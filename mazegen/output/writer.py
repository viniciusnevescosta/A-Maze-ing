"""Write the hexadecimal maze and its endpoint coordinates."""

from mazegen.maze.encoding import maze_to_hex
from mazegen.maze.grid import MazeGrid

Coordinate = tuple[int, int]


def write_maze(
    maze: MazeGrid,
    output_file: str,
    entry: Coordinate,
    exit: Coordinate,
) -> None:
    """Write maze rows, a blank line, entry and exit.

    Raises:
        ValueError: If either coordinate is outside the maze.
        OSError: If the output file cannot be opened or written.
    """
    maze.get_cell(*entry)
    maze.get_cell(*exit)
    rows = maze_to_hex(maze)

    with open(output_file, "w", encoding="utf-8", newline="\n") as file:
        for row in rows:
            file.write(row + "\n")

        file.write("\n")
        file.write(f"{entry[0]},{entry[1]}\n")
        file.write(f"{exit[0]},{exit[1]}\n")
