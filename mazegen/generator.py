from typing import Literal

from mazegen.cell import Cell

Direction = Literal["north", "east", "south", "west"]


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
            raise ValueError(f"Coordinates outside maze bounds: ({x}, {y})")

        return self.grid[y][x]

    def get_neighbors(
        self,
        x: int,
        y: int,
    ) -> dict[Direction, tuple[int, int]]:
        """Return existing orthogonal neighbors and their directions.

        Neighbors are returned in north, east, south, west order.
        Walls are not considered when finding neighbors.

        Args:
            x: Column index of the source cell.
            y: Row index of the source cell.

        Returns:
            A mapping from each valid direction to neighbor coordinates.

        Raises:
            ValueError: If the source coordinates are outside the maze.
        """
        self.get_cell(x, y)

        candidates: dict[Direction, tuple[int, int]] = {
            "north": (x, y - 1),
            "east": (x + 1, y),
            "south": (x, y + 1),
            "west": (x - 1, y),
        }

        neighbors: dict[Direction, tuple[int, int]] = {}

        for direction, coordinate in candidates.items():
            neighbor_x, neighbor_y = coordinate

            if 0 <= neighbor_x < self.width and 0 <= neighbor_y < self.height:
                neighbors[direction] = coordinate

        return neighbors
