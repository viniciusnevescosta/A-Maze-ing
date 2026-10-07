from mazegen.cell import Cell


class MazeGenerator:
    """Store the dimensions and cell grid of a maze.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        grid: Cells arranged as grid[y][x].
    """

    def __init__(self, width: int, height: int) -> None:
        """Create a grid of independent, fully closed cells.

        Args:
            width: Number of columns, greater than zero.
            height: Number of rows, greater than zero.

        Raises:
            ValueError: If either dimension is not greater than zero.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Maze dimensions must be greater than zero")

        self.width: int = width
        self.height: int = height
        self.grid: list[list[Cell]] = []

        for y in range(height):
            row: list[Cell] = []

            for x in range(width):
                row.append(Cell())

            self.grid.append(row)

    def get_cell(self, x: int, y: int) -> Cell:
        """Return the cell at the given coordinates.

        Args:
            x: Column index.
            y: Row index.

        Raises:
            ValueError: If the coordinates are outside the maze.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(
                f"Coordinates outside maze bounds: ({x}, {y})"
            )

        return self.grid[y][x]
