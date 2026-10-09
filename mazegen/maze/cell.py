from dataclasses import dataclass


@dataclass
class Cell:
    """Represent a maze cell with four independently stored walls.

    Attributes:
        north: Whether the north wall is closed.
        east: Whether the east wall is closed.
        south: Whether the south wall is closed.
        west: Whether the west wall is closed.

    A True value means a closed wall; False means an open passage.
    New cells start with all four walls closed.
    """

    north: bool = True
    east: bool = True
    south: bool = True
    west: bool = True
