"""Render walls, endpoints, reserved cells and the shortest solution."""

from mazegen.maze.cell import Cell
from mazegen.maze.grid import MazeGrid

Coordinate = tuple[int, int]
WALL_COLORS = ("\033[37m", "\033[36m", "\033[33m", "\033[35m")
RESET = "\033[0m"


def render_row(
    cells: list[Cell], markers: list[str] | None = None,
) -> tuple[str, str, str]:
    """Return top, middle and bottom lines with shared walls drawn once."""
    if markers is not None and len(markers) != len(cells):
        raise ValueError("One marker is required per cell")
    if not cells:
        return "+", "|", "+"
    top = "+"
    middle = "|" if cells[0].west else " "
    bottom = "+"
    for index, cell in enumerate(cells):
        marker = " " if markers is None else markers[index]
        if len(marker) != 1:
            raise ValueError("Markers must contain exactly one character")
        top += ("---" if cell.north else "   ") + "+"
        middle += f" {marker} " + ("|" if cell.east else " ")
        bottom += ("---" if cell.south else "   ") + "+"
    return top, middle, bottom


def render_cell(cell: Cell) -> str:
    """Render one cell independently of a maze."""
    return "\n".join(render_row([cell]))


def render_maze(
    maze: MazeGrid,
    entry: Coordinate,
    exit: Coordinate,
    path: list[Coordinate],
    reserved: set[Coordinate],
    show_path: bool = True,
    color: int | None = None,
) -> str:
    """Render the whole grid without modifying cells or solving it again."""
    solution = set(path) if show_path else set()
    lines: list[str] = []
    for y, row in enumerate(maze.grid):
        markers: list[str] = []
        for x in range(maze.width):
            coordinate = (x, y)
            marker = " "
            if coordinate in reserved:
                marker = "#"
            elif coordinate in solution:
                marker = "."
            if coordinate == entry:
                marker = "E"
            elif coordinate == exit:
                marker = "X"
            markers.append(marker)
        top, middle, bottom = render_row(row, markers)
        lines.extend((top, middle))
        if y == maze.height - 1:
            lines.append(bottom)
    text = "\n".join(lines)
    if color is not None:
        selected = WALL_COLORS[color % len(WALL_COLORS)]
        text = "".join(
            selected + character + RESET if character in "+-|" else character
            for character in text
        )
    return text
