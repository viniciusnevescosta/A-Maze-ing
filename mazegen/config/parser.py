def filter_valid_lines(lines: list[str]) -> list[str]:
    valid_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        valid_lines.append(line)

    return valid_lines
