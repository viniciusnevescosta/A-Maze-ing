"""Coordinate configuration, maze generation and output writing."""

import sys
from collections.abc import Sequence

from mazegen.display.ascii import render_maze
from mazegen.display.interactive import run_menu
from mazegen.input.config.config import Config
from mazegen.input.config.config import build_config
from mazegen.input.config.parser import filter_valid_lines, parse_config_lines
from mazegen.input.config.reader import read_config_file
from mazegen.input.config.validator import (
    convert_config_coordinates,
    convert_config_dimensions,
    convert_config_perfect,
    convert_config_seed,
    validate_config_coordinates,
    validate_required_keys,
    validate_unknown_keys,
)
from mazegen.maze.generator import MazeGenerator
from mazegen.maze.pattern import can_fit_pattern
from mazegen.maze.solver import (
    path_to_directions,
    solve_bfs,
    validate_solution,
)
from mazegen.output.writer import write_maze

USAGE = "Usage: python3 a_maze_ing.py <config_file>"


def generate_output(
    maze: MazeGenerator, config: Config,
) -> list[tuple[int, int]]:
    """Generate the requested mode, validate its solution and write output."""
    maze.generate(config.perfect, config.entry, config.exit)
    if maze.pattern_omitted:
        if not can_fit_pattern(config.width, config.height):
            reason = "maze is too small for the 42 pattern"
        else:
            reason = "no safe position for the 42 pattern"
        print(f"Warning: {reason}; generating without it.", file=sys.stderr)
    path = solve_bfs(maze, config.entry, config.exit)
    validate_solution(maze, path, config.entry, config.exit)
    write_maze(
        maze, config.output_file, config.entry, config.exit,
        path_to_directions(path),
    )
    return path


def main(argv: Sequence[str] | None = None) -> int:
    """Read configuration, generate a maze and write its output file."""
    arguments = sys.argv[1:] if argv is None else argv

    if len(arguments) < 1:
        print(f"Missing config file argument.\n{USAGE}", file=sys.stderr)
        return 1

    if len(arguments) > 1:
        print(f"Too many arguments.\n{USAGE}", file=sys.stderr)
        return 1

    config_path = arguments[0]

    try:
        config_lines = read_config_file(config_path)
    except FileNotFoundError:
        print(
            f"Error: The file '{config_path}' was not found.",
            file=sys.stderr,
        )
        return 1
    except PermissionError:
        print(
            f"Error: Permission denied while reading "
            f"the file '{config_path}'.",
            file=sys.stderr,
        )
        return 1
    except (OSError, UnicodeError) as error:
        print(
            f"Unexpected error while reading the file: "
            f"'{config_path}': {error}",
            file=sys.stderr,
        )
        return 1

    try:
        filtered_lines = filter_valid_lines(config_lines)
        parsed_config = parse_config_lines(filtered_lines)
    except ValueError as error:
        print(f"Config error: {error}", file=sys.stderr)
        return 1

    try:
        validate_required_keys(parsed_config)
        validate_unknown_keys(parsed_config)
        typed_config = convert_config_dimensions(parsed_config)
        typed_config = convert_config_perfect(typed_config)
        typed_config = convert_config_coordinates(typed_config)
        validate_config_coordinates(typed_config)
        typed_config = convert_config_seed(typed_config)
        config = build_config(typed_config)
    except ValueError as error:
        print(f"Config error: {error}", file=sys.stderr)
        return 1

    try:
        maze = MazeGenerator(config.width, config.height, config.seed)
        path = generate_output(maze, config)
        if sys.stdin.isatty() and sys.stdout.isatty():
            run_menu(
                maze, config.entry, config.exit, path,
                lambda: generate_output(maze, config),
            )
        else:
            print(render_maze(
                maze, config.entry, config.exit, path, maze.reserved,
            ))
    except ValueError as error:
        print(f"Maze error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(
            f"Error writing output file '{config.output_file}': {error}",
            file=sys.stderr,
        )
        return 1
    except (MemoryError, OverflowError):
        print("Maze dimensions exceed available resources.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130

    return 0
