from collections.abc import Mapping

import pytest

from mazegen.input.config.validator import (
    ConfigValue,
    MissingRequiredKeysError,
    UnknownConfigKeysError,
    convert_config_coordinates,
    convert_config_dimensions,
    convert_config_perfect,
    convert_config_seed,
    validate_config_coordinates,
    validate_coordinate_in_bounds,
    validate_required_keys,
    validate_unknown_keys,
)


def valid_text_config() -> dict[str, str]:
    """Return a fresh dictionary with valid configuration text."""
    return {
        "WIDTH": "20",
        "HEIGHT": "15",
        "ENTRY": "0,0",
        "EXIT": "19,14",
        "OUTPUT_FILE": "maze.txt",
        "PERFECT": "True",
    }


def test_validate_required_keys_accepts_complete_config() -> None:
    """Verify validate required keys accepts complete config."""
    validate_required_keys(valid_text_config())


def test_validate_required_keys_reports_one_missing_key() -> None:
    """Verify validate required keys reports one missing key."""
    config = valid_text_config()
    del config["ENTRY"]

    with pytest.raises(MissingRequiredKeysError) as error:
        validate_required_keys(config)

    assert error.value.missing_keys == ("ENTRY",)
    assert str(error.value) == "Missing required configuration key: ENTRY"


def test_validate_required_keys_reports_all_missing_keys_in_schema_order() -> (
    None
):
    """Verify missing keys are reported in schema order."""
    config = {"WIDTH": "20"}

    with pytest.raises(MissingRequiredKeysError) as error:
        validate_required_keys(config)

    assert error.value.missing_keys == (
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    )


def test_validate_unknown_keys_accepts_required_and_optional_keys() -> None:
    """Verify validate unknown keys accepts required and optional keys."""
    config = valid_text_config()
    config["SEED"] = "42"

    validate_unknown_keys(config)


def test_validate_unknown_keys_reports_all_unknown_keys() -> None:
    """Verify validate unknown keys reports all unknown keys."""
    config = valid_text_config()
    config["COLOR"] = "blue"
    config["ALGORITHM"] = "dfs"

    with pytest.raises(UnknownConfigKeysError) as error:
        validate_unknown_keys(config)

    assert error.value.unknown_keys == ("COLOR", "ALGORITHM")
    assert str(error.value) == ("unknown configuration keys: COLOR, ALGORITHM")


@pytest.mark.parametrize(
    "coordinate",
    [(0, 0), (19, 0), (0, 14), (19, 14), (10, 7)],
)
def test_validate_coordinate_in_bounds_accepts_valid_coordinates(
    coordinate: tuple[int, int],
) -> None:
    """Verify validate coordinate in bounds accepts valid coordinates."""
    validate_coordinate_in_bounds("ENTRY", coordinate, 20, 15)


@pytest.mark.parametrize(
    "coordinate",
    [(-1, 0), (0, -1), (20, 0), (0, 15), (20, 15)],
)
def test_validate_coordinate_in_bounds_rejects_invalid_coordinates(
    coordinate: tuple[int, int],
) -> None:
    """Verify validate coordinate in bounds rejects invalid coordinates."""
    with pytest.raises(ValueError, match="ENTRY must be inside maze bounds"):
        validate_coordinate_in_bounds("ENTRY", coordinate, 20, 15)


def test_convert_config_coordinates_converts_entry_and_exit() -> None:
    """Verify convert config coordinates converts entry and exit."""
    config = valid_text_config()

    result = convert_config_coordinates(config)

    assert result["ENTRY"] == (0, 0)
    assert result["EXIT"] == (19, 14)
    assert result["WIDTH"] == "20"


def test_convert_config_coordinates_does_not_modify_input() -> None:
    """Verify convert config coordinates does not modify input."""
    config = valid_text_config()

    convert_config_coordinates(config)

    assert config["ENTRY"] == "0,0"
    assert config["EXIT"] == "19,14"


def test_validate_config_coordinates_accepts_distinct_coordinates() -> None:
    """Verify validate config coordinates accepts distinct coordinates."""
    config: Mapping[str, ConfigValue] = {
        "WIDTH": 20,
        "HEIGHT": 15,
        "ENTRY": (0, 0),
        "EXIT": (19, 14),
    }

    validate_config_coordinates(config)


