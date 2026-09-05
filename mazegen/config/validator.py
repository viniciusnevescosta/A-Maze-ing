from collections.abc import Mapping


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
        super().__init__(
            f"Missing required configuration {key_label}: {keys}"
        )


def validate_required_keys(config: Mapping[str, str]) -> None:
    pass