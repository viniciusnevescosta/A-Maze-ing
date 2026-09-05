from collections.abc import Mapping

ConfigValue = str | int


REQUIRED_CONFIG_KEYS = (
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
)


class MissingRequiredKeysError(ValueError):
    def __init__(self, missing_keys: tuple[str, ...]) -> None:
        self.missing_keys = missing_keys
        keys = ", ".join(missing_keys)
        key_label: str = "key" if len(missing_keys) == 1 else "keys"
        super().__init__(f"Missing required configuration {key_label}: {keys}")


def validate_required_keys(config: Mapping[str, str]) -> None:
    missing_keys: list[str] = []

    for key in REQUIRED_CONFIG_KEYS:
        if key not in config:
            missing_keys.append(key)

    if missing_keys:
        raise MissingRequiredKeysError(tuple(missing_keys))


def convert_dimensions(
    config: Mapping[str, str],
) -> dict[str, ConfigValue]:
    converted_config: dict[str, ConfigValue] = dict(config)
    for key in ("WIDTH", "HEIGHT"):
        try:
            value = int(config[key])
        except ValueError as error:
            raise ValueError(
                f"{key} must be an integer: '{config[key]}'"
            ) from error

        if value <= 0:
            raise ValueError(
                f"{key} must be greater than zero: '{config[key]}'"
            )

        converted_config[key] = value
    return converted_config