@pytest.mark.parametrize(
    ("key", "entry", "exit_coordinate"),
    [
        ("ENTRY", (-1, 0), (19, 14)),
        ("EXIT", (0, 0), (20, 14)),
    ],
)
def test_validate_config_coordinates_rejects_out_of_bounds_coordinate(
    key: str,
    entry: tuple[int, int],
    exit_coordinate: tuple[int, int],
) -> None:
    """Verify validate config coordinates rejects out of bounds coordinate."""
    config: Mapping[str, ConfigValue] = {
        "WIDTH": 20,
        "HEIGHT": 15,
        "ENTRY": entry,
        "EXIT": exit_coordinate,
    }

    with pytest.raises(ValueError, match=f"{key} must be inside maze bounds"):
        validate_config_coordinates(config)


def test_validate_config_coordinates_rejects_equal_entry_and_exit() -> None:
    """Verify validate config coordinates rejects equal entry and exit."""
    config: Mapping[str, ConfigValue] = {
        "WIDTH": 20,
        "HEIGHT": 15,
        "ENTRY": (1, 1),
        "EXIT": (1, 1),
    }

    with pytest.raises(
        ValueError,
        match="ENTRY and EXIT must be different coordinates",
    ):
        validate_config_coordinates(config)


def test_convert_config_dimensions_converts_width_and_height() -> None:
    """Verify convert config dimensions converts width and height."""
    config = valid_text_config()

    result = convert_config_dimensions(config)

    assert result["WIDTH"] == 20
    assert result["HEIGHT"] == 15
    assert result["ENTRY"] == "0,0"


def test_convert_config_dimensions_does_not_modify_input() -> None:
    """Verify convert config dimensions does not modify input."""
    config = valid_text_config()

    convert_config_dimensions(config)

    assert config["WIDTH"] == "20"
    assert config["HEIGHT"] == "15"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("WIDTH", "wide"),
        ("HEIGHT", "tall"),
    ],
)
def test_convert_config_dimensions_rejects_non_integer(
    key: str,
    value: str,
) -> None:
    """Verify convert config dimensions rejects non integer."""
    config = valid_text_config()
    config[key] = value

    with pytest.raises(ValueError, match=f"{key} must be an integer"):
        convert_config_dimensions(config)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("WIDTH", "0"),
        ("WIDTH", "-1"),
        ("HEIGHT", "0"),
        ("HEIGHT", "-1"),
    ],
)
def test_convert_config_dimensions_rejects_non_positive_values(
    key: str,
    value: str,
) -> None:
    """Verify convert config dimensions rejects non positive values."""
    config = valid_text_config()
    config[key] = value

    with pytest.raises(ValueError, match=f"{key} must be greater than zero"):
        convert_config_dimensions(config)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("True", True), ("False", False)],
)
def test_convert_config_perfect_converts_exact_boolean_values(
    text: str,
    expected: bool,
) -> None:
    """Verify convert config perfect converts exact boolean values."""
    config: Mapping[str, ConfigValue] = {"PERFECT": text}

    result = convert_config_perfect(config)

    assert result["PERFECT"] is expected
    assert config["PERFECT"] == text


@pytest.mark.parametrize("value", ["true", "false", "1", "yes", ""])
def test_convert_config_perfect_rejects_invalid_values(value: str) -> None:
    """Verify convert config perfect rejects invalid values."""
    config: Mapping[str, ConfigValue] = {"PERFECT": value}

    with pytest.raises(ValueError, match="PERFECT must be 'True' or 'False'"):
        convert_config_perfect(config)


def test_convert_config_seed_returns_copy_when_seed_is_absent() -> None:
    """Verify convert config seed returns copy when seed is absent."""
    config: Mapping[str, ConfigValue] = {"WIDTH": 20}

    result = convert_config_seed(config)

    assert result == config
    assert result is not config


@pytest.mark.parametrize(
    ("text", "expected"),
    [("42", 42), ("0", 0), ("-10", -10)],
)
def test_convert_config_seed_converts_integer(
    text: str,
    expected: int,
) -> None:
    """Verify convert config seed converts integer."""
    config: Mapping[str, ConfigValue] = {"SEED": text}

    result = convert_config_seed(config)

    assert result["SEED"] == expected
    assert config["SEED"] == text


@pytest.mark.parametrize("value", ["random", "4.2", ""])
def test_convert_config_seed_rejects_non_integer(value: str) -> None:
    """Verify convert config seed rejects non integer."""
    config: Mapping[str, ConfigValue] = {"SEED": value}

    with pytest.raises(ValueError, match="SEED must be an integer"):
        convert_config_seed(config)
