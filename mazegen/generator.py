from random import Random
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

    def __init__(
        self, width: int, height: int, seed: int | None = None
    ) -> None:
        """Create a grid of independent, fully closed cells.

        Args:
            width: Number of columns, greater than zero.
            height: Number of rows, greater than zero.
            seed: Optional seed for reproducible random choices.

        Raises:
            ValueError: If either dimension is not greater than zero.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Maze dimensions must be greater than zero")

        self.width: int = width
        self.height: int = height
        self.grid: list[list[Cell]] = []
        self.visited: set[tuple[int, int]] = set()
        self.random: Random = Random(seed)

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

    def remove_wall(
        self,
        x: int,
        y: int,
        neighbor_x: int,
        neighbor_y: int,
    ) -> None:
        """Open the shared wall between two orthogonally adjacent cells.

        Args:
            x: Column index of the first cell.
            y: Row index of the first cell.
            neighbor_x: Column index of the second cell.
            neighbor_y: Row index of the second cell.

        Raises:
            ValueError: If either cell is outside the maze or the cells
                are not orthogonally adjacent.
        """
        cell = self.get_cell(x, y)
        neighbor = self.get_cell(neighbor_x, neighbor_y)

        neighbors = self.get_neighbors(x, y)
        direction: Direction | None = None

        for candidate_direction, coordinate in neighbors.items():
            if coordinate == (neighbor_x, neighbor_y):
                direction = candidate_direction
                break

        if direction is None:
            raise ValueError(
                "Cells must be orthogonally adjacent: "
                f"({x}, {y}) and ({neighbor_x}, {neighbor_y})"
            )

        if direction == "north":
            cell.north = False
            neighbor.south = False
        elif direction == "east":
            cell.east = False
            neighbor.west = False
        elif direction == "south":
            cell.south = False
            neighbor.north = False
        elif direction == "west":
            cell.west = False
            neighbor.east = False

    def validate_external_walls(self) -> None:
        """Check that every external wall is closed.

        Raises:
            ValueError: If an external wall is open.
        """
        for x in range(self.width):
            top_cell = self.get_cell(x, 0)
            bottom_cell = self.get_cell(x, self.height - 1)

            if not top_cell.north:
                raise ValueError(f"Open external North wall at ({x}, 0)")

            if not bottom_cell.south:
                raise ValueError(
                    f"Open external South wall at ({x}, {self.height - 1})"
                )

        for y in range(self.height):
            left_cell = self.get_cell(0, y)
            right_cell = self.get_cell(self.width - 1, y)

            if not left_cell.west:
                raise ValueError(f"Open external West wall at (0, {y})")

            if not right_cell.east:
                raise ValueError(
                    f"Open external East wall at ({self.width - 1}, {y})"
                )

    def mark_visited(self, x: int, y: int) -> None:
        """Mark an existing cell as visited."""
        self.get_cell(x, y)
        self.visited.add((x, y))

    def is_visited(self, x: int, y: int) -> bool:
        """Return whether an existing cell has been visited."""
        self.get_cell(x, y)
        return (x, y) in self.visited

    def reset_visited(self) -> None:
        """Clear the visit history for a new generation."""
        self.visited.clear()

    def choose_unvisited_neighbor(
        self,
        x: int,
        y: int,
    ) -> tuple[int, int] | None:
        """Choose a random unvisited neighbor, or return None.

        Raises:
            ValueError: If the source coordinates are outside the maze.
        """
        neighbors = self.get_neighbors(x, y)
        candidates: list[tuple[int, int]] = []

        for neighbor_x, neighbor_y in neighbors.values():
            if not self.is_visited(neighbor_x, neighbor_y):
                candidates.append((neighbor_x, neighbor_y))

        if not candidates:
            return None

        return self.random.choice(candidates)
