from mazegen.config.parser import filter_valid_lines


def test_preserves_valid_line() -> None:
    line = ["key=value"]
    expected_result = ["key=value"]
    result = filter_valid_lines(line)
    assert result == expected_result


def test_ignores_comment_line() -> None:
    line = ["# comment"]
    expected_result: list[str] = []
    result = filter_valid_lines(line)
    assert result == expected_result


def test_ignores_empty_line() -> None:
    line = [""]
    expected_result: list[str] = []
    result = filter_valid_lines(line)
    assert result == expected_result


def test_ignores_whitespace_only_line() -> None:
    line = ["  "]
    expected_result: list[str] = []
    result = filter_valid_lines(line)
    assert result == expected_result
