"""Encode maze cell walls as hexadecimal digits."""

from mazegen.maze.cell import Cell
from mazegen.maze.grid import MazeGrid


def cell_to_hex(cell: Cell) -> str:
    """Return one uppercase hexadecimal digit representing cell walls."""
    value = 0

    if cell.north:
        value |= 1 << 0

    if cell.east:
        value |= 1 << 1

    if cell.south:
        value |= 1 << 2

    if cell.west:
        value |= 1 << 3

    return format(value, "X")


def row_to_hex(row: list[Cell]) -> str:
    """Encode a row as one hexadecimal digit per cell."""
    digits: list[str] = []

    for cell in row:
        digits.append(cell_to_hex(cell))

    return "".join(digits)


def maze_to_hex(maze: MazeGrid) -> list[str]:
    """Encode the maze as hexadecimal rows in grid order."""
    rows: list[str] = []

    for row in maze.grid:
        rows.append(row_to_hex(row))

    return rows
