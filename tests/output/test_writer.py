"""Test hexadecimal maze output writing."""

from pathlib import Path
from unittest.mock import patch

import pytest

from mazegen.cli import main
from mazegen.maze.grid import MazeGrid
from mazegen.output.writer import write_maze


def test_write_maze_creates_file(tmp_path: Path) -> None:
    """Create the requested file with one newline per maze row."""
    maze = MazeGrid(3, 2)
    output_file = tmp_path / "maze.txt"

    write_maze(maze, str(output_file), (0, 0), (1, 1))

    assert output_file.read_bytes() == b"FFF\nFFF\n\n0,0\n1,1\n"


def test_write_maze_preserves_encoding_order(tmp_path: Path) -> None:
    """Write encoded rows in their original grid order."""
    maze = MazeGrid(2, 2)
    maze.remove_wall(0, 0, 1, 0)
    output_file = tmp_path / "maze.txt"

    write_maze(maze, str(output_file), (0, 0), (1, 1))

    assert output_file.read_text(encoding="utf-8") == "D7\nFF\n\n0,0\n1,1\n"


def test_write_maze_replaces_existing_contents(tmp_path: Path) -> None:
    """Replace old contents instead of appending another maze."""
    output_file = tmp_path / "maze.txt"
    output_file.write_text("old contents\n", encoding="utf-8")

    write_maze(MazeGrid(1, 1), str(output_file), (0, 0), (0, 0))

    assert output_file.read_text(encoding="utf-8") == "F\n\n0,0\n0,0\n"


def test_write_maze_propagates_write_error(tmp_path: Path) -> None:
    """Let the caller handle failures that occur during writing."""
    output_file = tmp_path / "maze.txt"

    with patch("mazegen.output.writer.open") as mock_open:
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.write.side_effect = OSError("Disk full")

        with pytest.raises(OSError, match="Disk full"):
            write_maze(MazeGrid(1, 1), str(output_file), (0, 0), (0, 0))

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
        "mazegen.cli.write_maze",
        side_effect=PermissionError("Permission denied"),
    ):
        result = main([str(config_file)])

    captured = capsys.readouterr()

    assert result == 1
    assert "Error writing output file" in captured.err
    assert "Permission denied" in captured.err
    assert "Traceback" not in captured.err


def test_write_maze_preserves_coordinate_order(tmp_path: Path) -> None:
    """Write x,y coordinates with entry before exit."""
    maze = MazeGrid(4, 3)
    output_file = tmp_path / "maze.txt"

    write_maze(maze, str(output_file), (3, 1), (0, 2))

    lines = output_file.read_text(encoding="utf-8").splitlines()

    assert lines == ["FFFF", "FFFF", "FFFF", "", "3,1", "0,2"]


@pytest.mark.parametrize(
    "entry, exit",
    [
        ((-1, 0), (1, 1)),
        ((0, 0), (2, 1)),
    ],
)
def test_invalid_coordinates_preserve_existing_file(
    tmp_path: Path,
    entry: tuple[int, int],
    exit: tuple[int, int],
) -> None:
    """Reject invalid coordinates before replacing existing contents."""
    output_file = tmp_path / "maze.txt"
    output_file.write_text("original\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside maze bounds"):
        write_maze(MazeGrid(2, 2), str(output_file), entry, exit)

    assert output_file.read_text(encoding="utf-8") == "original\n"


def test_cli_writes_configured_coordinates(tmp_path: Path) -> None:
    """Pass configured entry and exit coordinates to the output writer."""
    config_file = tmp_path / "config.txt"
    output_file = tmp_path / "maze.txt"
    config_file.write_text(
        "WIDTH=4\n"
        "HEIGHT=3\n"
        "ENTRY=3,1\n"
        "EXIT=0,2\n"
        f"OUTPUT_FILE={output_file}\n"
        "PERFECT=True\n"
        "SEED=42\n",
        encoding="utf-8",
    )

    assert main([str(config_file)]) == 0

    lines = output_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 6
    assert all(len(row) == 4 for row in lines[:3])
    assert lines[3:] == ["", "3,1", "0,2"]
