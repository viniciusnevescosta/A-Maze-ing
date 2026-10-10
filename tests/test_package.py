"""Verify that the subject's root wheel is complete and installable offline."""

import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile


def test_wheel_contains_current_sources_and_documentation() -> None:
    """Reject stale release code or missing reusable-module documentation."""
    root = Path(__file__).resolve().parents[1]
    artifact = root / "mazegen-1.0.0-py3-none-any.whl"
    with ZipFile(artifact) as wheel:
        for source in (root / "mazegen").rglob("*.py"):
            relative = source.relative_to(root).as_posix()
            assert wheel.read(relative) == source.read_bytes()
        metadata = wheel.read("mazegen-1.0.0.dist-info/METADATA").decode()
        assert "from mazegen import MazeGenerator" in metadata
        assert "License-Expression: MIT" in metadata
        assert wheel.read("mazegen-1.0.0.dist-info/licenses/LICENSE.md")


def test_offline_install_and_external_import(tmp_path: Path) -> None:
    """Install the wheel in a fresh venv and import it outside the repo."""
    root = Path(__file__).resolve().parents[1]
    artifact = root / "mazegen-1.0.0-py3-none-any.whl"
    environment = tmp_path / "environment"
    subprocess.run(
        [sys.executable, "-m", "venv", str(environment)], check=True,
        capture_output=True, text=True,
    )
    directory = "Scripts" if sys.platform == "win32" else "bin"
    executable = "python.exe" if sys.platform == "win32" else "python"
    python = environment / directory / executable
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-deps", str(artifact)],
        check=True, capture_output=True, text=True,
    )
    script = (
        "from mazegen import MazeGenerator; "
        "m = MazeGenerator(20, 15, seed=42); "
        "m.generate(False); "
        "m.validate_non_perfect(); "
        "assert m.get_cell(2, 3) is m.grid[3][2]; "
        "assert m.solve((0, 0), (19, 14))"
    )
    subprocess.run(
        [str(python), "-I", "-c", script], cwd=tmp_path, check=True,
        capture_output=True, text=True,
    )
