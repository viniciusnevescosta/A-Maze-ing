def filter_valid_lines(lines: list[str]) -> list[str]:
    valid_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        valid_lines.append(line)
    return valid_lines


def parse_config_lines(lines: list[str]) -> dict[str, str]:
    config: dict[str, str] = {}
    for line in lines:
        if "=" not in line:
            raise ValueError(f"Invalid syntax (missing '='): '{line}'")

        if line.count("=") > 1:
            raise ValueError(f"Ambiguous syntax (multiple '='): '{line}'")

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError(f"Empty key in line: '{line}'")
        if not value:
            raise ValueError(f"Empty value for key '{key}' in line: '{line}'")

        config[key] = value
    return config


def parse_coordinate(value: str) -> tuple[int, int]:
    components: list[str] = value.split(",")

    if len(components) != 2:
        raise ValueError(
            f"Invalid coordinate format: expected 'x,y', got '{value}'"
        )

    x, y = components
    try:
        x_coordinate: int = int(x)
        y_coordinate: int = int(y)
    except ValueError as error:
        raise ValueError(
            f"Invalid coordinate components: expected integers, got '{value}'"
        ) from error

    return (x_coordinate, y_coordinate)
