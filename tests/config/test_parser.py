import pytest

from mazegen.config.parser import (
    filter_valid_lines,
    parse_config_lines,
    parse_coordinate,
)


def test_filter_valid_lines_preserves_only_configuration_lines() -> None:
    lines = [
        "",
        "   ",
        "# comment",
        "  # indented comment",
        "WIDTH=20",
        " HEIGHT = 15 ",
    ]

    result = filter_valid_lines(lines)

    assert result == ["WIDTH=20", " HEIGHT = 15 "]


def test_filter_valid_lines_does_not_modify_input() -> None:
    lines = ["# comment", "WIDTH=20"]
    original_lines = lines.copy()

    filter_valid_lines(lines)

    assert lines == original_lines


def test_parse_config_lines_builds_dictionary_and_strips_whitespace() -> None:
    lines = [" WIDTH = 20 ", "HEIGHT=15", "PERFECT = True"]

    result = parse_config_lines(lines)

    assert result == {
        "WIDTH": "20",
        "HEIGHT": "15",
        "PERFECT": "True",
    }


def test_parse_config_lines_uses_last_value_for_duplicate_key() -> None:
    lines = ["WIDTH=10", "WIDTH=20"]

    result = parse_config_lines(lines)

    assert result == {"WIDTH": "20"}


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("WIDTH 20", "missing '='"),
        ("WIDTH=10=20", "multiple '='"),
        ("=20", "Empty key"),
        ("WIDTH=", "Empty value"),
        ("   =20", "Empty key"),
        ("WIDTH=   ", "Empty value"),
    ],
)
def test_parse_config_lines_rejects_invalid_syntax(
    line: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        parse_config_lines([line])


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("0,0", (0, 0)),
        ("19,14", (19, 14)),
        ("-1,5", (-1, 5)),
        (" 10 , 20 ", (10, 20)),
    ],
)
def test_parse_coordinate_returns_integer_pair(
    text: str,
    expected: tuple[int, int],
) -> None:
    assert parse_coordinate(text) == expected


@pytest.mark.parametrize("text", ["", "10", "10,20,30"])
def test_parse_coordinate_rejects_wrong_component_count(text: str) -> None:
    with pytest.raises(ValueError, match="expected 'x,y'"):
        parse_coordinate(text)


@pytest.mark.parametrize("text", ["x,20", "10,y", "10.5,20"])
def test_parse_coordinate_rejects_non_integer_components(text: str) -> None:
    with pytest.raises(ValueError, match="expected integers"):
        parse_coordinate(text)
