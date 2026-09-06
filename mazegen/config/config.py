from dataclasses import dataclass


@dataclass
class Config:
    width: int
    height: int
    entry: str
    exit: str
    output_file: str
    perfect: bool
