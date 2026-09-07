from dataclasses import dataclass
from typing import cast

from mazegen.config.validator import ConfigValue


@dataclass
class Config:
    width: int
    height: int
    entry: str
    exit: str
    output_file: str
    perfect: bool
    seed: int | None = None


def build_config(values: dict[str, ConfigValue]) -> Config:
    return Config(
        width=cast(int, values["WIDTH"]),
        height=cast(int, values["HEIGHT"]),
        entry=cast(str, values["ENTRY"]),
        exit=cast(str, values["EXIT"]),
        output_file=cast(str, values["OUTPUT_FILE"]),
        perfect=cast(bool, values["PERFECT"]),
        seed=cast(int | None, values.get("SEED")),
    )
