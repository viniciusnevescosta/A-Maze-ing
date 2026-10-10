"""Exercise both generation modes, braiding and geometric constraints."""

from random import Random

import pytest

from mazegen.maze.areas import has_open_area, open_safe_passage
from mazegen.maze.braiding import add_loops
from mazegen.maze.encoding import maze_to_hex
from mazegen.maze.generator import MazeGenerator
from mazegen.maze.grid import MazeGrid
from mazegen.maze.topology import (
    count_dead_ends,
    count_loops,
    count_real_dead_ends,
)


@pytest.mark.parametrize("size", [(2, 3), (3, 2), (3, 3), (9, 7), (20, 15)])
@pytest.mark.parametrize("seed", [0, 1, 42, -5])
def test_playable_invariants(size: tuple[int, int], seed: int) -> None:
    """Generate connected, coherent boards with at least two loops."""
    maze = MazeGenerator(*size, seed=seed)
    maze.generate(perfect=False)
    maze.validate_non_perfect()
    assert count_loops(maze, maze.reserved) >= 2
    assert count_real_dead_ends(maze, maze.reserved) <= 2
    assert not has_open_area(maze)
    assert not maze.get_key_cells() & maze.reserved
    assert maze.solve((0, 0), (size[0] - 1, size[1] - 1))


@pytest.mark.parametrize("perfect", [True, False])
def test_same_seed_repeats_and_different_seeds_vary(perfect: bool) -> None:
    """Make the full pipeline deterministic without fixing every maze."""
    first = MazeGenerator(20, 15, seed=42)
    second = MazeGenerator(20, 15, seed=42)
    other = MazeGenerator(20, 15, seed=43)
    for maze in (first, second, other):
        maze.generate(perfect=perfect, entry=(6, 5), exit=(19, 14))
    assert maze_to_hex(first) == maze_to_hex(second)
    assert maze_to_hex(first) != maze_to_hex(other)
    assert (6, 5) not in first.reserved


def test_count_and_braiding_change_dead_ends() -> None:
    """Adding safe passages reduces dead ends while preserving connectivity."""
    maze = MazeGenerator(10, 10, seed=42)
    maze.generate_perfect()
    before = count_dead_ends(maze)
    add_loops(maze, set(), Random(42))
    assert count_dead_ends(maze) < before
    maze.validate_non_perfect()


def test_prevent_final_wall_of_open_3x3() -> None:
    """Reject the last opening of a forbidden block and restore both walls."""
    maze = MazeGrid(3, 3)
    for y in range(3):
        for x in range(3):
            if x < 2:
                maze.remove_wall(x, y, x + 1, y)
            if y < 2 and (x, y) != (1, 1):
                maze.remove_wall(x, y, x, y + 1)
    assert not has_open_area(maze)
    assert not open_safe_passage(maze, (1, 1), (1, 2), set())
    assert maze.get_cell(1, 1).south
    assert maze.get_cell(1, 2).north
    maze.remove_wall(1, 1, 1, 2)
    assert has_open_area(maze)


def test_permitted_2x3_and_reserved_cells() -> None:
    """Allow two-cell-wide regions without opening drawing cells."""
    maze = MazeGrid(2, 3)
    assert not open_safe_passage(maze, (0, 0), (1, 0), {(1, 0)})
    assert open_safe_passage(maze, (0, 0), (1, 0), set())
    assert not has_open_area(maze)


@pytest.mark.parametrize("size", [(1, 5), (5, 1), (2, 2)])
def test_impossible_playable_sizes_rejected(size: tuple[int, int]) -> None:
    """Reject boards that cannot have two independent cycles."""
    with pytest.raises(ValueError, match="at least"):
        MazeGenerator(*size).generate(perfect=False)


def test_dead_end_count_changes_with_passage() -> None:
    """Count endpoint changes when completing and reopening a loop."""
    maze = MazeGrid(2, 2)
    maze.remove_wall(0, 0, 1, 0)
    maze.remove_wall(1, 0, 1, 1)
    maze.remove_wall(1, 1, 0, 1)
    assert count_dead_ends(maze) == 2
    maze.remove_wall(0, 1, 0, 0)
    assert count_dead_ends(maze) == 0
    maze.get_cell(0, 1).north = True
    maze.get_cell(0, 0).south = True
    assert count_dead_ends(maze) == 2


def test_count_ignores_reservations() -> None:
    """Do not count isolated or reserved cells as common dead ends."""
    maze = MazeGrid(3, 1)
    assert count_dead_ends(maze) == 0
    maze.remove_wall(0, 0, 1, 0)
    maze.remove_wall(1, 0, 2, 0)
    assert count_dead_ends(maze, {(1, 0)}) == 0
