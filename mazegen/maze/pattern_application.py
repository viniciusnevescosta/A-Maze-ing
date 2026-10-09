"""Apply the 42 pattern to a fully closed maze grid."""

from mazegen.maze.grid import MazeGrid
from mazegen.maze.pattern import PATTERN_42, get_pattern_origin

Coordinate = tuple[int, int]


def apply_pattern(maze: MazeGrid) -> set[Coordinate]:
    """Close pattern cells and return their reserved coordinates.

    Apply before generation, while every cell is fully closed.

    Raises:
        ValueError: If the pattern does not fit or passages already exist.
    """
    origin_x, origin_y = get_pattern_origin(maze.width, maze.height)

    for row in maze.grid:
        for cell in row:
            if not (cell.north and cell.east and cell.south and cell.west):
                raise ValueError("Apply the 42 pattern before generation")

    reserved: set[Coordinate] = set()

    for pattern_y, pattern_row in enumerate(PATTERN_42):
        for pattern_x, value in enumerate(pattern_row):
            if value == 0:
                continue

            x = origin_x + pattern_x
            y = origin_y + pattern_y
            cell = maze.get_cell(x, y)

            cell.north = True
            cell.east = True
            cell.south = True
            cell.west = True

            reserved.add((x, y))

    return reserved
