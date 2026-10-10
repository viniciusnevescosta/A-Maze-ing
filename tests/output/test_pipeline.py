"""Verify exported walls, footer and shortest path independently."""

from collections import deque
from pathlib import Path
from unittest.mock import patch

import pytest

from mazegen.cli import main
from mazegen.maze.grid import MazeGrid
from mazegen.maze.solver import validate_solution
from mazegen.output.writer import write_maze


@pytest.mark.parametrize("perfect", [True, False])
def test_exported_solution_is_shortest(tmp_path: Path, perfect: bool) -> None:
    """Decode the actual file and run an independent BFS over wall bits."""
    output = tmp_path / "maze.txt"
    config = tmp_path / "config.txt"
    config.write_text(
        "WIDTH=20\nHEIGHT=15\nENTRY=6,5\nEXIT=19,14\n"
        f"OUTPUT_FILE={output}\nPERFECT={perfect}\nSEED=42\n",
        encoding="utf-8",
    )
    assert main([str(config)]) == 0
    raw = output.read_bytes()
    assert raw.endswith(b"\n") and b"\r" not in raw
    lines = raw.decode().splitlines()
    assert len(lines) == 19 and lines[15:18] == ["", "6,5", "19,14"]
    grid = [[int(digit, 16) for digit in row] for row in lines[:15]]
    assert all(len(row) == 20 for row in grid)
    offsets = {"N": (0, -1, 1, 4), "E": (1, 0, 2, 8),
               "S": (0, 1, 4, 1), "W": (-1, 0, 8, 2)}
    queue: deque[tuple[int, int, int]] = deque([(6, 5, 0)])
    seen = {(6, 5)}
    distance = -1
    while queue:
        x, y, steps = queue.popleft()
        if (x, y) == (19, 14):
            distance = steps
            break
        for dx, dy, bit, opposite in offsets.values():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < 20 and 0 <= ny < 15):
                continue
            if grid[y][x] & bit or grid[ny][nx] & opposite:
                continue
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                queue.append((nx, ny, steps + 1))
    x, y = 6, 5
    for letter in lines[18]:
        dx, dy, bit, opposite = offsets[letter]
        nx, ny = x + dx, y + dy
        assert 0 <= nx < 20 and 0 <= ny < 15
        assert not grid[y][x] & bit and not grid[ny][nx] & opposite
        x, y = nx, ny
    assert (x, y) == (19, 14)
    assert len(lines[18]) == distance


def test_write_failure_preserves_existing_output(tmp_path: Path) -> None:
    """Failed publication preserves the previous file and removes temp data."""
    output = tmp_path / "maze.txt"
    output.write_text("original\n", encoding="utf-8")
    with patch(
        "mazegen.output.writer.os.replace", side_effect=OSError("full"),
    ):
        with pytest.raises(OSError, match="full"):
            write_maze(MazeGrid(1, 1), str(output), (0, 0), (0, 0), "")
    assert output.read_text(encoding="utf-8") == "original\n"
    assert list(tmp_path.glob(".maze-*.tmp")) == []


def test_solution_rejects_closed_wall() -> None:
    """Do not export a path that crosses closed cells."""
    with pytest.raises(ValueError, match="closed wall"):
        validate_solution(MazeGrid(2, 1), [(0, 0), (1, 0)], (0, 0), (1, 0))


def test_cli_handles_bad_encoding(tmp_path: Path) -> None:
    """Treat invalid UTF-8 as a controlled configuration read error."""
    config = tmp_path / "config.txt"
    config.write_bytes(b"\xff")
    assert main([str(config)]) == 1
