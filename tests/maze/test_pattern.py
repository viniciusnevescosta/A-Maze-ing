"""Test positioning of the 42 pattern."""

import pytest

from mazegen.maze.pattern import PATTERN_42, get_pattern_origin


@pytest.mark.parametrize(
    "width, height, expected",
    [
        (7, 5, (0, 0)),
        (9, 7, (1, 1)),
        (10, 8, (1, 1)),
        (20, 15, (6, 5)),
    ],
)
def test_pattern_origin(
    width: int,
    height: int,
    expected: tuple[int, int],
) -> None:
    """Center the pattern with any extra space on the right or bottom."""
    assert get_pattern_origin(width, height) == expected


@pytest.mark.parametrize(
    "width, height",
    [
        (7, 5),
        (8, 6),
        (20, 15),
        (31, 24),
    ],
)
def test_centered_pattern_stays_inside_grid(
    width: int,
    height: int,
) -> None:
    """Keep the entire pattern within bounds with balanced margins."""
    origin_x, origin_y = get_pattern_origin(width, height)
    pattern_width = len(PATTERN_42[0])
    pattern_height = len(PATTERN_42)

    right_margin = width - origin_x - pattern_width
    bottom_margin = height - origin_y - pattern_height

    assert origin_x >= 0
    assert origin_y >= 0
    assert right_margin >= 0
    assert bottom_margin >= 0
    assert right_margin - origin_x in (0, 1)
    assert bottom_margin - origin_y in (0, 1)


@pytest.mark.parametrize(
    "width, height",
    [
        (6, 5),
        (7, 4),
        (1, 1),
        (0, 0),
        (-1, 10),
    ],
)
def test_pattern_origin_rejects_small_grid(
    width: int,
    height: int,
) -> None:
    """Reject dimensions that cannot contain the pattern."""
    with pytest.raises(ValueError, match="too small"):
        get_pattern_origin(width, height)
