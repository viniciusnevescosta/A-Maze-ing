"""Define the 42 pattern independently of maze coordinates."""

PATTERN_42: tuple[tuple[int, ...], ...] = (
    (1, 0, 1, 0, 1, 1, 1),
    (1, 0, 1, 0, 0, 0, 1),
    (1, 1, 1, 0, 1, 1, 1),
    (0, 0, 1, 0, 1, 0, 0),
    (0, 0, 1, 0, 1, 1, 1),
)


def get_pattern_origin(width: int, height: int) -> tuple[int, int]:
    """Return the top-left coordinates of the centered 42 pattern.

    Raises:
        ValueError: If the maze is too small to contain the pattern.
    """
    pattern_height = len(PATTERN_42)
    pattern_width = len(PATTERN_42[0])

    if width < pattern_width or height < pattern_height:
        raise ValueError("Maze is too small to contain the 42 pattern")

    origin_x = (width - pattern_width) // 2
    origin_y = (height - pattern_height) // 2

    return origin_x, origin_y
