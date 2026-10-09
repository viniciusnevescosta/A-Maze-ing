"""Test hexadecimal encoding of cell walls."""

import pytest

from mazegen.maze.cell import Cell
from mazegen.maze.encoding import cell_to_hex, row_to_hex


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
