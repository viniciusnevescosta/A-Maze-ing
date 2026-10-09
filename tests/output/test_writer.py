"""Test hexadecimal maze output writing."""

from pathlib import Path
from unittest.mock import patch

import pytest

from mazegen.input.cli import main
from mazegen.maze.grid import MazeGrid
from mazegen.output.writer import write_maze


def test_write_maze_creates_file(tmp_path: Path) -> None:
    """Create the requested file with one newline per maze row."""
    maze = MazeGrid(3, 2)
    output_file = tmp_path / "maze.txt"

    write_maze(maze, str(output_file))

    assert output_file.read_bytes() == b"FFF\nFFF\n"


def test_write_maze_preserves_encoding_order(tmp_path: Path) -> None:
    """Write encoded rows in their original grid order."""
    maze = MazeGrid(2, 2)
    maze.remove_wall(0, 0, 1, 0)
    output_file = tmp_path / "maze.txt"

    write_maze(maze, str(output_file))

    assert output_file.read_text(encoding="utf-8") == "D7\nFF\n"


def test_write_maze_replaces_existing_contents(tmp_path: Path) -> None:
    """Replace old contents instead of appending another maze."""
    output_file = tmp_path / "maze.txt"
    output_file.write_text("old contents\n", encoding="utf-8")

    write_maze(MazeGrid(1, 1), str(output_file))

    assert output_file.read_text(encoding="utf-8") == "F\n"


def test_write_maze_propagates_write_error(tmp_path: Path) -> None:
    """Let the caller handle failures that occur during writing."""
    output_file = tmp_path / "maze.txt"

    with patch("mazegen.output.writer.open") as mock_open:
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.write.side_effect = OSError("Disk full")

        with pytest.raises(OSError, match="Disk full"):
            write_maze(MazeGrid(1, 1), str(output_file))

        mock_open.return_value.__exit__.assert_called_once()


def test_cli_handles_output_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Report output failures without an unexpected traceback."""
    config_file = tmp_path / "config.txt"
    config_file.write_text(
        "WIDTH=2\n"
        "HEIGHT=2\n"
        "ENTRY=0,0\n"
        "EXIT=1,1\n"
        f"OUTPUT_FILE={tmp_path / 'maze.txt'}\n"
        "PERFECT=True\n",
        encoding="utf-8",
    )

    with patch(
        "mazegen.input.cli.write_maze",
        side_effect=PermissionError("Permission denied"),
    ):
        result = main([str(config_file)])

    captured = capsys.readouterr()

    assert result == 1
    assert "Error writing output file" in captured.err
    assert "Permission denied" in captured.err
    assert "Traceback" not in captured.err
