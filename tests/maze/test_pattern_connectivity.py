"""Test corridor connectivity while preserving the 42 pattern."""

import pytest

from mazegen.maze.generator import MazeGenerator
from mazegen.maze.pattern_application import apply_pattern
from mazegen.maze.solver import solve_bfs


@pytest.mark.parametrize("width, height", [(9, 7), (20, 15)])
@pytest.mark.parametrize("seed", [0, 42, -10])
def test_generation_preserves_connected_corridors(
    width: int, height: int, seed: int,
) -> None:
    """Connect every nonreserved cell without opening the drawing."""
    maze = MazeGenerator(width, height, seed=seed)
    maze.reserved = apply_pattern(maze)
    expected = {
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in maze.reserved
    }

    for _ in range(2):
        maze.generate_perfect()

        assert maze.visited == expected
        assert maze.get_reachable_cells() == expected
        assert len(maze.reserved) == 20
        for x, y in maze.reserved:
            cell = maze.get_cell(x, y)
            assert cell.north and cell.east and cell.south and cell.west

        edges = 0
        for row in maze.grid:
            for cell in row:
                edges += int(not cell.east) + int(not cell.south)
        assert edges == len(expected) - 1
        path = solve_bfs(maze, (0, 0), (width - 1, height - 1))
        assert not set(path) & maze.reserved


def test_validation_detects_isolated_corridor() -> None:
    """Do not mistake an accidentally isolated cell for part of 42."""
    maze = MazeGenerator(20, 15, seed=42)
    maze.reserved = apply_pattern(maze)
    maze.generate_perfect()
    cell = maze.get_cell(19, 14)
    cell.north = cell.east = cell.south = cell.west = True
    maze.get_cell(19, 13).south = True
    maze.get_cell(18, 14).east = True

    with pytest.raises(ValueError, match="not fully connected"):
        maze.validate_connectivity(reserved=maze.reserved)


def test_validation_detects_open_pattern_cell() -> None:
    """Reject an opened reserved cell even when corridors are connected."""
    maze = MazeGenerator(20, 15, seed=42)
    maze.reserved = apply_pattern(maze)
    maze.generate_perfect()
    x, y = next(iter(maze.reserved))
    maze.get_cell(x, y).north = False

    with pytest.raises(ValueError, match="Reserved pattern cell"):
        maze.validate_connectivity(reserved=maze.reserved)


def test_generation_rejects_disconnected_layout() -> None:
    """Reject a drawing that divides the available corridor positions."""
    maze = MazeGenerator(7, 5, seed=42)
    maze.reserved = apply_pattern(maze)

    with pytest.raises(ValueError, match="not fully connected"):
        maze.generate_perfect(1, 0)


def test_generation_rejects_reserved_start_before_reset() -> None:
    """Reject a reserved starting cell without resetting valid passages."""
    maze = MazeGenerator(20, 15, seed=42)
    maze.reserved = apply_pattern(maze)
    maze.generate_perfect()
    visited = set(maze.visited)
    x, y = next(iter(maze.reserved))

    with pytest.raises(ValueError, match="Starting cell belongs"):
        maze.generate_perfect(x, y)

    assert maze.visited == visited
    assert maze.get_reachable_cells() == visited


def test_generation_rejects_out_of_bounds_reservation() -> None:
    """Validate reserved coordinates before generation."""
    maze = MazeGenerator(2, 2)
    maze.reserved = {(2, 0)}

    with pytest.raises(ValueError, match="outside maze bounds"):
        maze.generate_perfect()
