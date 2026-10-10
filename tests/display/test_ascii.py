"""Check ASCII walls, endpoint markers and required interactions."""

from unittest.mock import patch

import pytest

from mazegen.display.ascii import render_cell, render_maze, render_row
from mazegen.display.interactive import run_menu
from mazegen.maze.cell import Cell
from mazegen.maze.encoding import maze_to_hex
from mazegen.maze.generator import MazeGenerator


def test_single_cell_and_row() -> None:
    """Render one cell and shared walls without duplicated boundaries."""
    assert render_cell(Cell()) == "+---+\n|   |\n+---+"
    assert render_row([Cell(), Cell()])[1] == "|   |   |"
    assert render_cell(Cell(east=False)).splitlines()[1] == "|    "


def test_full_render_and_toggle() -> None:
    """Show every cell, endpoints and solution without altering the maze."""
    maze = MazeGenerator(3, 2, seed=42)
    maze.generate_perfect()
    path = maze.solve((0, 0), (2, 1))
    before = maze_to_hex(maze)
    visible = render_maze(maze, (0, 0), (2, 1), path, set())
    hidden = render_maze(maze, (0, 0), (2, 1), path, set(), False)
    assert len(visible.splitlines()) == 5
    assert all(len(line) == 13 for line in visible.splitlines())
    assert "E" in visible and "X" in visible and "." in visible
    assert "." not in hidden
    assert before == maze_to_hex(maze)


def test_interactive_actions(capsys: pytest.CaptureFixture[str]) -> None:
    """Toggle solution and colors without regeneration; r regenerates once."""
    maze = MazeGenerator(3, 2, seed=42)
    maze.generate_perfect()
    path = maze.solve((0, 0), (2, 1))
    with patch("builtins.input", side_effect=["s", "c", "r", "q"]):
        with patch("mazegen.display.interactive.render_maze") as render:
            with patch("builtins.print"):
                from unittest.mock import Mock
                regenerate = Mock(return_value=path)
                run_menu(maze, (0, 0), (2, 1), path, regenerate)
    regenerate.assert_called_once()
    assert render.call_args_list[0].args[-2:] == (True, 0)
    assert render.call_args_list[1].args[-2:] == (False, 0)
    assert render.call_args_list[2].args[-2:] == (False, 1)


def test_pattern_and_colors() -> None:
    """Render reserved cells distinctly and apply ANSI only on demand."""
    maze = MazeGenerator(20, 15, seed=42)
    maze.generate()
    path = maze.solve((0, 0), (19, 14))
    plain = render_maze(maze, (0, 0), (19, 14), path, maze.reserved)
    colored = render_maze(maze, (0, 0), (19, 14), path, maze.reserved, color=1)
    assert plain.count("#") == 20
    assert "\033[" not in plain
    assert "\033[36m" in colored
