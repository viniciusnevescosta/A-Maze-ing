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
