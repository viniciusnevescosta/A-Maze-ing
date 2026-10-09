import pytest

from mazegen.maze.generator import MazeGenerator


@pytest.mark.parametrize(
    ("width", "height"),
    [
        (1, 1),
        (1, 3),
        (3, 1),
        (3, 3),
        (5, 4),
    ],
)
def test_initial_external_walls_are_closed(
    width: int,
    height: int,
) -> None:
    maze = MazeGenerator(width, height)

    maze.validate_external_walls()


def test_opening_internal_passages_preserves_external_walls() -> None:
    maze = MazeGenerator(3, 3)

    for y in range(maze.height):
        for x in range(maze.width):
            neighbors = maze.get_neighbors(x, y)

            for neighbor_x, neighbor_y in neighbors.values():
                maze.remove_wall(x, y, neighbor_x, neighbor_y)

    maze.validate_external_walls()


@pytest.mark.parametrize("x", [0, 1, 2])
def test_detects_open_external_north_wall(x: int) -> None:
    maze = MazeGenerator(3, 3)
    maze.get_cell(x, 0).north = False

    with pytest.raises(ValueError, match="North"):
        maze.validate_external_walls()


@pytest.mark.parametrize("x", [0, 1, 2])
def test_detects_open_external_south_wall(x: int) -> None:
    maze = MazeGenerator(3, 3)
    maze.get_cell(x, 2).south = False

    with pytest.raises(ValueError, match="South"):
        maze.validate_external_walls()


@pytest.mark.parametrize("y", [0, 1, 2])
def test_detects_open_external_west_wall(y: int) -> None:
    maze = MazeGenerator(3, 3)
    maze.get_cell(0, y).west = False

    with pytest.raises(ValueError, match="West"):
        maze.validate_external_walls()


@pytest.mark.parametrize("y", [0, 1, 2])
def test_detects_open_external_east_wall(y: int) -> None:
    maze = MazeGenerator(3, 3)
    maze.get_cell(2, y).east = False

    with pytest.raises(ValueError, match="East"):
        maze.validate_external_walls()
