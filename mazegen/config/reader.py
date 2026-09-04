import sys

def read_config_file(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as file:
            return [line.rstrip("\r\n") for line in file]
