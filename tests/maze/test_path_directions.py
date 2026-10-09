"""Test conversion of path coordinates into compass directions."""

import pytest

from mazegen.maze.solver import Coordinate, path_to_directions


@pytest.mark.parametrize(
    "path, expected",
    [
        ([(1, 1), (1, 0)], "N"),
        ([(1, 1), (2, 1)], "E"),
        ([(1, 1), (1, 2)], "S"),
        ([(1, 1), (0, 1)], "W"),
        ([(0, 0)], ""),
    ],
)
def test_path_to_directions(
    path: list[Coordinate],
    expected: str,
) -> None:
    """Convert each direction and a zero-step path correctly."""
    assert path_to_directions(path) == expected


def test_directions_reproduce_original_path() -> None:
    """Reconstruct every coordinate from the converted movements."""
    path: list[Coordinate] = [
        (0, 0),
        (1, 0),
        (2, 0),
        (2, 1),
        (1, 1),
        (1, 0),
    ]

    result = path_to_directions(path)

    assert result == "EESWN"
    assert len(result) == len(path) - 1

    offsets: dict[str, Coordinate] = {
        "N": (0, -1),
        "E": (1, 0),
        "S": (0, 1),
        "W": (-1, 0),
    }

    reconstructed: list[Coordinate] = [path[0]]
    x, y = path[0]

    for direction in result:
        delta_x, delta_y = offsets[direction]
        x += delta_x
        y += delta_y
        reconstructed.append((x, y))

    assert reconstructed == path


def test_empty_path_is_rejected() -> None:
    """Reject a path without an entry coordinate."""
    with pytest.raises(ValueError, match="must not be empty"):
        path_to_directions([])


@pytest.mark.parametrize(
    "path",
    [
        [(0, 0), (1, 1)],
        [(0, 0), (2, 0)],
        [(0, 0), (0, 0)],
    ],
)
def test_invalid_movement_is_rejected(
    path: list[Coordinate],
) -> None:
    """Reject diagonal, nonadjacent and stationary movements."""
    with pytest.raises(ValueError, match="Invalid path movement"):
        path_to_directions(path)
