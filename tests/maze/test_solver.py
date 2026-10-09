"""Test shortest-path search and wall handling."""

import pytest

from mazegen.maze.generator import MazeGenerator
from mazegen.maze.grid import MazeGrid
from mazegen.maze.solver import solve_bfs


def test_bfs_solves_generated_maze() -> None:
    """Reach the exit through valid passages."""
    maze = MazeGenerator(5, 5, seed=42)
    maze.generate_perfect()

    path = solve_bfs(maze, (0, 0), (4, 4))

    assert path[0] == (0, 0)
    assert path[-1] == (4, 4)
    assert len(path) == len(set(path))

    opposite = {
        "north": "south",
        "east": "west",
        "south": "north",
        "west": "east",
    }

    for current, following in zip(path, path[1:]):
        neighbors = maze.get_neighbors(*current)
        assert following in neighbors.values()

        for direction, coordinate in neighbors.items():
            if coordinate == following:
                cell = maze.get_cell(*current)
                neighbor = maze.get_cell(*following)

                assert not getattr(cell, direction)
                assert not getattr(neighbor, opposite[direction])


def test_bfs_chooses_shortest_path_with_loop() -> None:
    """Choose the direct route instead of a longer alternative."""
    maze = MazeGrid(3, 2)

    maze.remove_wall(0, 0, 1, 0)
    maze.remove_wall(1, 0, 2, 0)

    maze.remove_wall(0, 0, 0, 1)
    maze.remove_wall(0, 1, 1, 1)
    maze.remove_wall(1, 1, 2, 1)
    maze.remove_wall(2, 1, 2, 0)

    assert solve_bfs(maze, (0, 0), (2, 0)) == [
        (0, 0),
        (1, 0),
        (2, 0),
    ]


def test_bfs_rejects_unreachable_exit() -> None:
    """Report an exit separated by closed walls."""
    maze = MazeGrid(2, 1)

    with pytest.raises(ValueError, match="unreachable"):
        solve_bfs(maze, (0, 0), (1, 0))


@pytest.mark.parametrize("open_side", ["east", "west"])
def test_bfs_requires_both_wall_sides_open(open_side: str) -> None:
    """Reject passages opened on only one side."""
    maze = MazeGrid(2, 1)

    if open_side == "east":
        maze.get_cell(0, 0).east = False
    else:
        maze.get_cell(1, 0).west = False

    with pytest.raises(ValueError, match="unreachable"):
        solve_bfs(maze, (0, 0), (1, 0))


@pytest.mark.parametrize(
    "entry, exit",
    [
        ((-1, 0), (1, 0)),
        ((0, 0), (2, 0)),
    ],
)
def test_bfs_rejects_invalid_coordinates(
    entry: tuple[int, int],
    exit: tuple[int, int],
) -> None:
    """Reject coordinates outside the grid."""
    maze = MazeGrid(2, 1)

    with pytest.raises(ValueError, match="outside maze bounds"):
        solve_bfs(maze, entry, exit)


def test_bfs_handles_same_entry_and_exit() -> None:
    """Return a zero-step path when both coordinates are equal."""
    maze = MazeGrid(1, 1)

    assert solve_bfs(maze, (0, 0), (0, 0)) == [(0, 0)]
