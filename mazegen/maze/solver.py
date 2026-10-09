"""Find shortest paths through a maze using BFS."""

from collections import deque

from mazegen.maze.grid import Direction, MazeGrid

Coordinate = tuple[int, int]


def solve_bfs(
    maze: MazeGrid,
    entry: Coordinate,
    exit: Coordinate,
) -> list[Coordinate]:
    """Return the shortest path, including entry and exit.

    Raises:
        ValueError: If coordinates are invalid or exit is unreachable.
    """
    maze.get_cell(*entry)
    maze.get_cell(*exit)

    queue: deque[Coordinate] = deque([entry])
    visited: set[Coordinate] = {entry}
    predecessor: dict[Coordinate, Coordinate] = {}

    opposite: dict[Direction, Direction] = {
        "north": "south",
        "east": "west",
        "south": "north",
        "west": "east",
    }

    while queue:
        current = queue.popleft()

        if current == exit:
            path: list[Coordinate] = [current]

            while current != entry:
                current = predecessor[current]
                path.append(current)

            path.reverse()
            return path

        x, y = current
        cell = maze.get_cell(x, y)

        for direction, coordinate in maze.get_neighbors(x, y).items():
            if coordinate in visited:
                continue

            neighbor = maze.get_cell(*coordinate)

            if getattr(cell, direction):
                continue

            if getattr(neighbor, opposite[direction]):
                continue

            visited.add(coordinate)
            predecessor[coordinate] = current
            queue.append(coordinate)

    raise ValueError("Exit is unreachable from entry")
