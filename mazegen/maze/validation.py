"""Read-only traversal and validation of maze walls and connectivity."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mazegen.maze.grid import Direction, MazeGrid


def validate_external_walls(maze: MazeGrid) -> None:
    """Check that every external wall is closed.

    Raises:
        ValueError: If an external wall is open.
    """
    for x in range(maze.width):
        top_cell = maze.get_cell(x, 0)
        bottom_cell = maze.get_cell(x, maze.height - 1)

        if not top_cell.north:
            raise ValueError(f"Open external North wall at ({x}, 0)")

        if not bottom_cell.south:
            raise ValueError(
                f"Open external South wall at ({x}, {maze.height - 1})"
            )

    for y in range(maze.height):
        left_cell = maze.get_cell(0, y)
        right_cell = maze.get_cell(maze.width - 1, y)

        if not left_cell.west:
            raise ValueError(f"Open external West wall at (0, {y})")

        if not right_cell.east:
            raise ValueError(
                f"Open external East wall at ({maze.width - 1}, {y})"
            )


def get_reachable_cells(
    maze: MazeGrid,
    start_x: int = 0,
    start_y: int = 0,
) -> set[tuple[int, int]]:
    """Return cells reachable through passages open on both sides.

    Raises:
        ValueError: If the starting coordinates are invalid.
    """
    maze.get_cell(start_x, start_y)

    reachable: set[tuple[int, int]] = {(start_x, start_y)}
    stack: list[tuple[int, int]] = [(start_x, start_y)]

    opposite: dict[Direction, Direction] = {
        "north": "south",
        "east": "west",
        "south": "north",
        "west": "east",
    }

    while stack:
        x, y = stack.pop()
        cell = maze.get_cell(x, y)
        neighbors = maze.get_neighbors(x, y)

        for direction, coordinate in neighbors.items():
            neighbor_x, neighbor_y = coordinate
            neighbor = maze.get_cell(neighbor_x, neighbor_y)

            if getattr(cell, direction):
                continue

            if getattr(neighbor, opposite[direction]):
                continue

            if coordinate not in reachable:
                reachable.add(coordinate)
                stack.append(coordinate)

    return reachable


def validate_connectivity(
    maze: MazeGrid,
    start_x: int = 0,
    start_y: int = 0,
    reserved: set[tuple[int, int]] | None = None,
) -> None:
    """Check corridor connectivity and fully closed reserved cells.

    Raises:
        ValueError: If reservations are invalid or corridors are disconnected.
    """
    blocked = set() if reserved is None else set(reserved)

    for x, y in blocked:
        cell = maze.get_cell(x, y)

        if not (cell.north and cell.east and cell.south and cell.west):
            raise ValueError(
                f"Reserved pattern cell has an open wall: ({x}, {y})"
            )

    maze.get_cell(start_x, start_y)

    if (start_x, start_y) in blocked:
        raise ValueError("Starting cell belongs to the 42 pattern")

    expected: set[tuple[int, int]] = set()

    for y in range(maze.height):
        for x in range(maze.width):
            if (x, y) not in blocked:
                expected.add((x, y))

    reachable = maze.get_reachable_cells(start_x, start_y)

    if reachable != expected:
        raise ValueError(
            "Maze corridors are not fully connected: "
            f"{len(reachable)} of {len(expected)} cells are reachable"
        )
