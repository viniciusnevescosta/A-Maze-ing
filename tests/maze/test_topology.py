"""Test identification of cells with exactly one usable passage."""

import pytest

from mazegen.maze.grid import MazeGrid
from mazegen.maze.topology import is_dead_end


@pytest.mark.parametrize(
    "neighbor",
    [(1, 0), (2, 1), (1, 2), (0, 1)],
)
def test_one_passage_is_dead_end(
    neighbor: tuple[int, int],
) -> None:
    """Identify one passage in any of the four directions."""
    maze = MazeGrid(3, 3)
    maze.remove_wall(1, 1, *neighbor)

    assert is_dead_end(maze, 1, 1) is True


@pytest.mark.parametrize("passage_count", [0, 2, 3, 4])
def test_other_passage_counts_are_not_dead_ends(
    passage_count: int,
) -> None:
    """Reject isolated cells and cells with multiple exits."""
    maze = MazeGrid(3, 3)
    neighbors = [(1, 0), (2, 1), (1, 2), (0, 1)]

    for neighbor in neighbors[:passage_count]:
        maze.remove_wall(1, 1, *neighbor)

    assert is_dead_end(maze, 1, 1) is False


def test_reserved_cell_is_not_dead_end() -> None:
    """Never classify a reserved cell as a common dead end."""
    maze = MazeGrid(2, 1)
    maze.remove_wall(0, 0, 1, 0)

    assert is_dead_end(maze, 0, 0, reserved={(0, 0)}) is False


def test_passage_to_reserved_cell_is_not_usable() -> None:
    """Ignore passages leading into the reserved drawing."""
    maze = MazeGrid(2, 1)
    maze.remove_wall(0, 0, 1, 0)

    assert is_dead_end(maze, 0, 0, reserved={(1, 0)}) is False


@pytest.mark.parametrize("open_side", ["east", "west"])
def test_one_sided_opening_is_not_usable(open_side: str) -> None:
    """Require both sides of a shared wall to be open."""
    maze = MazeGrid(2, 1)

    if open_side == "east":
        maze.get_cell(0, 0).east = False
    else:
        maze.get_cell(1, 0).west = False

    assert is_dead_end(maze, 0, 0) is False


def test_external_opening_is_not_a_passage() -> None:
    """Do not count an opening that leads outside the grid."""
    maze = MazeGrid(1, 1)
    maze.get_cell(0, 0).north = False

    assert is_dead_end(maze, 0, 0) is False


def test_corner_with_one_passage_is_dead_end() -> None:
    """Identify a dead end at a grid corner."""
    maze = MazeGrid(2, 2)
    maze.remove_wall(0, 0, 1, 0)

    assert is_dead_end(maze, 0, 0) is True


def test_invalid_coordinate_is_rejected() -> None:
    """Reject coordinates outside the maze."""
    maze = MazeGrid(2, 2)

    with pytest.raises(ValueError, match="outside maze bounds"):
        is_dead_end(maze, -1, 0)
