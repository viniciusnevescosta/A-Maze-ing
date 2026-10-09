"""Test safe pattern placement and endpoint protection."""

from pathlib import Path

import pytest

from mazegen.cli import main
from mazegen.maze.generator import MazeGenerator
from mazegen.maze.grid import MazeGrid
from mazegen.maze.pattern_application import (
    choose_pattern_cells,
    get_pattern_cells,
)
from mazegen.maze.solver import solve_bfs


def test_safe_center_is_preserved() -> None:
    """Keep the centered drawing when it protects both endpoints."""
    maze = MazeGrid(20, 15)

    reserved = choose_pattern_cells(maze, (0, 0), (19, 14))

    assert reserved == get_pattern_cells((6, 5))


@pytest.mark.parametrize(
    "entry, exit",
    [
        ((6, 5), (19, 14)),
        ((0, 0), (6, 5)),
        ((6, 5), (8, 5)),
    ],
)
def test_center_collisions_reposition_pattern(
    entry: tuple[int, int],
    exit: tuple[int, int],
) -> None:
    """Move the drawing instead of blocking customized endpoints."""
    maze = MazeGenerator(20, 15, seed=42)

    maze.reserved = choose_pattern_cells(maze, entry, exit)

    assert len(maze.reserved) == 20
    assert maze.reserved != get_pattern_cells((6, 5))
    assert entry not in maze.reserved
    assert exit not in maze.reserved

    maze.generate_perfect(*entry)
    maze.validate_connectivity(*entry, reserved=maze.reserved)

    path = solve_bfs(maze, entry, exit)

    assert path[0] == entry
    assert path[-1] == exit
    assert not set(path) & maze.reserved

    for coordinate in (entry, exit):
        cell = maze.get_cell(*coordinate)
        assert not (cell.north and cell.east and cell.south and cell.west)


def test_no_safe_position_omits_pattern() -> None:
    """Omit a fitting drawing when it would split the corridors."""
    maze = MazeGenerator(7, 5, seed=42)

    maze.reserved = choose_pattern_cells(maze, (1, 0), (0, 4))

    assert maze.reserved == set()

    maze.generate_perfect(1, 0)
    assert len(maze.get_reachable_cells(1, 0)) == 35
    assert solve_bfs(maze, (1, 0), (0, 4))


def test_small_maze_omits_pattern() -> None:
    """Return no reservations when the drawing cannot fit."""
    maze = MazeGrid(2, 2)

    assert choose_pattern_cells(maze, (0, 0), (1, 1)) == set()


def test_placement_is_deterministic() -> None:
    """Choose the same position without consuming generation randomness."""
    maze = MazeGenerator(20, 15, seed=42)
    random_state = maze.random.getstate()

    first = choose_pattern_cells(maze, (6, 5), (19, 14))
    second = choose_pattern_cells(maze, (6, 5), (19, 14))

    assert first == second
    assert maze.random.getstate() == random_state


def test_cli_warns_when_no_safe_position_exists(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Continue generating without the drawing when placement is unsafe."""
    output_file = tmp_path / "maze.txt"
    config_file = tmp_path / "config.txt"
    config_file.write_text(
        "WIDTH=7\nHEIGHT=5\nENTRY=1,0\nEXIT=0,4\n"
        f"OUTPUT_FILE={output_file}\nPERFECT=True\nSEED=42\n",
        encoding="utf-8",
    )

    assert main([str(config_file)]) == 0

    captured = capsys.readouterr()
    assert "no safe position for the 42 pattern" in captured.err
    assert "generating without it" in captured.err
    assert "Traceback" not in captured.err

    lines = output_file.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 9
    assert all("F" not in row for row in lines[:5])
    assert lines[5:8] == ["", "1,0", "0,4"]
    assert lines[8]
    assert set(lines[8]) <= set("NESW")
