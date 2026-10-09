"""Analyze usable passages and dead ends in a maze."""

from mazegen.maze.grid import Direction, MazeGrid

Coordinate = tuple[int, int]


def is_dead_end(
    maze: MazeGrid,
    x: int,
    y: int,
    reserved: set[Coordinate] | None = None,
) -> bool:
    """Return whether a nonreserved cell has exactly one usable passage.

    Raises:
        ValueError: If the source coordinates are outside the maze.
    """
    cell = maze.get_cell(x, y)
    blocked: set[Coordinate] = set() if reserved is None else reserved

    if (x, y) in blocked:
        return False

    opposite: dict[Direction, Direction] = {
        "north": "south",
        "east": "west",
        "south": "north",
        "west": "east",
    }

    passages = 0

    for direction, coordinate in maze.get_neighbors(x, y).items():
        if coordinate in blocked:
            continue

        neighbor = maze.get_cell(*coordinate)

        if getattr(cell, direction):
            continue

        if getattr(neighbor, opposite[direction]):
            continue

        passages += 1

    return passages == 1
