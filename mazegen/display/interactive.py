"""Run the required terminal menu without coupling generation to rendering."""

import sys
from collections.abc import Callable

from mazegen.display.ascii import WALL_COLORS, render_maze
from mazegen.maze.generator import MazeGenerator

Coordinate = tuple[int, int]


def run_menu(
    maze: MazeGenerator,
    entry: Coordinate,
    exit: Coordinate,
    path: list[Coordinate],
    regenerate: Callable[[], list[Coordinate]],
) -> None:
    """Offer regeneration, solution toggle, wall colors and clean exit."""
    show_path = True
    color = 0
    while True:
        print("\033[2J\033[H", end="")
        print(render_maze(
            maze, entry, exit, path, maze.reserved, show_path, color,
        ))
        print("E: entry | X: exit | .: solution | #: 42")
        print("[r] regenerate  [s] show/hide path  [c] wall color  [q] quit")
        try:
            command = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if command == "q":
            return
        if command == "s":
            show_path = not show_path
        elif command == "c":
            color = (color + 1) % len(WALL_COLORS)
        elif command == "r":
            try:
                path = regenerate()
            except (ValueError, OSError) as error:
                print(f"Regeneration error: {error}", file=sys.stderr)
                return
        elif command:
            print("Unknown command; use r, s, c or q.", file=sys.stderr)
