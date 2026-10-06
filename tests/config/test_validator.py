from collections.abc import Mapping

import pytest

from mazegen.config.validator import (
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
    return {
        "WIDTH": "20",
        "HEIGHT": "15",
        "ENTRY": "0,0",
        "EXIT": "19,14",
        "OUTPUT_FILE": "maze.txt",
        "PERFECT": "True",
    }


def test_validate_required_keys_accepts_complete_config() -> None:
    validate_required_keys(valid_text_config())


def test_validate_required_keys_reports_one_missing_key() -> None:
    config = valid_text_config()
    del config["ENTRY"]

    with pytest.raises(MissingRequiredKeysError) as error:
        validate_required_keys(config)

    assert error.value.missing_keys == ("ENTRY",)
    assert str(error.value) == "Missing required configuration key: ENTRY"


def test_validate_required_keys_reports_all_missing_keys_in_schema_order(
) -> None:
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
    config = valid_text_config()
    config["SEED"] = "42"

    validate_unknown_keys(config)


def test_validate_unknown_keys_reports_all_unknown_keys() -> None:
    config = valid_text_config()
    config["COLOR"] = "blue"
    config["ALGORITHM"] = "dfs"

    with pytest.raises(UnknownConfigKeysError) as error:
        validate_unknown_keys(config)

    assert error.value.unknown_keys == ("COLOR", "ALGORITHM")
    assert str(error.value) == (
        "unknown configuration keys: COLOR, ALGORITHM"
    )


@pytest.mark.parametrize(
    "coordinate",
    [(0, 0), (19, 0), (0, 14), (19, 14), (10, 7)],
)
def test_validate_coordinate_in_bounds_accepts_valid_coordinates(
    coordinate: tuple[int, int],
) -> None:
    validate_coordinate_in_bounds("ENTRY", coordinate, 20, 15)


@pytest.mark.parametrize(
    "coordinate",
    [(-1, 0), (0, -1), (20, 0), (0, 15), (20, 15)],
)
def test_validate_coordinate_in_bounds_rejects_invalid_coordinates(
    coordinate: tuple[int, int],
) -> None:
    with pytest.raises(ValueError, match="ENTRY must be inside maze bounds"):
        validate_coordinate_in_bounds("ENTRY", coordinate, 20, 15)


def test_convert_config_coordinates_converts_entry_and_exit() -> None:
    config = valid_text_config()

    result = convert_config_coordinates(config)

    assert result["ENTRY"] == (0, 0)
    assert result["EXIT"] == (19, 14)
    assert result["WIDTH"] == "20"


def test_convert_config_coordinates_does_not_modify_input() -> None:
    config = valid_text_config()

    convert_config_coordinates(config)

    assert config["ENTRY"] == "0,0"
    assert config["EXIT"] == "19,14"


def test_validate_config_coordinates_accepts_distinct_coordinates() -> None:
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
    config: Mapping[str, ConfigValue] = {
        "WIDTH": 20,
        "HEIGHT": 15,
        "ENTRY": entry,
        "EXIT": exit_coordinate,
    }

    with pytest.raises(ValueError, match=f"{key} must be inside maze bounds"):
        validate_config_coordinates(config)


def test_validate_config_coordinates_rejects_equal_entry_and_exit() -> None:
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
    config = valid_text_config()

    result = convert_config_dimensions(config)

    assert result["WIDTH"] == 20
    assert result["HEIGHT"] == 15
    assert result["ENTRY"] == "0,0"


def test_convert_config_dimensions_does_not_modify_input() -> None:
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
    config: Mapping[str, ConfigValue] = {"PERFECT": text}

    result = convert_config_perfect(config)

    assert result["PERFECT"] is expected
    assert config["PERFECT"] == text


@pytest.mark.parametrize("value", ["true", "false", "1", "yes", ""])
def test_convert_config_perfect_rejects_invalid_values(value: str) -> None:
    config: Mapping[str, ConfigValue] = {"PERFECT": value}

    with pytest.raises(ValueError, match="PERFECT must be 'True' or 'False'"):
        convert_config_perfect(config)


def test_convert_config_seed_returns_copy_when_seed_is_absent() -> None:
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
    config: Mapping[str, ConfigValue] = {"SEED": text}

    result = convert_config_seed(config)

    assert result["SEED"] == expected
    assert config["SEED"] == text


@pytest.mark.parametrize("value", ["random", "4.2", ""])
def test_convert_config_seed_rejects_non_integer(value: str) -> None:
    config: Mapping[str, ConfigValue] = {"SEED": value}

    with pytest.raises(ValueError, match="SEED must be an integer"):
        convert_config_seed(config)
