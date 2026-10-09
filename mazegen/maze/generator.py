"""Seeded perfect-maze generation using iterative recursive backtracking."""

from random import Random

from mazegen.maze.cell import Cell
from mazegen.maze.grid import Direction as Direction
from mazegen.maze.grid import MazeGrid

__all__ = ["Direction", "MazeGenerator"]


class MazeGenerator(MazeGrid):
    """Generate mazes while keeping grid operations available to callers."""

    def __init__(
        self, width: int, height: int, seed: int | None = None
    ) -> None:
        """Create a closed grid and initialize visits and seeded randomness."""
        super().__init__(width, height)
        self.visited: set[tuple[int, int]] = set()
        self.random: Random = Random(seed)

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

    def step(
        self,
        x: int,
        y: int,
    ) -> tuple[int, int] | None:
        """Open a passage to an unvisited neighbor and mark it visited.

        Return the neighbor coordinates, or None if none is available.

        Raises:
            ValueError: If the current cell is invalid or unvisited.
        """
        if not self.is_visited(x, y):
            raise ValueError(
                f"Current cell must be visited before a step: ({x}, {y})"
            )

        neighbor = self.choose_unvisited_neighbor(x, y)

        if neighbor is None:
            return None

        neighbor_x, neighbor_y = neighbor

        self.remove_wall(x, y, neighbor_x, neighbor_y)
        self.mark_visited(neighbor_x, neighbor_y)

        return neighbor

    def backtrack(
        self,
        start_x: int = 0,
        start_y: int = 0,
    ) -> None:
        """Explore the grid using a stack and backtrack at dead ends.

        Raises:
            ValueError: If the start is invalid or visits already exist.
        """
        self.get_cell(start_x, start_y)

        if self.visited:
            raise ValueError(
                "Backtracking must start with an empty visit history"
            )

        stack: list[tuple[int, int]] = []

        self.mark_visited(start_x, start_y)
        stack.append((start_x, start_y))

        while stack:
            x, y = stack[-1]
            neighbor = self.step(x, y)

            if neighbor is None:
                stack.pop()
            else:
                stack.append(neighbor)

    def generate_perfect(
        self,
        start_x: int = 0,
        start_y: int = 0,
    ) -> list[list[Cell]]:
        """Reset the maze and generate a connected grid without cycles.

        Raises:
            ValueError: If the starting coordinates are invalid.
        """
        self.get_cell(start_x, start_y)

        for row in self.grid:
            for cell in row:
                cell.north = True
                cell.east = True
                cell.south = True
                cell.west = True

        self.reset_visited()
        self.backtrack(start_x, start_y)
        self.validate_external_walls()
        self.validate_connectivity(start_x, start_y)

        return self.grid
