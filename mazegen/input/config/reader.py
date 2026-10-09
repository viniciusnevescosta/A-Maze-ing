def read_config_file(path: str) -> list[str]:
    """Read UTF-8 lines without line endings; propagate file errors."""
    with open(path, "r", encoding="utf-8") as file:
        return [line.rstrip("\r\n") for line in file]
