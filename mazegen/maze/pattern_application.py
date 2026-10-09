"""Apply and safely position the 42 pattern."""

from mazegen.maze.grid import MazeGrid
from mazegen.maze.pattern import (
    PATTERN_42,
    can_fit_pattern,
    get_pattern_origin,
)

Coordinate = tuple[int, int]


def get_pattern_cells(origin: Coordinate) -> set[Coordinate]:
    """Return drawing coordinates translated from a top-left origin."""
    origin_x, origin_y = origin
    cells: set[Coordinate] = set()

    for pattern_y, pattern_row in enumerate(PATTERN_42):
        for pattern_x, value in enumerate(pattern_row):
            if value == 1:
                cells.add((origin_x + pattern_x, origin_y + pattern_y))

    return cells


def apply_pattern(maze: MazeGrid) -> set[Coordinate]:
    """Close the centered pattern cells before generation.

    Raises:
        ValueError: If the pattern does not fit or passages already exist.
    """
    origin = get_pattern_origin(maze.width, maze.height)

    for row in maze.grid:
        for cell in row:
            if not (cell.north and cell.east and cell.south and cell.west):
                raise ValueError("Apply the 42 pattern before generation")

    reserved = get_pattern_cells(origin)

    for x, y in reserved:
        cell = maze.get_cell(x, y)
        cell.north = True
        cell.east = True
        cell.south = True
        cell.west = True

    return reserved


def corridors_can_connect(
    maze: MazeGrid,
    entry: Coordinate,
    reserved: set[Coordinate],
) -> bool:
    """Check geometric connectivity, ignoring current cell walls."""
    if entry in reserved:
        return False

    reachable: set[Coordinate] = {entry}
    stack: list[Coordinate] = [entry]

    while stack:
        x, y = stack.pop()

        for coordinate in maze.get_neighbors(x, y).values():
            if coordinate in reserved or coordinate in reachable:
                continue

            reachable.add(coordinate)
            stack.append(coordinate)

    return len(reachable) == maze.width * maze.height - len(reserved)


def choose_pattern_cells(
    maze: MazeGrid,
    entry: Coordinate,
    exit: Coordinate,
) -> set[Coordinate]:
    """Choose safe reservations nearest the center, or return an empty set.

    Prefer topmost, then leftmost origins when distances are equal.
    This function does not modify cells or consider existing passages.

    Raises:
        ValueError: If entry or exit is outside the maze.
    """
    maze.get_cell(*entry)
    maze.get_cell(*exit)

    if not can_fit_pattern(maze.width, maze.height):
        return set()

    pattern_width = len(PATTERN_42[0])
    pattern_height = len(PATTERN_42)
    remaining_x = maze.width - pattern_width
    remaining_y = maze.height - pattern_height

    candidates: list[tuple[int, int, int]] = []

    for origin_y in range(remaining_y + 1):
        for origin_x in range(remaining_x + 1):
            distance = abs(2 * origin_x - remaining_x) + abs(
                2 * origin_y - remaining_y
            )
            candidates.append((distance, origin_y, origin_x))

    candidates.sort()

    for _, origin_y, origin_x in candidates:
        reserved = get_pattern_cells((origin_x, origin_y))

        if entry in reserved or exit in reserved:
            continue

        if corridors_can_connect(maze, entry, reserved):
            return reserved

    return set()
