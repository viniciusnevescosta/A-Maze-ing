from dataclasses import dataclass
from typing import cast

from mazegen.config.validator import ConfigValue, Coordinate


@dataclass
class Config:
    width: int
    height: int
    entry: Coordinate
    exit: Coordinate
    output_file: str
    perfect: bool


def build_config(values: dict[str, ConfigValue]) -> Config:
    return Config(
        width=cast(int, values["WIDTH"]),
        height=cast(int, values["HEIGHT"]),
        entry=cast(Coordinate, values["ENTRY"]),
        exit=cast(Coordinate, values["EXIT"]),
        output_file=cast(str, values["OUTPUT_FILE"]),
        perfect=cast(bool, values["PERFECT"]),
    )
