from pathlib import Path

import pytest

from mazegen.input.config.reader import read_config_file


def test_read_config_file_returns_lines_without_line_endings(
    tmp_path: Path,
) -> None:
    """Verify read config file returns lines without line endings."""
    config_path = tmp_path / "config.txt"
    config_path.write_text(
        "WIDTH=20\nHEIGHT=15\n\nPERFECT=True\n",
        encoding="utf-8",
    )

    result = read_config_file(str(config_path))

    assert result == ["WIDTH=20", "HEIGHT=15", "", "PERFECT=True"]


def test_read_config_file_accepts_crlf_and_missing_final_newline(
    tmp_path: Path,
) -> None:
    """Verify read config file accepts crlf and missing final newline."""
    config_path = tmp_path / "config.txt"
    config_path.write_bytes(b"WIDTH=20\r\nHEIGHT=15")

    result = read_config_file(str(config_path))

    assert result == ["WIDTH=20", "HEIGHT=15"]


def test_read_config_file_reads_utf8_content(tmp_path: Path) -> None:
    """Verify read config file reads utf8 content."""
    config_path = tmp_path / "config.txt"
    config_path.write_text("# configuração\nWIDTH=20\n", encoding="utf-8")

    result = read_config_file(str(config_path))

    assert result == ["# configuração", "WIDTH=20"]


def test_read_config_file_raises_when_file_does_not_exist(
    tmp_path: Path,
) -> None:
    """Verify read config file raises when file does not exist."""
    missing_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        read_config_file(str(missing_path))
