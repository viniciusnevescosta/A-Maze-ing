from mazegen.input.config.config import Config, build_config
from mazegen.input.config.validator import ConfigValue


def test_build_config_creates_config_with_seed() -> None:
    """Verify build config creates config with seed."""
    values: dict[str, ConfigValue] = {
        "WIDTH": 20,
        "HEIGHT": 15,
        "ENTRY": (0, 0),
        "EXIT": (19, 14),
        "OUTPUT_FILE": "maze.txt",
        "PERFECT": True,
        "SEED": 42,
    }

    result = build_config(values)

    assert result == Config(
        width=20,
        height=15,
        entry=(0, 0),
        exit=(19, 14),
        output_file="maze.txt",
        perfect=True,
        seed=42,
    )


def test_build_config_uses_none_when_seed_is_absent() -> None:
    """Verify build config uses none when seed is absent."""
    values: dict[str, ConfigValue] = {
        "WIDTH": 5,
        "HEIGHT": 4,
        "ENTRY": (0, 0),
        "EXIT": (4, 3),
        "OUTPUT_FILE": "maze.txt",
        "PERFECT": False,
    }

    result = build_config(values)

    assert result.seed is None
