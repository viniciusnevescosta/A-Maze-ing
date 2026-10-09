"""Encode maze cell walls as hexadecimal digits."""

from mazegen.maze.cell import Cell


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
