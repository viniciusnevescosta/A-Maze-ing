"""Write the hexadecimal maze, endpoints and shortest path."""

import os
from pathlib import Path
from tempfile import mkstemp

from mazegen.maze.encoding import maze_to_hex
from mazegen.maze.grid import MazeGrid

Coordinate = tuple[int, int]


def write_maze(
    maze: MazeGrid,
    output_file: str,
    entry: Coordinate,
    exit: Coordinate,
    shortest_path: str,
) -> None:
    """Write maze rows, endpoints and N/E/S/W movements.

    Raises:
        ValueError: If coordinates or movement characters are invalid.
        OSError: If the output file cannot be opened or written.
    """
    maze.get_cell(*entry)
    maze.get_cell(*exit)

    for direction in shortest_path:
        if direction not in "NESW":
            raise ValueError(f"Invalid shortest path direction: {direction}")

    rows = maze_to_hex(maze)

    destination = Path(output_file)
    descriptor, temporary = mkstemp(
        prefix=".maze-", suffix=".tmp", dir=destination.parent,
    )
    os.close(descriptor)
    try:
        with open(temporary, "w", encoding="utf-8", newline="\n") as file:
            for row in rows:
                file.write(row + "\n")
            file.write("\n")
            file.write(f"{entry[0]},{entry[1]}\n")
            file.write(f"{exit[0]},{exit[1]}\n")
            file.write(shortest_path + "\n")
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
