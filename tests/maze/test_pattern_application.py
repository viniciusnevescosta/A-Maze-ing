"""Test reservation of fully closed cells forming 42."""

import pytest

from mazegen.maze.grid import MazeGrid
from mazegen.maze.pattern import PATTERN_42, get_pattern_origin
from mazegen.maze.pattern_application import apply_pattern


def test_apply_pattern_reserves_exact_drawing() -> None:
    """Reserve only marked positions translated to the maze center."""
    maze = MazeGrid(20, 15)
    origin_x, origin_y = get_pattern_origin(maze.width, maze.height)

    expected: set[tuple[int, int]] = set()

    for y, row in enumerate(PATTERN_42):
        for x, value in enumerate(row):
            if value == 1:
                expected.add((origin_x + x, origin_y + y))

    reserved = apply_pattern(maze)

    assert reserved == expected
    assert len(reserved) == 20

    for x, y in reserved:
        cell = maze.get_cell(x, y)
        assert cell.north and cell.east and cell.south and cell.west


def test_apply_pattern_preserves_existing_cells() -> None:
    """Preserve cell identity and walls, including outside the pattern."""
    maze = MazeGrid(9, 7)
    original_cells = [[cell for cell in row] for row in maze.grid]

    apply_pattern(maze)

    for y, row in enumerate(maze.grid):
        for x, cell in enumerate(row):
            assert cell is original_cells[y][x]
            assert cell.north and cell.east and cell.south and cell.west


def test_apply_pattern_rejects_open_grid_without_modification() -> None:
    """Reject an opened grid without changing its existing passage."""
    maze = MazeGrid(9, 7)
    maze.remove_wall(0, 0, 1, 0)

    with pytest.raises(ValueError, match="before generation"):
        apply_pattern(maze)

    assert maze.get_cell(0, 0).east is False
    assert maze.get_cell(1, 0).west is False


def test_apply_pattern_rejects_small_grid() -> None:
    """Reject dimensions too small for the drawing."""
    maze = MazeGrid(6, 5)

    with pytest.raises(ValueError, match="too small"):
        apply_pattern(maze)
