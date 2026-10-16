"""Independently check generated output against the mandatory scale."""

from collections import deque
from pathlib import Path

import pytest

from mazegen.cli import main

Coordinate = tuple[int, int]

# dx, dy, local closed-wall bit, neighbour's opposite wall bit.
SIDES = ((0, -1, 1, 4), (1, 0, 2, 8), (0, 1, 4, 1), (-1, 0, 8, 2))


def check_output(path: Path, width: int, height: int, perfect: bool) -> None:
    """Validate the on-disk format and graph without using maze classes."""
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == height + 4
    assert lines[height] == ""
    assert all(len(line) == width for line in lines[:height])
    assert all(set(line) <= set("0123456789ABCDEF") for line in lines[:height])
    grid = [[int(digit, 16) for digit in line] for line in lines[:height]]
    entry_x, entry_y = lines[height + 1].split(",")
    exit_x, exit_y = lines[height + 2].split(",")
    entry: Coordinate = (int(entry_x), int(entry_y))
    exit_cell: Coordinate = (int(exit_x), int(exit_y))
    assert entry == (0, 0) and exit_cell == (width - 1, height - 1)

    def neighbors(cell: Coordinate) -> list[Coordinate]:
        x, y = cell
        passages: list[Coordinate] = []
        for dx, dy, bit, opposite in SIDES:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                assert grid[y][x] & bit
                continue
            assert bool(grid[y][x] & bit) == bool(grid[ny][nx] & opposite)
            if not (grid[y][x] & bit):
                passages.append((nx, ny))
        return passages

    cells = {(x, y) for y in range(height) for x in range(width)}
    closed = {cell for cell in cells if grid[cell[1]][cell[0]] == 15}
    graph: dict[Coordinate, list[Coordinate]] = {
        cell: neighbors(cell) for cell in cells
    }
    reachable = {entry}
    queue = deque([entry])
    distances = {entry: 0}
    while queue:
        cell = queue.popleft()
        for neighbor in graph[cell]:
            if neighbor not in reachable:
                reachable.add(neighbor)
                distances[neighbor] = distances[cell] + 1
                queue.append(neighbor)
    assert reachable == cells - closed
    assert exit_cell in reachable
    edges = sum(len(graph[cell]) for cell in reachable) // 2
    loops = edges - len(reachable) + 1
    if perfect:
        assert loops == 0
    else:
        assert loops >= 2

    directions = {"N": (0, -1), "E": (1, 0),
                  "S": (0, 1), "W": (-1, 0)}
    path = lines[-1]
    assert set(path) <= set(directions)
    point = entry
    for move in path:
        dx, dy = directions[move]
        following = (point[0] + dx, point[1] + dy)
        assert following in graph[point]
        point = following
    assert point == exit_cell
    assert len(path) == distances[exit_cell]

    for y in range(height - 2):
        for x in range(width - 2):
            internal = [(x + dx, y + dy) for dy in range(3)
                        for dx in range(3)]
            assert any(
                neighbor not in graph[cell]
                for cell in internal
                for neighbor in ((cell[0] + 1, cell[1]),
                                 (cell[0], cell[1] + 1))
                if neighbor[0] <= x + 2 and neighbor[1] <= y + 2
            ), "A completely open 3x3 region is forbidden"

    if not perfect:
        assert {(0, 0), (width - 1, 0),
                (0, height - 1), (width - 1, height - 1),
                (width // 2, height // 2)} <= reachable

        def is_real_dead_end(cell: Coordinate) -> bool:
            if len(graph[cell]) != 1:
                return False
            x, y = cell
            for dx, dy, bit, _ in SIDES:
                nx, ny = x + dx, y + dy
                if (0 <= nx < width and 0 <= ny < height
                        and grid[y][x] & bit and (nx, ny) not in closed):
                    return True
            return False

        real_dead_ends = sum(is_real_dead_end(cell) for cell in reachable)
        assert real_dead_ends <= 2


@pytest.mark.parametrize("perfect", [True, False])
@pytest.mark.parametrize("seed", [0, 42, 1337])
def test_both_modes_pass_independent_scale_check(
    tmp_path: Path, perfect: bool, seed: int,
) -> None:
    """Exercise the real CLI and independently inspect its exported file."""
    maze_file = tmp_path / "maze.txt"
    config_file = tmp_path / "config.txt"
    config_file.write_text(
        "WIDTH=20\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n"
        f"OUTPUT_FILE={maze_file}\nPERFECT={perfect}\nSEED={seed}\n",
        encoding="utf-8",
    )
    assert main([str(config_file)]) == 0
    check_output(maze_file, 20, 15, perfect)
