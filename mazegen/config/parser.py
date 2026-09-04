

def filter_valid_lines(lines: list[str]) -> list[str]:
    valid_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        valid_lines.append(line)

    return valid_lines


def parse_config_lines(lines: list[str]) -> dict[str, str]:
    config: dict[str, str] = {}

    for line in lines:
        key, value = line.split("=")
        config[key] = value

    return config
