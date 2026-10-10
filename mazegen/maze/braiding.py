"""Add safe loops to a generated tree for the non-perfect mode."""

from random import Random

from mazegen.maze.areas import open_safe_passage
from mazegen.maze.grid import MazeGrid
from mazegen.maze.topology import (
    count_loops,
    count_real_dead_ends,
    is_dead_end,
    is_real_dead_end,
)

Coordinate = tuple[int, int]


def add_loops(
    maze: MazeGrid, reserved: set[Coordinate], random: Random,
) -> None:
    """Reduce real dead ends to at most two and create at least two cycles."""
    cells = [
        (x, y) for y in range(maze.height) for x in range(maze.width)
        if (x, y) not in reserved
    ]
    random.shuffle(cells)
    remaining = count_real_dead_ends(maze, reserved)
    for x, y in cells:
        if remaining <= 2:
            break
        if not is_dead_end(maze, x, y, reserved):
            continue
        neighbors = list(maze.get_neighbors(x, y).values())
        random.shuffle(neighbors)
        for neighbor in neighbors:
            before = int(is_real_dead_end(maze, (x, y), reserved))
            before += int(is_real_dead_end(maze, neighbor, reserved))
            if open_safe_passage(maze, (x, y), neighbor, reserved):
                after = int(is_real_dead_end(maze, (x, y), reserved))
                after += int(is_real_dead_end(maze, neighbor, reserved))
                remaining -= before - after
                break

    if count_loops(maze, reserved) < 2:
        for x, y in cells:
            neighbors = list(maze.get_neighbors(x, y).values())
            random.shuffle(neighbors)
            for neighbor in neighbors:
                open_safe_passage(maze, (x, y), neighbor, reserved)
                if count_loops(maze, reserved) >= 2:
                    return
