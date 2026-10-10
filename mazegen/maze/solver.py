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


def path_to_directions(path: list[Coordinate]) -> str:
    """Convert adjacent path coordinates into N/E/S/W movements.

    Raises:
        ValueError: If the path is empty or a movement is invalid.
    """
    if not path:
        raise ValueError("Path must not be empty")

    directions: dict[Coordinate, str] = {
        (0, -1): "N",
        (1, 0): "E",
        (0, 1): "S",
        (-1, 0): "W",
    }

    movements: list[str] = []

    for current, following in zip(path, path[1:]):
        current_x, current_y = current
        following_x, following_y = following

        delta = (
            following_x - current_x,
            following_y - current_y,
        )

        if delta not in directions:
            raise ValueError(
                f"Invalid path movement: {current} -> {following}"
            )

        movements.append(directions[delta])

    return "".join(movements)


def validate_solution(
    maze: MazeGrid,
    path: list[Coordinate],
    entry: Coordinate,
    exit: Coordinate,
) -> None:
    """Reject solutions with wrong endpoints, blocked steps or extra length."""
    if not path or path[0] != entry or path[-1] != exit:
        raise ValueError("Solution must start at ENTRY and end at EXIT")
    path_to_directions(path)
    opposite = {"north": "south", "east": "west",
                "south": "north", "west": "east"}
    for source, target in zip(path, path[1:]):
        cell = maze.get_cell(*source)
        neighbor = maze.get_cell(*target)
        for direction, coordinate in maze.get_neighbors(*source).items():
            if coordinate == target:
                if getattr(cell, direction) or getattr(
                    neighbor, opposite[direction]
                ):
                    raise ValueError("Solution crosses a closed wall")
    if len(path) != len(solve_bfs(maze, entry, exit)):
        raise ValueError("Solution is not a shortest path")
