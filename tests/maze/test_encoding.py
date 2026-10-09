"""Test hexadecimal encoding of cell walls."""

import pytest

from mazegen.maze.cell import Cell
from mazegen.maze.encoding import cell_to_hex, maze_to_hex, row_to_hex
from mazegen.maze.grid import MazeGrid


@pytest.mark.parametrize(
    "north, east, south, west, expected",
    [
        (False, False, False, False, "0"),
        (True, False, False, False, "1"),
        (False, True, False, False, "2"),
        (True, True, False, False, "3"),
        (False, False, True, False, "4"),
        (True, False, True, False, "5"),
        (False, True, True, False, "6"),
        (True, True, True, False, "7"),
        (False, False, False, True, "8"),
        (True, False, False, True, "9"),
        (False, True, False, True, "A"),
        (True, True, False, True, "B"),
        (False, False, True, True, "C"),
        (True, False, True, True, "D"),
        (False, True, True, True, "E"),
        (True, True, True, True, "F"),
    ],
)
def test_cell_to_hex(
    north: bool,
    east: bool,
    south: bool,
    west: bool,
    expected: str,
) -> None:
    """Encode every combination using the required bit positions."""
    cell = Cell(
        north=north,
        east=east,
        south=south,
        west=west,
    )

    result = cell_to_hex(cell)

    assert result == expected
    assert len(result) == 1
    assert result in "0123456789ABCDEF"
    assert (cell.north, cell.east, cell.south, cell.west) == (
        north,
        east,
        south,
        west,
    )


def test_new_cell_encodes_as_f() -> None:
    """Encode a fully closed default cell as F."""
    assert cell_to_hex(Cell()) == "F"


def test_row_to_hex_preserves_order() -> None:
    """Encode cells in their original left-to-right order."""
    row = [
        Cell(north=True, east=False, south=False, west=True),
        Cell(north=False, east=True, south=False, west=True),
        Cell(north=True, east=False, south=True, west=False),
    ]

    result = row_to_hex(row)

    assert result == "9A5"
    assert len(result) == len(row)


@pytest.mark.parametrize("width", [0, 1, 3, 20])
def test_row_to_hex_matches_row_width(width: int) -> None:
    """Produce exactly one digit per cell for different row sizes."""
    row: list[Cell] = []

    for _ in range(width):
        row.append(Cell())

    assert row_to_hex(row) == "F" * width


def test_row_to_hex_uses_cell_encoding() -> None:
    """Apply the individual cell encoding to every row position."""
    row = [
        Cell(),
        Cell(north=False, east=False, south=False, west=False),
        Cell(north=True, east=True, south=False, west=False),
    ]

    result = row_to_hex(row)

    assert len(result) == len(row)

    for cell, digit in zip(row, result):
        assert digit == cell_to_hex(cell)


@pytest.mark.parametrize(
    "width, height",
    [
        (1, 1),
        (5, 1),
        (1, 5),
        (3, 2),
        (20, 15),
    ],
)
def test_maze_to_hex_dimensions(width: int, height: int) -> None:
    """Produce height rows with width hexadecimal digits each."""
    maze = MazeGrid(width, height)

    result = maze_to_hex(maze)

    assert len(result) == height

    for row in result:
        assert len(row) == width
        assert row == "F" * width


def test_maze_to_hex_preserves_grid_order() -> None:
    """Preserve top-to-bottom rows and left-to-right cells."""
    maze = MazeGrid(3, 2)
    maze.grid = [
        [
            Cell(north=True, east=False, south=False, west=True),
            Cell(north=False, east=True, south=False, west=True),
            Cell(north=True, east=False, south=True, west=False),
        ],
        [
            Cell(),
            Cell(north=False, east=False, south=False, west=False),
            Cell(north=True, east=True, south=False, west=False),
        ],
    ]

    assert maze_to_hex(maze) == ["9A5", "F03"]


def test_maze_to_hex_uses_row_encoding() -> None:
    """Apply the existing row encoder to every grid row."""
    maze = MazeGrid(2, 2)
    maze.remove_wall(0, 0, 1, 0)
    maze.remove_wall(1, 0, 1, 1)

    result = maze_to_hex(maze)

    for index, row in enumerate(maze.grid):
        assert result[index] == row_to_hex(row)
