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


def count_dead_ends(
    maze: MazeGrid,
    reserved: set[Coordinate] | None = None,
) -> int:
    """Count all corridor cells with exactly one usable passage."""
    return sum(
        is_dead_end(maze, x, y, reserved)
        for y in range(maze.height)
        for x in range(maze.width)
    )


def count_real_dead_ends(maze: MazeGrid, reserved: set[Coordinate]) -> int:
    """Count dead ends not enclosed by the drawing, as in the analyzer."""
    return sum(
        is_real_dead_end(maze, (x, y), reserved)
        for y in range(maze.height) for x in range(maze.width)
    )


def is_real_dead_end(
    maze: MazeGrid, coordinate: Coordinate, reserved: set[Coordinate],
) -> bool:
    """Detect a dead end with a closed wall facing another corridor."""
    x, y = coordinate
    if not is_dead_end(maze, x, y, reserved):
        return False
    cell = maze.get_cell(x, y)
    return any(
        neighbor not in reserved and getattr(cell, direction)
        for direction, neighbor in maze.get_neighbors(x, y).items()
    )


def count_loops(maze: MazeGrid, reserved: set[Coordinate]) -> int:
    """Return E - V + 1 for a connected corridor graph."""
    edges = 0
    for y in range(maze.height):
        for x in range(maze.width):
            if (x, y) in reserved:
                continue
            cell = maze.get_cell(x, y)
            if x + 1 < maze.width and (x + 1, y) not in reserved:
                neighbor = maze.get_cell(x + 1, y)
                edges += int(not cell.east and not neighbor.west)
            if y + 1 < maze.height and (x, y + 1) not in reserved:
                neighbor = maze.get_cell(x, y + 1)
                edges += int(not cell.south and not neighbor.north)
    return edges - (maze.width * maze.height - len(reserved)) + 1
