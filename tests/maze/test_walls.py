import pytest

from mazegen.maze.generator import MazeGenerator


def assert_walls_are_coherent(maze: MazeGenerator) -> None:
    """Check that every shared wall has the same state on both sides."""
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.get_cell(x, y)

            if x + 1 < maze.width:
                east_neighbor = maze.get_cell(x + 1, y)

                assert cell.east == east_neighbor.west, (
                    f"Incoherent East/West wall at ({x}, {y})"
                )

            if y + 1 < maze.height:
                south_neighbor = maze.get_cell(x, y + 1)

                assert cell.south == south_neighbor.north, (
                    f"Incoherent South/North wall at ({x}, {y})"
                )


def test_initial_walls_are_coherent() -> None:
    """Verify initial walls are coherent."""
    maze = MazeGenerator(width=3, height=3)

    assert_walls_are_coherent(maze)


def test_remove_wall_opens_east_and_west() -> None:
    """Verify remove wall opens east and west."""
    maze = MazeGenerator(width=2, height=1)

    maze.remove_wall(0, 0, 1, 0)

    assert maze.get_cell(0, 0).east is False
    assert maze.get_cell(1, 0).west is False
    assert_walls_are_coherent(maze)


def test_remove_wall_opens_west_and_east() -> None:
    """Verify remove wall opens west and east."""
    maze = MazeGenerator(width=2, height=1)

    maze.remove_wall(1, 0, 0, 0)

    assert maze.get_cell(1, 0).west is False
    assert maze.get_cell(0, 0).east is False
    assert_walls_are_coherent(maze)


def test_remove_wall_opens_south_and_north() -> None:
    """Verify remove wall opens south and north."""
    maze = MazeGenerator(width=1, height=2)

    maze.remove_wall(0, 0, 0, 1)

    assert maze.get_cell(0, 0).south is False
    assert maze.get_cell(0, 1).north is False
    assert_walls_are_coherent(maze)


def test_remove_wall_opens_north_and_south() -> None:
    """Verify remove wall opens north and south."""
    maze = MazeGenerator(width=1, height=2)

    maze.remove_wall(0, 1, 0, 0)

    assert maze.get_cell(0, 1).north is False
    assert maze.get_cell(0, 0).south is False
    assert_walls_are_coherent(maze)


def test_coherence_check_detects_one_sided_horizontal_change() -> None:
    """Verify coherence check detects one sided horizontal change."""
    maze = MazeGenerator(width=2, height=1)
    maze.get_cell(0, 0).east = False

    with pytest.raises(AssertionError, match="East/West"):
        assert_walls_are_coherent(maze)


def test_coherence_check_detects_one_sided_vertical_change() -> None:
    """Verify coherence check detects one sided vertical change."""
    maze = MazeGenerator(width=1, height=2)
    maze.get_cell(0, 0).south = False

    with pytest.raises(AssertionError, match="South/North"):
        assert_walls_are_coherent(maze)
