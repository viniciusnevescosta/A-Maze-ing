import pytest

from mazegen.maze.generator import MazeGenerator


@pytest.mark.parametrize(
    ("width", "height"),
    [(1, 1), (1, 5), (5, 1), (3, 3), (20, 15)],
)
@pytest.mark.parametrize("seed", [0, 42, -10])
def test_generated_maze_is_fully_connected(
    width: int,
    height: int,
    seed: int,
) -> None:
    """Verify every generated cell is reachable through open passages."""
    maze = MazeGenerator(width, height, seed)
    maze.generate_perfect()

    reachable = maze.get_reachable_cells()

    assert len(reachable) == width * height
    maze.validate_connectivity()


def test_detects_an_artificially_isolated_cell() -> None:
    """Verify closing both sides of a passage isolates a cell."""
    maze = MazeGenerator(3, 1, seed=42)
    maze.generate_perfect()

    maze.get_cell(1, 0).east = True
    maze.get_cell(2, 0).west = True

    assert maze.get_reachable_cells() == {(0, 0), (1, 0)}

    with pytest.raises(ValueError, match="not fully connected"):
        maze.validate_connectivity()


def test_one_sided_opening_is_not_a_passage() -> None:
    """Verify a passage requires both neighboring walls to be open."""
    maze = MazeGenerator(2, 1)
    maze.get_cell(0, 0).east = False

    assert maze.get_reachable_cells() == {(0, 0)}


def test_traversal_does_not_change_generation_visits() -> None:
    """Verify connectivity traversal uses its own exploration state."""
    maze = MazeGenerator(3, 1)
    maze.remove_wall(0, 0, 1, 0)

    reachable = maze.get_reachable_cells()

    assert reachable == {(0, 0), (1, 0)}
    assert maze.visited == set()


def test_traversal_accepts_a_different_start() -> None:
    """Verify traversal begins at the requested coordinates."""
    maze = MazeGenerator(3, 1)
    maze.remove_wall(1, 0, 2, 0)

    assert maze.get_reachable_cells(2, 0) == {(1, 0), (2, 0)}


@pytest.mark.parametrize(
    ("x", "y"),
    [(-1, 0), (0, -1), (3, 0), (0, 3)],
)
def test_traversal_rejects_invalid_start(x: int, y: int) -> None:
    """Verify out-of-bounds starting coordinates are rejected."""
    maze = MazeGenerator(3, 3)

    with pytest.raises(ValueError, match="outside maze bounds"):
        maze.get_reachable_cells(x, y)
