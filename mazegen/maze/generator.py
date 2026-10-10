"""Seeded perfect-maze generation using iterative recursive backtracking."""

from random import Random

from mazegen.maze.areas import has_open_area
from mazegen.maze.braiding import add_loops
from mazegen.maze.cell import Cell
from mazegen.maze.grid import Direction as Direction
from mazegen.maze.grid import MazeGrid
from mazegen.maze.pattern_application import choose_pattern_cells
from mazegen.maze.solver import solve_bfs
from mazegen.maze.topology import count_loops, count_real_dead_ends
from mazegen.maze.validation import validate_shared_walls

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
        self.reserved: set[tuple[int, int]] = set()
        self.pattern_omitted: bool = False

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
            coordinate = (neighbor_x, neighbor_y)

            if coordinate in self.reserved:
                continue

            if not self.is_visited(neighbor_x, neighbor_y):
                candidates.append(coordinate)

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

        if (start_x, start_y) in self.reserved:
            raise ValueError("Starting cell belongs to the 42 pattern")

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
        """Generate connected corridors while preserving reserved cells.

        Raises:
            ValueError: If the start or reservations are invalid, or corridors
                cannot be connected around the pattern.
        """
        self.get_cell(start_x, start_y)

        if (start_x, start_y) in self.reserved:
            raise ValueError("Starting cell belongs to the 42 pattern")

        for x, y in self.reserved:
            self.get_cell(x, y)

        for row in self.grid:
            for cell in row:
                cell.north = True
                cell.east = True
                cell.south = True
                cell.west = True

        self.reset_visited()
        self.backtrack(start_x, start_y)
        self.validate_external_walls()
        self.validate_connectivity(
            start_x,
            start_y,
            reserved=self.reserved,
        )

        return self.grid

    def generate_non_perfect(
        self, start_x: int = 0, start_y: int = 0,
    ) -> list[list[Cell]]:
        """Generate a playable board, retrying bounded seeded tree attempts."""
        if self.width < 2 or self.height < 2 or self.width * self.height < 6:
            raise ValueError(
                "Non-perfect mode needs at least a 2x3 or 3x2 grid"
            )
        for _ in range(30):
            self.generate_perfect(start_x, start_y)
            add_loops(self, self.reserved, self.random)
            if count_loops(self, self.reserved) >= 2:
                if count_real_dead_ends(self, self.reserved) <= 2:
                    self.validate_non_perfect(start_x, start_y)
                    return self.grid
        raise ValueError("Cannot build a playable board with these parameters")

    def validate_non_perfect(
        self, start_x: int = 0, start_y: int = 0,
    ) -> None:
        """Check playable connectivity, cycles, dead ends and key corridors."""
        self.validate_connectivity(start_x, start_y, self.reserved)
        self.validate_external_walls()
        validate_shared_walls(self)
        key_cells = self.get_key_cells()
        reachable = self.get_reachable_cells(start_x, start_y)
        if not key_cells <= reachable:
            raise ValueError("Corners and center must be reachable corridors")
        if count_loops(self, self.reserved) < 2:
            raise ValueError("Non-perfect mode requires at least two loops")
        if count_real_dead_ends(self, self.reserved) > 2:
            raise ValueError(
                "Non-perfect mode allows at most two real dead ends"
            )
        if has_open_area(self):
            raise ValueError("Maze contains a completely open 3x3 area")

    def get_key_cells(self) -> set[tuple[int, int]]:
        """Return the four corners and center (right/bottom for even sizes)."""
        return {
            (0, 0), (self.width - 1, 0), (0, self.height - 1),
            (self.width - 1, self.height - 1),
            (self.width // 2, self.height // 2),
        }

    def generate(
        self,
        perfect: bool = True,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] | None = None,
        include_pattern: bool = True,
    ) -> list[list[Cell]]:
        """Generate a validated maze with safe 42 placement and endpoints."""
        destination = exit
        if destination is None:
            destination = (self.width - 1, self.height - 1)
        self.get_cell(*entry)
        self.get_cell(*destination)
        if entry == destination:
            raise ValueError("ENTRY and EXIT must be different coordinates")
        protected = set() if perfect else self.get_key_cells()
        self.reserved = (
            choose_pattern_cells(self, entry, destination, protected)
            if include_pattern else set()
        )
        self.pattern_omitted = include_pattern and not self.reserved
        if perfect:
            self.generate_perfect(*entry)
        else:
            self.generate_non_perfect(*entry)
        validate_shared_walls(self)
        if has_open_area(self):
            raise ValueError("Maze contains a completely open 3x3 area")
        solve_bfs(self, entry, destination)
        return self.grid

    def solve(
        self, entry: tuple[int, int], exit: tuple[int, int],
    ) -> list[tuple[int, int]]:
        """Return a shortest solution without changing generation state."""
        return solve_bfs(self, entry, exit)
