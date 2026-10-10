"""Detect and prevent completely open 3x3 regions."""

from mazegen.maze.grid import MazeGrid

Coordinate = tuple[int, int]


def has_open_area(
    maze: MazeGrid, affected: Coordinate | None = None,
) -> bool:
    """Return whether any 3x3 block has all internal passages open."""
    left_min, top_min = 0, 0
    left_max, top_max = maze.width - 2, maze.height - 2
    if affected is not None:
        x, y = affected
        left_min, top_min = max(0, x - 2), max(0, y - 2)
        left_max, top_max = min(left_max, x + 1), min(top_max, y + 1)
    for top in range(top_min, top_max):
        for left in range(left_min, left_max):
            open_block = True
            for y in range(top, top + 3):
                for x in range(left, left + 3):
                    cell = maze.get_cell(x, y)
                    if x < left + 2:
                        neighbor = maze.get_cell(x + 1, y)
                        if cell.east or neighbor.west:
                            open_block = False
                    if y < top + 2:
                        neighbor = maze.get_cell(x, y + 1)
                        if cell.south or neighbor.north:
                            open_block = False
            if open_block:
                return True
    return False


def open_safe_passage(
    maze: MazeGrid,
    source: Coordinate,
    target: Coordinate,
    reserved: set[Coordinate],
) -> bool:
    """Open one closed internal passage unless it creates a 3x3 area."""
    cell = maze.get_cell(*source)
    neighbor = maze.get_cell(*target)
    if source in reserved or target in reserved:
        return False
    opposites = {"north": "south", "east": "west",
                 "south": "north", "west": "east"}
    direction = None
    for side, coordinate in maze.get_neighbors(*source).items():
        if coordinate == target:
            direction = side
            break
    if direction is None:
        raise ValueError("Cells must be orthogonally adjacent")
    opposite = opposites[direction]
    if not getattr(cell, direction) or not getattr(neighbor, opposite):
        return False
    maze.remove_wall(*source, *target)
    if has_open_area(maze, source):
        setattr(cell, direction, True)
        setattr(neighbor, opposite, True)
        return False
    return True
